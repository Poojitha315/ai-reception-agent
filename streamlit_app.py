import os
import tempfile
import json
import streamlit as st
from datetime import datetime

# Import the functions from agent module
from agent import transcribe_audio, analyze_call
from database import (
    init_db,
    get_db,
    save_call,
    get_all_calls,
    get_call_by_id,
    mask_phone,
)
from models import Call

# Page configuration
st.set_page_config(
    page_title="AI Reception Agent",
    page_icon="📞",
    layout="wide"
)

# Initialize database
init_db()

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        margin: 5px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)


def login():
    """Handle user login."""
    # Already authenticated
    if st.session_state.get("authenticated", False):
        return True

    admin_password = os.getenv("APP_ADMIN_PASSWORD", "admin123")

    st.title("🔒 AI Reception Agent Login")

    with st.form("login_form"):
        password = st.text_input("Enter admin password:", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if password == admin_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")

    if not admin_password or admin_password == "admin123":
        st.warning(
            "⚠️ Warning: Using default password. "
            "Set APP_ADMIN_PASSWORD environment variable for production use."
        )

    st.stop()


def process_new_call():
    """Process a new call recording."""
    st.header("📞 New Call")

    uploaded_file = st.file_uploader(
        "Upload Call Recording",
        type=["mp3", "wav", "m4a", "ogg"],
        help="Upload a call recording file",
    )

    if uploaded_file is not None:
        # Audio player
        st.audio(uploaded_file, format=uploaded_file.type.split("/")[-1])

        if st.button("Analyze Call", type="primary"):
            with st.spinner("Analyzing call..."):
                try:
                    # Transcription
                    transcript = transcribe_audio(uploaded_file)
                    st.session_state.transcript = transcript

                    # Analysis
                    with st.spinner("Analyzing transcript..."):
                        analysis = analyze_call(transcript)
                        st.session_state.analysis = analysis

                    st.success("Call analysis complete!")

                except Exception as e:
                    st.error(f"Error analyzing call: {e}")
                    st.stop()

        # Show transcript
        if "transcript" in st.session_state:
            st.subheader("Transcript")
            st.text_area(
                "",
                st.session_state.transcript,
                height=200,
                label_visibility="collapsed",
                key="transcript_area",
            )

        # Show analysis + save form
        if "analysis" in st.session_state:
            analysis = st.session_state.analysis

            st.subheader("Analysis Results")

            with st.form("call_details"):
                col1, col2 = st.columns(2)

                with col1:
                    caller_name = st.text_input(
                        "Caller Name", value=analysis.get("caller_name", "")
                    )
                    phone = st.text_input(
                        "Phone", value=analysis.get("phone", "")
                    )
                    department = st.text_input(
                        "Department", value=analysis.get("department", "")
                    )

                with col2:
                    priority = st.selectbox(
                        "Priority",
                        ["Low", "Medium", "High"],
                        index=["Low", "Medium", "High"].index(
                            analysis.get("priority", "Medium").capitalize()
                        ),
                    )

                    summary = st.text_area(
                        "Summary",
                        value=analysis.get("summary", ""),
                        height=100,
                    )

                    response = st.text_area(
                        "AI Response",
                        value=analysis.get("response", ""),
                        height=100,
                    )

                submitted = st.form_submit_button("Save Call")

                if submitted:
                    if not summary:
                        st.error("Please enter a summary")
                    else:
                        db = next(get_db())
                        try:
                            call = save_call(
                                db=db,
                                transcript=st.session_state.transcript,
                                summary=summary,
                                caller_name=caller_name or None,
                                phone=phone or None,
                                department=department or None,
                                priority=priority,
                                response=response or None,
                            )
                            db.commit()

                            # Clear session state
                            st.session_state.pop("analysis", None)
                            st.session_state.pop("transcript", None)

                            st.success("Call saved successfully!")
                            st.balloons()
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error saving call: {e}")
                        finally:
                            db.close()


def view_call_logs():
    """Display call logs in a table (no nested expanders)."""
    st.header("📋 Call Logs")

    search_term = st.text_input(
        "Search calls",
        "",
        placeholder="Search by caller name, department, or summary",
    )

    db = next(get_db())
    calls = get_all_calls(db)

    if search_term:
        search_term_lower = search_term.lower()
        calls = [
            call
            for call in calls
            if (call.caller_name and search_term_lower in call.caller_name.lower())
            or (call.department and search_term_lower in call.department.lower())
            or (call.summary and search_term_lower in call.summary.lower())
            or (call.transcript and search_term_lower in call.transcript.lower())
        ]

    if not calls:
        st.info("ℹ️ No calls found in the database.")
        return

    # One expander per call – no nested expanders anywhere
    for call in calls:
        header = (
            f"📞 {call.caller_name or 'Unknown Caller'} - "
            f"{call.timestamp.strftime('%Y-%m-%d %H:%M')} "
            f"({call.priority or 'Medium'})"
        )

        with st.expander(header, expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Caller Name:** {call.caller_name or 'N/A'}")
                st.markdown(
                    f"**Phone:** {mask_phone(call.phone) if call.phone else 'N/A'}"
                )
                st.markdown(f"**Department:** {call.department or 'N/A'}")

            with col2:
                priority_color = {
                    "High": "red",
                    "Medium": "orange",
                    "Low": "green",
                }.get((call.priority or "Medium"), "black")

                st.markdown(
                    f"**Priority:** :{priority_color.lower()}[{call.priority or 'Medium'}]"
                )
                st.markdown(
                    f"**Date/Time:** {call.timestamp.strftime('%Y-%m-%d %H:%M')}"
                )

            st.markdown("---")

            st.markdown("**Summary:**")
            st.write(call.summary or "No summary available.")

            st.markdown("---")

            st.markdown("**Full Transcript:**")
            st.text_area(
                "Transcript",
                call.transcript,
                height=200,
                label_visibility="collapsed",
                key=f"transcript_{call.id}",
                disabled=True,
            )

            if call.response:
                st.markdown("---")
                st.markdown("**AI Response:**")
                st.info(call.response)


def main():
    """Main application function."""
    if not login():
        return

    # Sidebar
    st.sidebar.title("AI Reception Agent")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.sidebar.markdown(
        """
    ### Welcome to AI Reception Agent
    
    This tool helps you manage call recordings and extract key information using AI.
    
    **Quick Start:**
    1. Go to "New Call" tab
    2. Upload a call recording
    3. Review and edit the extracted information
    4. Save the call to the database
    5. View all calls in the "Call Logs" tab
    """
    )

    tab1, tab2 = st.tabs(["📞 New Call", "📋 Call Logs"])

    with tab1:
        process_new_call()

    with tab2:
        view_call_logs()


if __name__ == "__main__":
    main()
