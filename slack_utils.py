import hashlib
import hmac
import time

def verify_slack_signature(signing_secret: str, timestamp: str, body: str, slack_signature: str) -> bool:
    """Verify Slack request signature.

    Args:
        signing_secret (str): Your Slack app's signing secret.
        timestamp (str): The 'X-Slack-Request-Timestamp' header from the request.
        body (str): The raw request body.
        slack_signature (str): The 'X-Slack-Signature' header from the request.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    current_timestamp = int(time.time())
    if abs(current_timestamp - int(timestamp)) > 60 * 5:
        # The request is older than 5 minutes
        return False
    
    # Create the basestring as per Slack's requirements
    basestring = f"v0:{timestamp}:{body}".encode('utf-8')

    # Create the HMAC SHA256 hash
    my_signature = 'v0=' + hmac.new(
        signing_secret.encode('utf-8'),
        basestring,
        hashlib.sha256
    ).hexdigest()

    # Compare the computed signature with the one from Slack
    return hmac.compare_digest(my_signature, slack_signature)


