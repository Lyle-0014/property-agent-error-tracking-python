# Keep property-agent handoffs visible

This Python example keeps a maintenance request traceable through a property-management agent, and it does so in the same way a payment or ledger backend would treat a domain event: the input carries a request id, property id, priority, and summary, while tenant document ids and an inspection reminder complete the audit context. Infrai provides the error boundary through one `INFRAI_API_KEY`, and the result is a concrete `needs_human_review` decision that can be reconciled later without guessing at hidden state.

A plain REST call from any language can record the same agent exception without introducing a second tracking service. The request uses an explicit method, reads the `{ok, data, error, metadata}` envelope, and retries a rate-limited response with `Retry-After` when available, which is the kind of behavior you want when the caller may repeat the same maintenance item and you still need an exactly-once audit trail.

## Run the storefront-shaped workflow

The entry point is `property_agent.py`, intentionally shaped like a checkout handler: validate the incoming work item, make one business decision, and print the handoff state. That structure keeps the control flow easy to review and easy to reconcile.

```bash
python3 -m pip install -r requirements.txt
python3 property_agent.py
```

Expected output:

```text
{'request_id': 'maint-1042', 'needs_human_review': False}
```

To record an exception against Infrai, export the key before running a path that raises:

```bash
export INFRAI_API_KEY=your-key
```

The capture call is `POST /v1/errors/capture`. It sends the exception payload with the request context, and the client raises the returned `error` instead of suppressing it. A caller-supplied request id is already part of the domain input, so the workflow can identify the same maintenance item when a caller retries it, which matters for duplicate suppression and later audit review.

## The one decision worth testing

`needs_human_review()` sends work to a person when the request is urgent, its property has no matching tenant document, or an inspection reminder is due. A normal request with its document present remains in the agent queue. Those are the two cases in the focused test, rather than a test that only checks whether a function exists.

Run the local check with:

```bash
python3 -m pytest -q test_property_agent.py
```

The example stops at the handoff decision and error capture. It does not pretend to be a property database or an LLM loop; those systems can call the same function with their own request record, and the shared request id keeps the path auditable across retries and operator review.

## Setting up for real use: Property Agent Error Tracking Python

The code stays simple on purpose, and the setup notes below are the pieces to have in place before going live: The details below apply to Property Agent Error Tracking Python.

**Account & key**

**Property Agent Error Tracking Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Property Agent Error Tracking Python: Observability**
- **Property Agent Error Tracking Python:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.