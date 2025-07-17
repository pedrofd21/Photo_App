#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 11:12:36 2025

@author: pedrodorea
"""

import streamlit as st
from PIL import Image

st.set_page_config(page_title="Camera and Gallery Access", layout="centered")
st.title("📸 Camera and Gallery Access")

# Initialize session state
if "camera_confirmed" not in st.session_state:
    st.session_state.camera_confirmed = False
if "gallery_confirmed" not in st.session_state:
    st.session_state.gallery_confirmed = False

st.markdown("Choose an option below:")

# CAMERA SECTION
with st.expander("📷 Access Camera"):
    confirm = st.checkbox("I allow access to the camera", key="cam_confirm")
    if confirm:
        st.session_state.camera_confirmed = True
        img_file = st.camera_input("Take a photo now:")
        if img_file is not None:
            st.image(img_file, caption="📸 Photo Taken", use_column_width=True)
    else:
        st.warning("Please confirm access to the camera.")

# GALLERY SECTION
with st.expander("🖼️ Access Photo Gallery"):
    confirm = st.checkbox("I allow access to the photo library", key="gal_confirm")
    if confirm:
        st.session_state.gallery_confirmed = True
        uploaded_file = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="🖼️ Photo Uploaded", use_column_width=True)
    else:
        st.warning("Please confirm access to the photo gallery.")
