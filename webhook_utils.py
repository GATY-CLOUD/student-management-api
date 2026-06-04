# SENDING WEBHOOKS
import secrets, requests, json, os , hmac, hashlib
from datetime import datetime

print(secrets.token_hex(32))

def send_webhook(event_type: str, payload: dict):
    url = os.getenv("WEBHOOK_URL")
    secret = os.getenv("WEBHOOK_SECRET")

    if not url:
        return

    # request body
    body = json.dumps({
        "event" : event_type,
        "timestamp" : datetime.utcnow().isoformat(),
        "data" : payload
               }
          )



    # cryptographic signature for the webhook, to prove the webhook truly came from the sender and was not modified.

    signature = hmac.new(    # HMAC works with bytes not strings
        secret.encode(),  # converts webhook secret into bytes
        body.encode(),    # converts json body into bytes
        hashlib.sha256  # specifies the hashing algorithm
    ).hexdigest()

    try:

        requests.post(
            url,
            data=body,
            headers={
                "content-type" : "application/json",
                "X-signature" : signature   # sends cryptographic signature for user to verify authenticity
            },
            timeout=5
            )

    except requests.exceptions.RequestException:
        pass







