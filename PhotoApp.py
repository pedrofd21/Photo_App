#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 11:12:36 2025

@author: pedrodorea
"""

import streamlit as st
import numpy as np
import pandas as pd
import cv2
from PIL import Image

st.set_page_config(layout="wide")
st.title("🌿 Grass Analyzer App")
st.markdown("Upload or take pictures of grass/forage. This app detects green (healthy) vs. dried blades and summarizes them in a table.")

# === Image Processing Function ===
def analyze_image(image_pil):
    image = np.array(image_pil.convert("RGB"))
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # Green mask
    lower_green = np.array([30, 40, 40])
    upper_green = np.array([90, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # Dried mask
    lower_dried = np.array([10, 20, 100])
    upper_dried = np.array([30, 255, 255])
    dried_mask = cv2.inRange(hsv, lower_dried, upper_dried)

    # Percentages
    green_area = np.sum(green_mask > 0)
    dried_area = np.sum(dried_mask > 0)
    total_area = green_area + dried_area
    green_pct = 100 * green_area / total_area if total_area else 0
    dried_pct = 100 * dried_area / total_area if total_area else 0

    # Overlay
    overlay = image_bgr.copy()
    green_overlay = np.zeros_like(overlay); green_overlay[:, :] = (0, 255, 0)
    overlay = np.where(green_mask[..., None] > 0, cv2.addWeighted(overlay, 0.6, green_overlay, 0.4, 0), overlay)
    yellow_overlay = np.zeros_like(overlay); yellow_overlay[:, :] = (50, 50, 150)
    overlay = np.where(dried_mask[..., None] > 0, cv2.addWeighted(overlay, 0.6, yellow_overlay, 0.4, 0), overlay)
    overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

    return image, overlay_rgb, green_pct, dried_pct

# === Upload interface ===
uploaded_files = st.file_uploader(
    "📸 Take or choose photos of grass",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    label_visibility="visible"
)

if uploaded_files:
    results = []
    for idx, uploaded_file in enumerate(uploaded_files, start=1):
        image_pil = Image.open(uploaded_file)
        image_rgb, overlay_rgb, green_pct, dried_pct = analyze_image(image_pil)

        st.markdown(f"### 🖼️ Image {idx}")
        col1, col2 = st.columns(2)
        with col1:
            st.image(image_rgb, caption="Original", use_column_width=True)
        with col2:
            st.image(overlay_rgb, caption="Overlay: Green vs Dried", use_column_width=True)

        results.append({
            "Image": f"Image {idx}",
            "Green %": round(green_pct, 1),
            "Dried %": round(dried_pct, 1)
        })

    df_results = pd.DataFrame(results)
    st.markdown("### 📊 Summary Table")
    st.dataframe(df_results, use_container_width=True)
