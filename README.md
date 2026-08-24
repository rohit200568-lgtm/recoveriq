# RecoverIQ

> An explainable AI agent for recovering failed payments safely and efficiently.

RecoverIQ is a payment-recovery assistant designed for merchants that lose revenue because of failed subscriptions, temporary bank errors, insufficient funds, expired cards, and unclear payment failures.

Instead of retrying every failed payment blindly, RecoverIQ diagnoses the likely failure reason, selects a bounded recovery action, tracks the action, and stops the workflow when the payment succeeds.

## Problem

Failed payments create revenue loss for merchants, but different failures require different responses.

For example:

- A temporary bank timeout may be retried later.
- An insufficient-funds failure may require a reminder.
- An expired card requires the customer to update the payment method.
- Repeated failures should be escalated to a human.
- A successful payment should immediately cancel pending reminders and retries.

A generic retry system can waste money, annoy customers, and create unnecessary operational work.

## Solution

RecoverIQ follows this workflow:

```text
Detect → Diagnose → Decide → Execute → Verify → Stop
```

The system:

1. Receives a failed payment event.
2. Classifies the likely failure reason.
3. Calculates a safe recovery decision.
4. Applies retry limits and consent rules.
5. Creates a recovery action.
6. Tracks the action status.
7. Stops pending recovery actions after successful payment.
8. Displays recovery metrics through a dashboard.

## Features

- Failed-payment diagnosis.
- Temporary-failure detection.
- Insufficient-funds handling.
- Expired-card handling.
- Retry-limit enforcement.
- Customer-consent validation.
- Manual-review escalation.
- Recovery action tracking.
- Payment capture simulation.
- Recovery analytics.
- FastAPI backend.
- Streamlit dashboard.
- Interactive API documentation.
- Synthetic data and mock recovery actions.
- Audit-friendly decision explanations.

## Recovery actions

RecoverIQ currently supports these actions:

| Failure type | Recovery action |
|---|---|
| Bank timeout | Retry after a delay |
| Technical or network failure | Retry after a delay |
| Insufficient funds | Send a delayed reminder |
| Expired card | Ask the customer to update the payment method |
| Too many attempts | Escalate for manual review |
| Unknown failure | Escalate for manual review |
| Already captured | Stop the recovery workflow |

## Architecture

```text
Payment event
     ↓
FastAPI ingestion API
     ↓
Payment state store
     ↓
Failure diagnosis engine
     ↓
Policy and safety checks
     ↓
Recovery action
     ↓
Analytics dashboard
```

## Technology stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- Streamlit
- Requests
- GitHub Codespaces
- Razorpay test-mode integration planned

## Project structure

```text
recoveriq/
├── README.md
├── requirements.txt
├── requirements-dashboard.txt
├── .gitignore
├── dashboard.py
└── app/
    ├── __init__.py
    ├── main.py
    ├── models.py
    └── engine.py
```

## Requirements

- Python 3.10 or newer.
- Git.
- GitHub Codespaces or a local terminal.
- Internet connection for installing dependencies.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/recoveriq.git
cd recoveriq
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux or GitHub Codespaces:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate it on Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Install backend dependencies:

```bash
python -m pip install -r requirements.txt
```

Install dashboard dependencies:

```bash
python -m pip install -r requirements-dashboard.txt
```

## Run the backend

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

For GitHub Codespaces, use:

```bash
uvicorn app.main:app --reload --host 0.0.0.0
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Run the dashboard

Open a second terminal and activate the environment:

```bash
source .venv/bin/activate
```

Start Streamlit:

```bash
python -m streamlit run dashboard.py
```

For GitHub Codespaces:

```bash
python -m streamlit run dashboard.py --server.address 0.0.0.0
```

The dashboard will usually run on port `8501`.

## Test the API

### Create a failed payment

```bash
curl -X POST http://127.0.0.1:8000/payments \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "pay_001",
    "customer_id": "cus_001",
    "amount": 99900,
    "failure_reason": "bank_timeout",
    "attempt_number": 1,
    "customer_language": "en",
    "consent": true
  }'
```

Expected decision:

```json
{
  "action": "retry",
  "delay_hours": 6,
  "diagnosis": "temporary_failure"
}
```

### Test insufficient funds

```bash
curl -X POST http://127.0.0.1:8000/payments \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "pay_002",
    "customer_id": "cus_002",
    "amount": 149900,
    "failure_reason": "insufficient_funds",
    "attempt_number": 1,
    "customer_language": "ta",
    "consent": true
  }'
