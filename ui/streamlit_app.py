# -- Standard Libraries ---
import sys
import os
from datetime import datetime
import json

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
    save_summary_to_s3
)
from agent.summarizer import should_upload_summary


st.set_page_config(page_title="Gmail AI Agent", layout="wide")

st.title("📬 Gmail AI Agent")
st.markdown("Review and approve GPT-generated email responses.")

reply_emails, summary_emails, service = get_emails_for_ui()

if not reply_emails and not summary_emails:
    st.info("✅ No new actionable emails found right now.")
if reply_emails:
    st.subheader("📬 Emails that may need a response")
    for email in reply_emails:
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

if summary_emails:
    st.subheader("📜 Informational emails (summarized)")
    for email in summary_emails:
        with st.expander(f"📨 {email['subject']} — {email['sender']}"):
            st.markdown("**📨 Email Body:**")
            st.write(email["body"])

            # Show summary
            st.markdown("**📝 Agent Summary:**")
            st.write(email["summary"])

            # Download summary as JSON
            json_data = {
                "subject": email["subject"],
                "sender": email["sender"],
                "summary": email["summary"],
                "timestamp": datetime.utcnow().isoformat()
            }

            # option to download summary locally
            st.download_button(
                label="⬇️ Download Summary",
                data=json.dumps(json_data, indent=2),
                file_name=f"{email['subject'].replace(' ', '_')}_summary.json",
                mime="application/json",
                key=f"download_{email['subject']}"
            )

            if should_upload_summary(email["summary"]):
                s3_response = save_summary_to_s3(
                    subject=email["subject"],
                    sender=email["sender"],
                    summary_text=email["summary"]
                )
                    
                if s3_response.get("status") == "success":
                    st.toast("📝 Summary saved to S3", icon="🗂️")
                else:
                    st.warning("⚠️ Failed to save summary to S3.")
            else:
                st.info("ℹ️ This summary will not be uploaded "
                        "(e.g., job alert or internal notification).")
