#GUI implementation of main
#WIP
#Opted for Streamlit as GUI module

import streamlit as st
import time

# Title of the app
st.title("My First Streamlit App")

# Text input
name = st.text_input("Enter your name:")

# Button
if st.button("Submit"):
    st.write(f"Hello, {name}!")

st.title("Progress Bar Example")

# Create a progress bar
progress_bar = st.progress(0)

for i in range(100):
    # Update the progress bar
    progress_bar.progress(i + 1)
    time.sleep(0.05)  # Simulate a long-running task

st.write("Task completed!")
