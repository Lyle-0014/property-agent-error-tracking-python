import traceback

import infrai


def needs_human_review(request, tenant_document_ids, inspection_due):
    """Return the checkout-style handoff decision for one maintenance request."""
    urgent = request["priority"] == "urgent"
    missing_document = request["property_id"] not in tenant_document_ids
    return urgent or missing_document or inspection_due


def process_maintenance_request(request, tenant_document_ids, inspection_due):
    try:
        review = needs_human_review(request, tenant_document_ids, inspection_due)
        return {"request_id": request["request_id"], "needs_human_review": review}
    except Exception as exc:
        infrai.errors.capture(
            title="property agent request failed",
            message=str(exc),
            level="error",
            exception=traceback.format_exc(),
        )
        raise


if __name__ == "__main__":
    maintenance_request = {
        "request_id": "maint-1042",
        "property_id": "unit-7b",
        "priority": "normal",
        "summary": "Kitchen sink is leaking",
    }
    result = process_maintenance_request(
        maintenance_request,
        tenant_document_ids={"unit-7b"},
        inspection_due=False,
    )
    print(result)
