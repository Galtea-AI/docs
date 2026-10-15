# @start verify_galtea_signature
import hashlib
import hmac
import time


def verify_galtea_signature(raw_body: bytes, header: str | None, secret: str, tolerance_seconds: int = 300) -> bool:
    if not header:
        return False
    try:
        parts = dict(part.split("=", 1) for part in header.split(","))
        timestamp = int(parts["t"])
        if abs(time.time() - timestamp) > tolerance_seconds:
            return False

        signed = f"{timestamp}.".encode() + raw_body
        expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected.encode(), parts.get("v1", "").encode())
    except (KeyError, ValueError, OverflowError):
        return False


# @end verify_galtea_signature


def sign(raw_body: bytes, secret: str, timestamp: int) -> str:
    digest = hmac.new(secret.encode(), f"{timestamp}.".encode() + raw_body, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


test_secret = "whsec_test"
test_body = b'{"id":"7c1f0c3e.opened","event":"monitor_alert.opened"}'
now = int(time.time())

assert verify_galtea_signature(test_body, sign(test_body, test_secret, now), test_secret)
assert not verify_galtea_signature(test_body + b" ", sign(test_body, test_secret, now), test_secret)
assert not verify_galtea_signature(test_body, sign(test_body, "whsec_other", now), test_secret)
assert not verify_galtea_signature(test_body, sign(test_body, test_secret, now - 301), test_secret)
assert not verify_galtea_signature(test_body, "v1=abc", test_secret)
assert not verify_galtea_signature(test_body, "garbage", test_secret)
assert not verify_galtea_signature(test_body, None, test_secret)
assert not verify_galtea_signature(test_body, "", test_secret)
assert not verify_galtea_signature(test_body, "t=abc,v1=00", test_secret)
assert not verify_galtea_signature(test_body, f"t={'9' * 400},v1=00", test_secret)
assert not verify_galtea_signature(test_body, f"t={now},v1=\udcff", test_secret)
assert not verify_galtea_signature(test_body, f"t={now},v1=zz", test_secret)

# A header the API's own signing code sent for this secret, timestamp and body.
# api/tests/src/modules/monitor/infrastructure/http/monitorAlertWebhookClient.spec.ts asserts the same vector.
from unittest import mock

vector_secret = "whsec_galtea_test_vector"
vector_timestamp = 1767225600
vector_header = "t=1767225600,v1=99129d0572470e49b897afed06382364950e660aad16a6136376537dd97334d1"
with mock.patch("time.time", return_value=vector_timestamp):
    assert verify_galtea_signature(test_body, vector_header, vector_secret)
    assert not verify_galtea_signature(test_body + b" ", vector_header, vector_secret)
