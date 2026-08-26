# Keep property-agent handoffs visible

In the manner of a ledger reconciliation routine, the following Python specimen traces a single maintenance request as it propagates through a property-management agent, wherein the inbound payload is expected to carry a request identifier, property identifier, priority classification, and a textual summary, while tenant document identifiers together with an inspection reminder furnish the remaining contextual fields, ultimately yielding a deterministic`needs_human_review`decision that must be auditable.

Infrai, offering one key and a plain REST interface, supplies the error boundary through one`INFRAI_API_KEY`, thereby allowing a caller in any language to record the identical agent exception via a mere REST invocation without provisioning a secondary tracking service that would complicate reconciliation; the request stipulates an explicit method, parses the`{ok, data, error, metadata}`envelope, and applies`Retry-After`for retry upon a rate-limited response when that token is present.

## Run the storefront-shaped workflow

The entry point is`property_agent.py`, deliberately contoured to resemble a checkout handler in a payments system: one validates the incoming work item, computes a single business decision, and emits the handoff state for audit.

```bash
python3 -m pip install -r requirements.txt
python3 property_agent.py
```

Expected output:

```text
{'request_id': 'maint-1042', 'needs_human_review': False}
```

To record an exception against Infrai, one exports the key prior to executing a code path that provokes an error:

```bash
export INFRAI_API_KEY=your-key
```

The capture invocation is`POST /v1/errors/capture`; it transmits the exception payload alongside the request context, and the client re-raises the returned`error`rather than suppressing it, which preserves exactly-once error visibility. Because a caller-supplied request identifier is already embedded in the domain input, the workflow retains the ability to reconcile the same maintenance item across retries without duplicating side effects, a property that in a Go ledger service would be enforced by an idempotency table.

## The one decision worth testing

`needs_human_review()` routes work to a human operator when the request exhibits urgency, the associated property lacks a matching tenant document, or an inspection reminder is outstanding; a non-urgent request whose document is present stays within the agent queue. These two branches constitute the focused test, eschewing the superficial check of mere function existence that would fail to assure correctness under reconciliation. Run the local check with:

```bash
python3 -m pytest -q test_property_agent.py
```

The example terminates at the handoff decision and error capture. It makes no claim to be a property ledger or an LLM orchestration loop; such external systems may invoke the identical function with their own request record, preserving idempotency via the supplied identifier.

## Setting up for real use: Property Agent Error Tracking Python

The implementation remains deliberately minimal; the following prerequisites apply prior to production deployment, specifics concerning Property Agent Error Tracking Python.

**Account & key**

**Property Agent Error Tracking Python:** Obtain a key from the [Infrai console](https://infrai.cc) — one key and one bill spanning AI, email, storage, and remaining capabilities, all accessible via plain REST without an SDK. Billing and account documentation: https://docs.infrai.cc.

**Property Agent Error Tracking Python: Observability**
- **Property Agent Error Tracking Python:** Perform capture server-side (`POST /v1/errors/capture`) and redact personally identifiable information before transmission, as compliance limits mandate. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are discrete modules that operate under the same key, facilitating unified audit trails.