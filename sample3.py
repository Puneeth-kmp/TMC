import streamlit as st
import os
import csv
import time
from datetime import datetime
import requests
from PIL import Image
import io
import base64

# Initialize session state if not already initialized
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.is_admin = False

# Function to load the icon from URL
def load_icon():
    icon_url = "https://raw.githubusercontent.com/Puneeth-kmp/TMC/main/.devcontainer/PCANBasicExampleIcon.ico"
    response = requests.get(icon_url)
    img = Image.open(io.BytesIO(response.content))
    return img

# Function to convert image to base64
def img_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="ICO")
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64

# Convert icon to base64
icon_base64 = img_to_base64(load_icon())

# Display header with logo and title
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
        <h1>Takumi Firmware Over The Air (FOTA)</h1>
    </div>
    """,
    unsafe_allow_html=True
)
# Directory paths
data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fota_data")
auth_data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fota_auth_data")
auth_csv_path = os.path.join(auth_data_directory, "auth_data.csv")

# Ensure the directories exist
os.makedirs(data_directory, exist_ok=True)
os.makedirs(auth_data_directory, exist_ok=True)

# Ensure auth_data.csv exists and contains default admin credentials
def ensure_auth_csv_exists():
    if not os.path.isfile(auth_csv_path):
        # Create the CSV file and add the default admin user
        with open(auth_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["UserID", "Password"])
            writer.writerow(["Pk", "tmc@124"])
        st.info("Authentication file created with default admin credentials.")

# Call the function to ensure the auth CSV exists
ensure_auth_csv_exists()

# Function to get target types from folder names
def get_target_types(folder_path):
    try:
        return [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]
    except FileNotFoundError:
        st.error(f"The directory {folder_path} does not exist.")
        return []

# Function to get firmware versions under a target type
def get_firmware_versions(target_folder):
    try:
        return [name for name in os.listdir(target_folder) if os.path.isdir(os.path.join(target_folder, name))]
    except FileNotFoundError:
        st.error(f"The directory {target_folder} does not exist.")
        return []

# Function to read VCU data from CSV
def read_vcu_data(csv_file_path):
    vcu_data = {}
    try:
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                vcu_data[row["VCU Serial Number"]] = {
                    "IP Address": row["IP Address"],
                    "Last Firmware Version": row["Last Firmware Version"]
                }
    except FileNotFoundError:
        st.error(f"The CSV file {csv_file_path} does not exist.")
    return vcu_data

# Function to create a CSV file with the target type name
def create_csv_file(csv_file_path):
    header = ["Sl No", "Device added on", "VCU Serial Number", "IP Address", "Last Firmware Version", "Last Update On", "Update Status"]
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)

# Function to append new data to the CSV file
def append_to_csv(csv_file_path, data):
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

# Function to get the next available Sl No
def get_next_sl_no(csv_file_path):
    max_sl_no = 0
    if os.path.isfile(csv_file_path):
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    current_sl_no = int(row["Sl No"])
                    if current_sl_no > max_sl_no:
                        max_sl_no = current_sl_no
                except ValueError:
                    continue
    return max_sl_no + 1

# Function to update device entry in the CSV file
def update_device_in_csv(csv_file_path, vcu_serial_number, firmware_version):
    temp_file = csv_file_path + '.tmp'
    with open(csv_file_path, mode='r') as file, open(temp_file, mode='w', newline='') as new_file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(new_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            if row["VCU Serial Number"] == vcu_serial_number:
                row["Last Firmware Version"] = firmware_version
                row["Last Update On"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row["Update Status"] = "Updated"
            writer.writerow(row)
    os.replace(temp_file, csv_file_path)

# Function to handle "Upload Firmware to VCU"
def upload_firmware_to_vcu():
    st.write("You selected: Upload Firmware to VCU")
    
    # Get the list of target types
    target_types = get_target_types(data_directory)
    
    if target_types:
        # Combo box to select target type
        selected_target_type = st.selectbox("Select Target Type", target_types)
        
        if selected_target_type:
            # Get the CSV file path for the selected target type
            csv_file_path = os.path.join(data_directory, selected_target_type, f"{selected_target_type}_device_details.csv")
            
            # Get VCU data from CSV
            vcu_data = read_vcu_data(csv_file_path)
            
            if vcu_data:
                # Combo box to select VCU Serial Number
                selected_vcu_serial = st.selectbox("Select VCU Serial Number", list(vcu_data.keys()))
                
                if selected_vcu_serial:
                    # Display the IP Address for the selected VCU
                    st.write(f"IP Address: {vcu_data[selected_vcu_serial]['IP Address']}")
                    
                    # Get the list of firmware versions for the selected target type
                    firmware_versions = get_firmware_versions(os.path.join(data_directory, selected_target_type))
                    
                    if firmware_versions:
                        # Combo box to select firmware version
                        selected_firmware_version = st.selectbox("Select Firmware Version", firmware_versions)
                        
                        if st.button("Do FOTA"):
                            # Simulate firmware upload
                            with st.spinner("Uploading firmware..."):
                                time.sleep(2)  # Simulate upload time
                                st.success(f"Firmware '{selected_firmware_version}' uploaded successfully to VCU '{selected_vcu_serial}'.")
                                
                                # Update the CSV file with the new firmware version
                                update_device_in_csv(csv_file_path, selected_vcu_serial, selected_firmware_version)
                    else:
                        st.error(f"No firmware versions available under target type '{selected_target_type}'.")
            else:
                st.error(f"No VCU data available for target type '{selected_target_type}'.")
    else:
        st.error("No target types available.")

# Function to handle "Upload Binary to Server"
def upload_binary_to_server():
    st.write("You selected: Upload Binary to Server")
    
    # Get the list of target types (folder names)
    target_types = get_target_types(data_directory)
    
    # Add an option to add a new target type
    target_types.append("Add New Target Type")
    
    # Create a dropdown to select target type
    selected_target_type = st.selectbox("Select Target Type", target_types)
    
    if selected_target_type == "Add New Target Type":
        new_target_type_name = st.text_input("Enter the name of the new target type")
        binary_version = st.text_input("Enter the binary version")
        binary_file = st.file_uploader("Choose a binary file", type=['bin'])
        
        if new_target_type_name and binary_version and binary_file:
            new_folder_path = os.path.join(data_directory, new_target_type_name, binary_version)
            csv_file_path = os.path.join(data_directory, new_target_type_name, f"{new_target_type_name}_device_details.csv")
            
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
                
                # Create the CSV file with the same name as the target type
                create_csv_file(csv_file_path)
                
                # Save the binary file
                with open(os.path.join(new_folder_path, binary_file.name), "wb") as f:
                    f.write(binary_file.read())
                
                st.success(f"Binary file uploaded successfully to new target type '{new_target_type_name}'.")
            else:
                st.error(f"Target type '{new_target_type_name}' already exists.")
    elif selected_target_type:
        binary_version = st.text_input("Enter the binary version")
        binary_file = st.file_uploader("Choose a binary file", type=['bin'])
        
        if binary_file and binary_version:
            binary_folder_path = os.path.join(data_directory, selected_target_type, binary_version)
            
            if not os.path.exists(binary_folder_path):
                os.makedirs(binary_folder_path)
                
                # Save the binary file
                with open(os.path.join(binary_folder_path, binary_file.name), "wb") as f:
                    f.write(binary_file.read())
                
                st.success(f"Binary file uploaded successfully to target type '{selected_target_type}'.")
            else:
                st.error(f"Binary version '{binary_version}' already exists for target type '{selected_target_type}'.")

# Function to handle "Add New Device"
def add_new_device():
    st.write("You selected: Add New Device")
    
    # Get the list of target types
    target_types = get_target_types(data_directory)
    
    if target_types:
        # Combo box to select target type
        selected_target_type = st.selectbox("Select Target Type", target_types)
        
        if selected_target_type:
            # Get the CSV file path for the selected target type
            csv_file_path = os.path.join(data_directory, selected_target_type, f"{selected_target_type}_device_details.csv")
            
            # Get VCU data from CSV
            vcu_data = read_vcu_data(csv_file_path)
            
            # Text input for VCU Serial Number
            vcu_serial_number = st.text_input("Enter VCU Serial Number")
            
            # Text input for IP Address
            ip_address = st.text_input("Enter IP Address")
            
            # Get the list of firmware versions for the selected target type
            firmware_versions = get_firmware_versions(os.path.join(data_directory, selected_target_type))
            
            if firmware_versions:
                # Combo box to select firmware version
                selected_firmware_version = st.selectbox("Select Firmware Version", firmware_versions)
                
                # Arrange the buttons and "Or" text side by side with minimal gaps
                col1, col2, col3 = st.columns([1, 0.1, 1])
                
                with col1:
                    if st.button("Add Device"):
                        if vcu_serial_number and ip_address and selected_firmware_version:
                            # Get the next available Sl No
                            next_sl_no = get_next_sl_no(csv_file_path)
                            
                            # Add new device information to the CSV file
                            append_to_csv(csv_file_path, [
                                next_sl_no,  # Sl No
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Device added on
                                vcu_serial_number,
                                ip_address,
                                selected_firmware_version,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Last Update On
                                "Added"
                            ])
                            st.success(f"Device '{vcu_serial_number}' added successfully.")
                        else:
                            st.error("Please fill in all the fields.")
                
                with col1:
                    st.write("Or")  # Adding "Or" text with minimal spacing
                    
                with col1:
                    if st.button("Get Device Details via CAN"):
                        st.warning("Device Not Connected")
            else:
                st.error(f"No firmware versions available under target type '{selected_target_type}'.")
    else:
        st.error("No target types available.")

    

# Function to handle login
def login(username, password):
    # Check if the authentication CSV exists and create it if necessary
    ensure_auth_csv_exists()
    
    # Read the CSV file to validate credentials
    try:
        with open(auth_csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["UserID"] == username and row["Password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.is_admin = (username == "Pk")
                    st.success("Logged in successfully.")
                    return
    except FileNotFoundError:
        st.error("Authentication file not found.")
    
    st.error("Invalid username or password.")

# Function to handle logout
def logout():
    st.session_state.authenticated = False
    st.session_state.is_admin = False
    st.success("Logged out successfully.")

# Function to add new users in a unique way
def add_new_user():
    st.write("**Admin: Add New User**")
    
    # Unique interactive approach
    st.markdown("<h3 style='color:blue;'>👤 Add a New User</h3>", unsafe_allow_html=True)
    
    # Use a container with a background color for better visualization
    with st.container():
        new_user_id = st.text_input("🔐 Enter New User ID")
        new_user_password = st.text_input("🔑 Enter New User Password", type="password")
        
        if st.button("🆕 Add User"):
            if new_user_id and new_user_password:
                # Append new user data
                with open(auth_csv_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([new_user_id, new_user_password])
                
                st.success(f"New user '{new_user_id}' added successfully.")
            else:
                st.error("Please enter both user ID and password.")

# Sidebar for login/logout
with st.sidebar:
    if st.session_state.authenticated:
        st.write("**Logged In**")
        if st.session_state.is_admin:
            st.write("**Admin**")
            add_new_user()  # Admin can add new users
        if st.button("Logout"):
            logout()
    else:
        st.write("**Not Logged In**")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login(username, password)

# Main content based on authentication
if st.session_state.authenticated:
   # st.title("Takumi Firmware Over The Air (FOTA)")

    option = st.sidebar.selectbox(
        "Choose an option",
        ["Upload Binary to Server", "Upload Firmware to VCU", "Add New Device"]
    )

    if option == "Upload Binary to Server":
        upload_binary_to_server()
    elif option == "Upload Firmware to VCU":
        upload_firmware_to_vcu()
    elif option == "Add New Device":
        add_new_device()
else:
    st.write("Please log in to access the application.")
    
