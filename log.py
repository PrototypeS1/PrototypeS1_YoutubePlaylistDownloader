import streamlit as st
import streamlit.components.v1 as components
import json

def log_to_console(message: str) -> None:
    """Logs messages to the browser console."""
    js_code = f"""
    <script>
        console.log({json.dumps(message)});
    </script>
    """
    components.html(js_code, height=0)  # Set height to 0 to avoid affecting the layout

# Streamlit app to test console logging
st.title("Console Logger Test")

if st.button("Test Log to Console"):
    log_to_console("This is a test log message sent to the browser console!")
