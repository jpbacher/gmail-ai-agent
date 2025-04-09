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
from aws.s3_storage import (
    save_response_to_s3,
    upload_log_file_to_s3,
)

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
                    st.success("Approved ✅")
                    s3_response = save_response_to_s3(
                        response_type="approved",
                        subject=email["subject"],
                        sender=email["sender"],
                        response_body=suggested_response
                    )
                if s3_response.get("ResponseMetadata", {}).get(
                    "HTTPStatusCode"
                ) == 200:
                    st.toast("✅ Response saved to S3!", icon="🗂️")
                    
                    # Trigger log file upload to S3
                    upload_result = upload_log_file_to_s3(
                        local_log_path="logs/app.log",
                        s3_log_folder="logs"
                    )
                    if upload_result and \
                       upload_result.get("status") == "success":
                        st.toast("📤 Log uploaded to S3!", icon="📁")
                    else:
                        st.warning("⚠️ Log upload failed or skipped.")
                else:
                    st.error("⚠️ Failed to save response to S3.")

            with col2:
                if st.button("📝 Edit Only", key=f"editbtn_{email['subject']}"):
                    st.info("✏️ Edited but not submitted yet.")
                    s3_response = save_response_to_s3(
                        response_type="edited",
                        subject=email["subject"],
                        sender=email["sender"],
                        response_body=suggested_response
                    )
                if s3_response.get("ResponseMetadata", {}).get(
                    "HTTPStatusCode"
                ) == 200:
                    st.toast("📝 Edited response saved to S3.", icon="📤")

                    upload_result = upload_log_file_to_s3(
                        local_log_path="logs/app.log",
                        s3_log_folder="logs"
                    )
                    if upload_result and \
                       upload_result.get("status") == "success":
                        st.toast("📤 Log uploaded to S3!", icon="📁")
                    else:
                        st.warning("⚠️ Log upload failed or skipped.")
                else:
                    st.error("⚠️ Failed to save edited response to S3.")

            with col3:
                if st.button("❌ Skip", key=f"skip_{email['subject']}"):
                    st.warning("Skipped ❌")
                    s3_response = save_response_to_s3(
                        response_type="skipped",
                        subject=email["subject"],
                        sender=email["sender"],
                        response_body=suggested_response
                    )
                if s3_response.get("ResponseMetadata", {}).get(
                    "HTTPStatusCode"
                ) == 200:
                    st.toast("⏭️ Skipped response saved to S3.", icon="📥")

                    upload_result = upload_log_file_to_s3(
                        local_log_path="logs/app.log",
                        s3_log_folder="logs"
                    )
                    if upload_result and \
                       upload_result.get("status") == "success":
                        st.toast("📤 Log uploaded to S3!", icon="📁")
                    else:
                        st.warning("⚠️ Log upload failed or skipped.")
                else:
                    st.error("⚠️ Failed to save skipped response to S3.")
