from .models import PaymentEvent, RecoveryDecision

def diagnose(event: PaymentEvent) -> RecoveryDecision:
    reason = (event.failure_reason or "unknown").lower()
    if event.status == "captured":
        return RecoveryDecision(payment_id=event.payment_id, diagnosis="already_captured", action="stop", confidence=1.0, reason="Payment is already captured.", policy_allowed=True)
    if not event.consent:
        return RecoveryDecision(payment_id=event.payment_id, diagnosis="no_outreach_consent", action="manual_review", confidence=1.0, reason="Customer outreach is not permitted.", policy_allowed=True)
    if event.attempt_number > 2:
        return RecoveryDecision(payment_id=event.payment_id, diagnosis="retry_limit_reached", action="manual_review", confidence=1.0, reason="Automatic retry limit has been reached.", policy_allowed=True)
    if "expired" in reason or ("card" in reason and "incorrect" in reason):
        return RecoveryDecision(payment_id=event.payment_id, diagnosis="payment_method_issue", action="update_payment_method", confidence=.92, reason="The payment method likely needs customer action.", policy_allowed=True)
    if "insufficient" in reason:
        return RecoveryDecision(payment_id=event.payment_id, diagnosis="insufficient_funds", action="reminder", delay_hours=12, confidence=.89, reason="A delayed reminder is safer than an immediate retry.", policy_allowed=True)
    if any(word in reason for word in ["timeout", "technical", "network"]):
        return RecoveryDecision(payment_id=event.payment_id, diagnosis="temporary_failure", action="retry", delay_hours=6, confidence=.91, reason="The failure appears temporary.", policy_allowed=True)
    return RecoveryDecision(payment_id=event.payment_id, diagnosis="unknown_failure", action="manual_review", confidence=.55, reason="The cause is ambiguous; human review is safer.", policy_allowed=True)