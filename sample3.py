import streamlit as st
from PIL import Image
import pandas as pd
import base64
import io
import time
import requests

# Function to load the icon image from GitHub URL
def load_icon():
    icon_url = "https://raw.githubusercontent.com/Puneeth-kmp/TMC/main/.devcontainer/PCANBasicExampleIcon.ico"
    response = requests.get(icon_url)
    img = Image.open(io.BytesIO(response.content))
    return img

# Function to convert image to base64 for embedding in HTML
def img_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="ICO")
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64

# Function to simulate firmware update process
def perform_firmware_update(vcu_serial_number, firmware_version):
    st.write(f"Starting firmware update for VCU {vcu_serial_number} to version {firmware_version}...")
    # Simulate progress for 72 seconds
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.1 / 100)  # 72 seconds total (0.72 seconds per increment)
        progress_bar.progress(i + 1)
    st.write(f"Firmware update for VCU {vcu_serial_number} to version {firmware_version} is complete.")
    # Log update status
    st.session_state.logs.append(f"Update for VCU {vcu_serial_number} to version {firmware_version} completed.")

# Initialize logs and firmware versions
if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'firmware_versions' not in st.session_state:
    st.session_state.firmware_versions = ["1.0.0", "1.0.1", "2.0.0"]

# Streamlit app layout
st.set_page_config(page_title="Takumi Motion Controls")

# Header with icon and company name
icon_base64 = img_to_base64(load_icon())
st.markdown(
    f"""
    <style>
        .header {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px;
        }}
        .header img {{
            height: 50px;
            margin-right: 10px;
        }}
        .header h1 {{
            font-size: 2em;
            margin: 0;
        }}
    </style>
    <div class="header">
        <img src="data:image/ico;base64,{icon_base64}" alt="Takumi Motion Controls Icon"/>
        <h1>Takumi Motion Controls</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Authentication logic
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if username == "admin" and password == "password":
            st.session_state.authenticated = True
            st.sidebar.success("Logged in successfully")
        else:
            st.sidebar.error("Invalid credentials")

# Check if authenticated
if st.session_state.authenticated:

    # Firmware Version Management
    st.sidebar.header("Firmware Management")
    st.sidebar.subheader("Upload New Firmware")
    firmware_file = st.sidebar.file_uploader("Upload firmware file", type=["zip", "bin"])

    if firmware_file:
        # Simulate storing the firmware file
        st.sidebar.write("Firmware file uploaded successfully.")
        st.session_state.firmware_versions.append("New Version")

    # Section for firmware update
    st.header("Firmware Update")
    st.write("Enter the details below to perform a firmware update.")

    # Input fields
    vcu_serial_number = st.text_input("Vehicle Control Unit (VCU) Serialc No")
    firmware_version = st.selectbox("Firmware Version", options=st.session_state.firmware_versions)
    submit_button = st.button("Update Firmware")

    if submit_button:
        if vcu_serial_number and firmware_version:
            perform_firmware_update(vcu_serial_number, firmware_version)
        else:
            st.error("Please enter both VCU Serial Number and Firmware Version.")

    # Section for displaying vehicle status
    st.header("Vehicle Status")
    status_data = {
        "VCU Serial Number": ["123456", "789012", "345678"],
        "Last Firmware Version": ["1.0.0", "1.0.1", "1.0.0"],
        "Update Status": ["Up-to-date", "Pending", "Up-to-date"]
    }
    status_df = pd.DataFrame(status_data)

    # Search and Filter
    search_term = st.text_input("Search by VCU Serial Number")
    filtered_df = status_df[status_df["VCU Serial Number"].str.contains(search_term, case=False)]

    st.write("Current status of vehicles in the fleet:")
    st.dataframe(filtered_df)

    # Logs and Error Reporting
    st.header("Update Logs")
    st.write("Recent logs and errors related to firmware updates:")
    st.text_area("Logs", value="\n".join(st.session_state.logs), height=200)

else:
    st.sidebar.info("Please log in to access the application.")
    
# Inject custom CSS to hide menu and footer options
hide_st_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        span {
            display: none;
        }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

