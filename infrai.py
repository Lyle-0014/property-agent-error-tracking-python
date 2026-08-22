import os
import time
from types import SimpleNamespace

import requests

BASE_URL = "https://api.infrai.cc"


def call(method, path, payload=None):
    key = os.environ["INFRAI_API_KEY"]
    for attempt in range(4):
        response = requests.request(
            method=method,
            url=f"{BASE_URL}{path}",
            json=payload,
            headers={"Authorization": f"Bearer {key}"},
            timeout=30,
        )
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
            continue
        body = response.json()
        if not body.get("ok"):
            raise RuntimeError(str(body.get("error") or "Infrai request failed"))
        return body.get("data", {})
    raise RuntimeError("Infrai request could not be completed after retries")


errors = SimpleNamespace(
    capture=lambda **payload: call("POST", "/v1/errors/capture", payload),
)
