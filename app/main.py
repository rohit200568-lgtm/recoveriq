from datetime import datetime
from fastapi import FastAPI, HTTPException
from .engine import diagnose
from .models import PaymentEvent

app = FastAPI(title="RecoverIQ", version="0.1.0")
payments = {}
actions = []

@app.get("/")
def root():
    return {"name": "RecoverIQ", "status": "running", "docs": "/docs"}

@app.post("/payments", status_code=201)
def ingest_payment(event: PaymentEvent):
    if event.payment_id in payments:
        return {"status": "duplicate", "payment": payments[event.payment_id]}
    payments[event.payment_id] = event.model_dump(mode="json")
    decision = diagnose(event)
    action = {"action_id": f"act_{len(actions)+1:04d}", "created_at": datetime.utcnow().isoformat(), "status": "proposed", **decision.model_dump()}
    actions.append(action)
    return {"payment": payments[event.payment_id], "decision": decision, "action": action}

@app.post("/payments/{payment_id}/capture")
def capture_payment(payment_id: str):
    if payment_id not in payments:
        raise HTTPException(404, "Payment not found")
    payments[payment_id]["status"] = "captured"
    for action in actions:
        if action["payment_id"] == payment_id and action["status"] in ["proposed", "approved"]:
            action["status"] = "cancelled"
    return {"payment_id": payment_id, "status": "captured", "message": "Recovery workflow stopped."}

@app.post("/actions/{action_id}/approve")
def approve_action(action_id: str):
    for action in actions:
        if action["action_id"] == action_id:
            if action["status"] != "proposed":
                raise HTTPException(400, "Action is not awaiting approval")
            action["status"] = "approved"
            return action
    raise HTTPException(404, "Action not found")

@app.post("/actions/{action_id}/execute")
def execute_action(action_id: str):
    for action in actions:
        if action["action_id"] == action_id:
            if action["status"] not in ["proposed", "approved"]:
                raise HTTPException(400, "Action cannot be executed")
            action["status"] = "awaiting_human_review" if action["action"] == "manual_review" else "executed"
            return action
    raise HTTPException(404, "Action not found")

@app.get("/payments/at-risk")
def at_risk():
    return [p for p in payments.values() if p["status"] in ["failed", "pending", "manual_review", "halted"]]

@app.get("/actions")
def get_actions():
    return actions

@app.get("/analytics")
def analytics():
    total = len(payments)
    captured = sum(p["status"] == "captured" for p in payments.values())
    at_risk = sum(p["amount"] for p in payments.values() if p["status"] != "captured")
    recovered = sum(p["amount"] for p in payments.values() if p["status"] == "captured")
    return {"total_payments": total, "captured_payments": captured, "recovery_rate": round(captured/total, 3) if total else 0, "amount_at_risk_paise": at_risk, "recovered_amount_paise": recovered, "total_actions": len(actions)}