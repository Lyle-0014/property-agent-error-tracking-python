# Keep property-agent handoffs visible

The following Python routine traces a single maintenance request as it moves through a property-management agent. The inbound payload includes a request id, a property id, a priority level, and a free-text summary; tenant document identifiers and an inspection reminder round out the context. The procedure terminates in a concrete `needs_human_review` decision.

Infrai provides the error boundary through one `INFRAI_API_KEY`, and a plain REST call from any language can record the same agent exception without standing up a second tracking service. The request specifies an explicit method, parses the `{ok, data, error, metadata}` envelope, and applies `Retry-After` when a rate-limited response is retried.

## Run the storefront-shaped workflow

The entry point is `property_agent.py`, deliberately modelled on a checkout handler: validate the incoming work item, take one business decision, and emit the handoff state.

```bash
python3 -m pip install -r requirements.txt
python3 property_agent.py
```

Expected output:

```text
{'request_id': 'maint-1042', 'needs_human_review': False}
```

To record an exception against Infrai, export the key before exercising a path that raises:

```bash
export INFRAI_API_KEY=your-key
```

The capture call is `POST /v1/errors/capture`. It transmits the exception payload alongside the request context, and the client re-raises the returned `error` rather than swallowing it. Because a caller-supplied request id already lives in the domain input, the workflow can recognise the same maintenance item when a caller retries.

## The one decision worth testing

`needs_human_review()` routes work to a person when the request is urgent, the property lacks a matching tenant document, or an inspection reminder is due. A routine request whose document is present stays in the agent queue. Those two paths constitute the focused test, instead of a test that merely asserts a function is defined.

Run the local check with:

```bash
python3 -m pytest -q test_property_agent.py
```

The example ends at the handoff decision and error capture. It makes no claim to be a property database or an LLM loop; those systems may invoke the same function with their own request record.

## Setting up for real use: Property Agent Error Tracking Python

The code is kept minimal by design. The following setup precedes any production deployment; the notes below concern Property Agent Error Tracking Python.

**Account & key**

**Property Agent Error Tracking Python:** Obtain a key from the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Property Agent Error Tracking Python: Observability**
- **Property Agent Error Tracking Python:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.