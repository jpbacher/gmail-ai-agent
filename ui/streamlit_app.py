import sys
import os

# --- Third-Party Libraries ---
import streamlit as st

# --- Fix import path (before custom modules) ---
current_file_path = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(current_file_path, "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Local modules ---
from pipeline.pipeline import get_emails_for_ui
from gmail.send import send_gmail_reply

st.set_page_config(page_title="Gmail AI Agent", layout="wide")

st.title("📬 Gmail AI Agent")
st.markdown("Review and approve GPT-generated email responses.")

emails, service = get_emails_for_ui()

if not emails:
    st.info("✅ No new actionable emails found right now.")
else:
    for email in emails:
        with st.expander(f"📨 {email['subject']} — {email['sender']}"):
            st.markdown("**📨 Email Body:**")
            st.write(email["body"])

            # Show suggested response
            st.markdown("**💡 Suggested Response:**")
            suggested_response = st.text_area(
                label="Edit response (optional)",
                value=email["suggested_response"],
                height=100,
                key=f"edit_{email['subject']}"
            )

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("✅ Approve", key=f"approve_{email['subject']}"):
                    try:
                        response = send_gmail_reply(
                            service=service,
                            message_id=email["message_id"],
                            thread_id=email["thread_id"],
                            to_email=email["to_email"],
                            subject=email["subject"],
                            reply_body=suggested_response,
                        )
                        st.success("✅ Email sent successfully!")
                        st.code(
                            f"Message ID: {response.get('id')}", 
                            language="text"
                        )
                    except Exception as e:
                        st.error(f"❌ Failed to send email: {e}")

            with col2:
                if st.button("📝 Edit Only", key=f"editbtn_{email['subject']}"):
                    st.info("✏️ Edited but not submitted yet.")

            with col3:
                if st.button("❌ Skip", key=f"skip_{email['subject']}"):
                    st.warning("Skipped ❌")
