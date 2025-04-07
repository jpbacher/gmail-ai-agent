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

        response_key = f"response_{email['subject']}"
        edit_mode_key = f"edit_mode_{email['subject']}"
        edited_text_key = f"edited_text_{email['subject']}"

        if edit_mode_key not in st.session_state:
            st.session_state[edit_mode_key] = False

        if not st.session_state[edit_mode_key]:
            st.text_area(
                "💡 Suggested Response",
                value="Hi there, thanks for reaching out...",
                height=100,
                key=response_key,
                disabled=True
            )
        else:
            st.text_area(
                "✏️ Edit Your Response",
                value=st.session_state[response_key],
                height=150,
                key=edited_text_key
            )

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            if st.button(f"✅ Approve", key=f"approve_{email['subject']}"):
                st.success("Response approved ✅")

        with col2:
            if st.button(f"✏️ Edit", key=f"edit_{email['subject']}"):
                st.session_state[edit_mode_key] = True

        with col3:
            if st.session_state[edit_mode_key]:
                if st.button(f"💾 Submit Edited", key=f"submit_edit_{email['subject']}"):
                    final_response = st.session_state[edited_text_key]
                    st.success("Edited response submitted ✅")
                    st.markdown("### ✅ Final Response:")
                    st.code(final_response)
        with col4:
            if st.button(f"❌ Skip", key=f"skip_{email['subject']}"):
                st.warning("Skipped ❌")
