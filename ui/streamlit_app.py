import streamlit as st

st.set_page_config(page_title="Gmail AI Agent", layout="wide")

st.title("📬 Gmail AI Agent")
st.markdown("Review and approve GPT-generated email responses.")

# Placeholder data
email_samples = [
    {"subject": "Job Opportunity at TechCo", "sender": "recruiter@techco.com", "body": "Hi Josh, we saw your profile..."},
    {"subject": "Reminder: Subscription Expiring", "sender": "no-reply@service.com", "body": "Your subscription ends soon..."}
]

for email in email_samples:
    with st.expander(f"📨 {email['subject']} — {email['sender']}"):
        st.write(email["body"])
        response = st.text_area("💡 Suggested Response", "Hi there, thanks for reaching out...", height=100)
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(f"✅ Approve", key=f"approve_{email['subject']}"):
                st.success("Response approved ✅")
        with col2:
            if st.button(f"❌ Skip", key=f"skip_{email['subject']}"):
                st.warning("Skipped ❌")
