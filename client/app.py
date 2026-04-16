import streamlit as st
import requests
import json
from requests.auth import HTTPBasicAuth
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
API_URL=os.getenv("API_URL")

# set page configuration
st.set_page_config(
    page_title="MedSaathi | GenAI Medical Diagnosis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Global CSS
st.markdown("""
<style>
/* Improve overall readability (text + controls size) */
.stApp {
    font-size: 18px;
}
html, body {
    font-size: 18px;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

/* Inputs / text areas */
input, textarea, select {
    font-size: 16px !important;
}

/* Buttons */
.stButton > button {
    font-size: 16px;
    padding: 0.65rem 1.2rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    font-size: 16px;
}

</style>
""", unsafe_allow_html=True)

# initial state management 
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "auth" not in st.session_state:
    st.session_state.auth = None

# API Functions :

def signup_user(username, password, role):
    try:
        response = requests.post(f"{API_URL}/auth/signup", json={"username": username, "password": password, "role": role})
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}
    
def authenticate_user(username, password):
    try:
        response = requests.get(f"{API_URL}/auth/login", auth=HTTPBasicAuth(username, password))
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}
    
def upload_report(auth, files, ct_scan=None, xray=None):
    try:
        headers = {'accept': 'application/json'}
        files_data = []
        for file in files or []:
            files_data.append(('files', (file.name, file.getvalue(), file.type)))
        if ct_scan is not None:
            files_data.append(('ct_scan', (ct_scan.name, ct_scan.getvalue(), ct_scan.type)))
        if xray is not None:
            files_data.append(('xray', (xray.name, xray.getvalue(), xray.type)))
        response = requests.post(
            f"{API_URL}/reports/upload",
            auth=auth,
            files=files_data,
            headers=headers,
            timeout=120,
        )
        try:
            return response.status_code, response.json()
        except ValueError:
            # Backend may return non-JSON (e.g., HTML error page). Surface it to the UI.
            return response.status_code, {"detail": response.text}
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}
    
def get_diagnosis(auth, doc_id, question):
    try:
        data = {'doc_id': doc_id, 'question': question}
        response = requests.post(
            f"{API_URL}/diagnosis/from_report",
            auth=auth,
            data=data,
            headers={'accept': 'application/json'},
            timeout=120,
        )
        try:
            return response.status_code, response.json()
        except ValueError:
            # Backend may return non-JSON (e.g., empty response / HTML). Surface it to the UI.
            return response.status_code, {"detail": response.text}
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}
    
def get_doctor_diagnosis(auth, patient_name):
    try:
        response = requests.get(f"{API_URL}/diagnosis/by_patient_name", auth=auth, params={'patient_name': patient_name})
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}
    
# Sidebar and Authentication Flow 
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=60)
    st.title("MedSaathi")
    st.markdown("Your AI Medical Companion")
    st.divider()

if st.session_state.logged_in:
    with st.sidebar:
        st.success(f"👋 Welcome, **{st.session_state.username}**!")
        st.caption(f"Role: **{st.session_state.role.capitalize()}**")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.session_state.auth = None
            st.rerun()
else:
    with st.sidebar:
        login_tab, signup_tab = st.tabs(["🔒 Login", "📝 Sign Up"])
        
        with login_tab:
            st.header("Welcome Back")
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", use_container_width=True, type="primary"):
                if login_username and login_password:
                    with st.spinner("Authenticating..."):
                        status_code, data = authenticate_user(login_username, login_password)
                        if status_code == 200:
                            st.session_state.logged_in = True
                            st.session_state.username = login_username
                            st.session_state.role = data["role"]
                            st.session_state.auth = HTTPBasicAuth(login_username, login_password)
                            st.rerun()
                        else:
                            st.error(f"Login failed: {data.get('detail', 'Unknown error')}")
                else:
                    st.warning("Please enter a username and password.")

        with signup_tab:
            st.header("Create Account")
            signup_username = st.text_input("New Username", key="signup_username")
            signup_password = st.text_input("New Password", type="password", key="signup_password")
            signup_role = st.selectbox("Role", ["patient", "doctor"], key="signup_role")
            if st.button("Create Account", use_container_width=True, type="primary"):
                if signup_username and signup_password:
                    with st.spinner("Creating account..."):
                        status_code, data = signup_user(signup_username, signup_password, signup_role)
                        if status_code == 200:
                            st.success("User created successfully! You can now log in.")
                        elif status_code == 400:
                            st.error(f"Signup failed: {data.get('detail', 'User already exists')}")
                        else:
                            st.error(f"Signup failed: {data.get('detail', 'Unknown error')}")
                else:
                    st.warning("Please fill in all fields.")


# Main Page Application
st.title("🩺 Medical Report Diagnosis")
st.markdown("<p style='font-size: 1.1rem; color: #64748b;'>An intelligent GenAI application to analyze your lab reports, explain medical terms, and provide actionable insights for patients and doctors.</p>", unsafe_allow_html=True)
st.divider()

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info("👋 **Please log in or sign up via the sidebar to access the dashboard.**")
        st.image("https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", use_container_width=True, caption="Your AI Medical Assistant")
