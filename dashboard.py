import requests
import streamlit as st

API = "http://127.0.0.1:8000"
st.set_page_config(page_title="RecoverIQ", layout="wide")
st.title("RecoverIQ")
st.caption("Explainable failed-payment recovery")

try:
    analytics = requests.get(f"{API}/analytics", timeout=3).json()
    payments = requests.get(f"{API}/payments/at-risk", timeout=3).json()
    actions = requests.get(f"{API}/actions", timeout=3).json()
except requests.RequestException:
    st.error("Start the API first: uvicorn app.main:app --reload")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Payments", analytics["total_payments"])
c2.metric("Captured", analytics["captured_payments"])
c3.metric("Recovery rate", f'{analytics["recovery_rate"]*100:.1f}%')
c4.metric("Amount at risk", f'₹{analytics["amount_at_risk_paise"]/100:,.2f}')

st.subheader("At-risk payments")
st.dataframe(payments, use_container_width=True)
st.subheader("Recovery actions")
st.dataframe(actions, use_container_width=True)