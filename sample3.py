import streamlit as st
from PIL import Image

# Function to display the icon
def show_icon():
    # Load and display the icon
    img_path = "D:\\downloads\\PCANBasicExampleIcon.ico"
    img = Image.open(img_path)
    st.image(img, caption="PCAN Basic Example Icon")

# Streamlit app layout
st.title("Icon Display App")
st.write("Press the button to display the icon")

if st.button("Show Icon"):
    show_icon()

# Inject custom CSS to hide menu and footer options and specific elements
hide_st_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* Target the span containing 'Deploy' text */
        span {
            display: none;
        }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