else:
    if st.session_state.role == "patient":
        st.header("🛡️ Patient Dashboard")
        
        tab_upload, tab_diag = st.tabs(["📄 Upload Reports", "💬 Ask & Diagnose"])
        
        with tab_upload:
            st.markdown("### Upload New Medical Reports")
            st.markdown("Upload PDFs/TXT files for report analysis, or add one CT scan and one X-ray image for Gemini vision diagnosis.")
            with st.form("upload_form", clear_on_submit=False):
                st.info("💡 **Tip:** You can upload multiple PDF/TXT reports plus up to one CT image and one X-ray image.")
                uploaded_files = st.file_uploader(
                    "Choose medical report files (e.g., PDF, TXT)",
                    type=["pdf", "txt"],
                    accept_multiple_files=True
                )
                image_col1, image_col2 = st.columns(2)
                with image_col1:
                    ct_scan_image = st.file_uploader(
                        "Optional CT Scan Image",
                        type=["png", "jpg", "jpeg"],
                        accept_multiple_files=False,
                    )
                with image_col2:
                    xray_image = st.file_uploader(
                        "Optional X-ray Image",
                        type=["png", "jpg", "jpeg"],
                        accept_multiple_files=False,
                    )

                preview_col1, preview_col2 = st.columns(2)
                with preview_col1:
                    if ct_scan_image is not None:
                        st.image(ct_scan_image, caption="CT scan preview", use_container_width=True)
                with preview_col2:
                    if xray_image is not None:
                        st.image(xray_image, caption="X-ray preview", use_container_width=True)

                upload_submitted = st.form_submit_button("🚀 Upload & Process Reports", type="primary")
                if upload_submitted and (uploaded_files or ct_scan_image or xray_image):
                    with st.spinner("Uploading and processing reports... This may take a few seconds."):
                        status_code, data = upload_report(
                            st.session_state.auth,
                            uploaded_files,
                            ct_scan=ct_scan_image,
                            xray=xray_image,
                        )
                        if status_code == 200:
                            st.success("✅ Reports uploaded and processed successfully!")
                            st.session_state.doc_id = data['doc_id']
                            st.code(f"Your Document ID: {data['doc_id']}", language="text")
                            if data.get("upload_types"):
                                st.caption(f"Saved: {', '.join(data['upload_types'])}")
                        else:
                            st.error(f"Upload failed: {data.get('detail', 'Unknown error')}")
                elif upload_submitted:
                    st.warning("Please upload at least one PDF/TXT report or one CT/X-ray image.")

        with tab_diag:
            st.markdown("### Get Medical Insights")
            st.markdown("Ask about uploaded reports or medical images. PDFs/TXT use report context, while CT/X-ray images use Gemini vision.")
            with st.container(border=True):
                with st.form("diagnosis_form"):
                    diagnosis_doc_id = st.text_input(
                        "Document ID (Auto-filled if recently uploaded)",
                        value=st.session_state.get('doc_id', '')
                    )
                    diagnosis_question = st.text_area(
                        "What do you want to know about your reports?",
                        "Can you summarize this report and provide a potential diagnosis?",
                        height=140,
                    )
                    diagnosis_submitted = st.form_submit_button("🧠 Get Diagnosis", type="primary")
                    
                if diagnosis_submitted:
                    if not diagnosis_doc_id:
                        st.warning("Please provide a valid Document ID.")
                    else:
                        with st.spinner("Analyzing reports and generating answer..."):
                            status_code, data = get_diagnosis(
                                st.session_state.auth,
                                diagnosis_doc_id,
                                diagnosis_question
                            )
                            if status_code == 200:
                                st.success("Analysis Complete!")
                                st.markdown("#### 📝 AI Diagnosis Result")
                                with st.container(border=True):
                                    st.markdown(data.get("diagnosis", "No diagnosis provided."))
                                    
                                with st.expander("📚 View Document Sources"):
                                    st.json(data.get("sources", []))
                            else:
                                st.error(f"Diagnosis failed: {data.get('detail', 'Unknown error')}")

    elif st.session_state.role == "doctor":
        st.header("⚕️ Doctor Dashboard")
        st.markdown("### View Patient Diagnosis History")
        
        with st.container(border=True):
            with st.form("doctor_form", clear_on_submit=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    patient_name_input = st.text_input("Search Patient's Username:", placeholder="e.g. john_doe")
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True) # alignments
                    view_submitted = st.form_submit_button("🔍 Search Records", use_container_width=True, type="primary")
                
        if view_submitted:
            with st.spinner(f"Retrieving medical history for {patient_name_input}..."):
                status_code, data = get_doctor_diagnosis(st.session_state.auth, patient_name_input)
                if status_code == 200:
                    if len(data) == 0:
                        st.info(f"No diagnosis records found for **{patient_name_input}**.")
                    else:
                        st.success(f"Found {len(data)} record(s) for **{patient_name_input}**.")
                        st.divider()
                        
                        for idx, record in enumerate(data):
                            with st.expander(f"🩺 Record {idx+1} | {datetime.datetime.fromtimestamp(record['timestamp']).strftime('%Y-%m-%d %H:%M')}", expanded=(idx==0)):
                                st.caption(f"**Doc ID:** `{record['doc_id']}` | **Record ID:** `{record['_id']}`")
                                st.markdown(f"**Question Asked:** _{record['question']}_")
                                st.markdown("---")
                                st.markdown("#### Diagnosis Answer")
                                st.markdown(record['answer'])
                                
                                if record['sources']:
                                    st.markdown("##### Sources Referenced:")
                                    for source in record['sources']:
                                        st.caption(f"- {source}")
                else:
                    st.error(f"Failed to fetch records: {data.get('detail', 'Unknown error')}")

    else:
        st.error("Unknown role detected. Please contact support.")