```

Expected decision:

```json
{
  "action": "reminder",
  "delay_hours": 12,
  "diagnosis": "insufficient_funds"
}
```

### Test an expired card

```bash
curl -X POST http://127.0.0.1:8000/payments \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "pay_003",
    "customer_id": "cus_003",
    "amount": 249900,
    "failure_reason": "expired_card",
    "attempt_number": 1,
    "customer_language": "en",
    "consent": true
  }'
```

Expected decision:

```json
{
  "action": "update_payment_method",
  "diagnosis": "payment_method_issue"
}
```

### Simulate successful recovery

```bash
curl -X POST \
  http://127.0.0.1:8000/payments/pay_001/capture
```

This marks the payment as captured and cancels pending recovery actions for that payment.

### View analytics

```bash
curl http://127.0.0.1:8000/analytics
```

### View at-risk payments

```bash
curl http://127.0.0.1:8000/payments/at-risk
```

### View recovery actions

```bash
curl http://127.0.0.1:8000/actions
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/payments` | Ingest a failed-payment event |
| `POST` | `/payments/{payment_id}/capture` | Simulate successful payment |
| `GET` | `/payments/at-risk` | View unresolved payments |
| `GET` | `/actions` | View recovery actions |
| `POST` | `/actions/{action_id}/approve` | Approve a proposed action |
| `POST` | `/actions/{action_id}/execute` | Execute a mock action |
| `GET` | `/analytics` | View recovery metrics |

## Safety design

RecoverIQ uses deterministic policy checks for sensitive actions.

The system:

- Limits automatic retries.
- Checks customer communication consent.
- Escalates ambiguous failures.
- Stops recovery after successful payment.
- Does not request card numbers.
- Does not request CVV, PIN, password, or OTP.
- Uses synthetic payments and mock actions.
- Does not perform real financial transactions.
- Separates AI recommendations from action execution.

The AI layer is intended for diagnosis, explanation, prioritisation, and message generation. Financial state transitions and action limits should remain deterministic.

## Planned Razorpay integration

The current project uses synthetic payment events. A future version can connect to Razorpay test mode through payment and subscription webhooks.

Planned events include:

- `payment.failed`
- `payment.captured`
- `subscription.pending`
- `subscription.charged`
- `subscription.halted`

Before using real webhook events, implement:

- Webhook signature verification.
- Persistent database storage.
- Idempotency handling.
- Duplicate-event protection.
- Asynchronous event processing.
- Secure environment variables.
- Test-mode credentials only.

## Evaluation metrics

RecoverIQ can be evaluated against a simple baseline:

```text
Baseline: retry every eligible failed payment once after 24 hours.
```

Recommended metrics:

| Metric | Description |
|---|---|
| Recovery rate | Recovered payments divided by eligible failed payments |
| Revenue recovery rate | Recovered amount divided by amount at risk |
| Diagnosis accuracy | Correct failure classifications |
| Action accuracy | Appropriate decisions divided by evaluated decisions |
| Unnecessary retry rate | Unsafe or low-value retries |
| Contact efficiency | Recovered payments per customer contact |
| Average recovery time | Time from failure to successful payment |
| Manual-review rate | Percentage of cases escalated |
| Net recovered value | Recovered amount minus discounts and outreach costs |

## Example workflow

```text
1. Payment fails because of a bank timeout.
2. RecoverIQ identifies it as a temporary failure.
3. The policy engine checks that the retry limit has not been reached.
4. The agent proposes a retry after six hours.
5. A mock recovery action is created.
6. The payment succeeds.
7. RecoverIQ marks the payment as captured.
8. Pending recovery actions are cancelled.
9. Analytics update the recovered amount.
```

## Limitations

This is a prototype and currently:

- Stores data in memory.
- Uses synthetic events.
- Does not connect to a live payment account.
- Uses rule-based diagnosis.
- Uses mock notifications.
- Does not include a production database.
- Does not include an actual payment retry scheduler.
- Does not send real customer messages.

## Roadmap

- Add PostgreSQL persistence.
- Add Razorpay test-mode webhooks.
- Add webhook signature validation.
- Add Redis and background task processing.
- Add retry scheduling.
- Add multilingual message generation.
- Add LLM-powered explanations.
- Add customer communication templates.
- Add baseline-versus-agent evaluation.
- Add authentication and role-based access.
- Add Docker deployment.
- Add automated tests.
- Add a production-ready audit log.

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/your-feature
```

3. Make your changes.
4. Run the project locally.
5. Commit your changes.

```bash
git add .
git commit -m "Add your feature"
```

6. Push the branch.

```bash
git push origin feature/your-feature
```

7. Open a pull request.

## License

This project is available under the MIT License.

## Disclaimer

RecoverIQ is an educational prototype for a buildathon. It is not a payment processor, financial adviser, fraud-detection guarantee, or production payment-recovery system.
