#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 14:19:37 2025

@author: pedrodorea
"""

import cv2
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt

# === CONFIG ===
input_folder = "/Users/pedrodorea/Downloads/images/inputs"
output_folder = "/Users/pedrodorea/Downloads/images/outputs"
os.makedirs(output_folder, exist_ok=True)

# === Process each image ===
for filename in os.listdir(input_folder):
    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        continue

    print(f"Processing: {filename}")
    input_path = os.path.join(input_folder, filename)
    base_name = os.path.splitext(filename)[0]

    # Load image
    image_pil = Image.open(input_path).convert("RGB")
    image = np.array(image_pil)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # === Convert to HSV ===
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Green mask
    lower_green = np.array([30, 40, 40])
    upper_green = np.array([90, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # Dried mask (yellow/brown)
    lower_dried = np.array([10, 20, 100])
    upper_dried = np.array([30, 255, 255])
    dried_mask = cv2.inRange(hsv, lower_dried, upper_dried)

    # === Leaf vs Stem detection ===
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    # Morphological filters
    kernel_leaf = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    kernel_stem = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))  # long vertical kernel for stems

    leaf_like = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_leaf)
    stem_like = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel_stem)

    leaf_mask = cv2.threshold(leaf_like, 30, 255, cv2.THRESH_BINARY)[1]
    stem_mask = cv2.threshold(stem_like, 30, 255, cv2.THRESH_BINARY)[1]

    # === Enhance Green ===
    h, s, v = cv2.split(hsv)
    s_boosted = cv2.add(s, (green_mask // 255) * 60)
    v_boosted = cv2.add(v, (green_mask // 255) * 40)
    s_boosted = np.clip(s_boosted, 0, 255).astype(np.uint8)
    v_boosted = np.clip(v_boosted, 0, 255).astype(np.uint8)
    hsv_boosted = cv2.merge([h, s_boosted, v_boosted])
    enhanced_image = cv2.cvtColor(hsv_boosted, cv2.COLOR_HSV2BGR)

    # === Green/Yellow overlay mask ===
    overlay = image.copy()
    green_overlay = np.zeros_like(image)
    green_overlay[:, :] = (0, 255, 0)
    overlay = np.where(green_mask[..., None] > 0, cv2.addWeighted(overlay, 0.6, green_overlay, 0.4, 0), overlay)

    yellow_overlay = np.zeros_like(image)
    yellow_overlay[:, :] = (50, 50, 150)
    overlay = np.where(dried_mask[..., None] > 0, cv2.addWeighted(overlay, 0.6, yellow_overlay, 0.4, 0), overlay)

    # === Proportion calculation ===
    green_area = np.sum(green_mask > 0)
    dried_area = np.sum(dried_mask > 0)
    total_area = green_area + dried_area
    if total_area > 0:
        green_pct = 100 * green_area / total_area
        dried_pct = 100 * dried_area / total_area
    else:
        green_pct = dried_pct = 0.0

    # === Add label ===
    overlay_with_text = overlay.copy()
    label_text = f"Green: {green_pct:.1f}%  |  Dried: {dried_pct:.1f}%"
    cv2.putText(
        overlay_with_text, label_text,
        org=(overlay.shape[1] - 1000, 200),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=2.0,
        color=(255, 255, 255),
        thickness=2,
        lineType=cv2.LINE_AA
    )

    # === Save outputs ===
    cv2.imwrite(os.path.join(output_folder, f"{base_name}_green_mask.png"), green_mask)
    cv2.imwrite(os.path.join(output_folder, f"{base_name}_dried_mask.png"), dried_mask)
    cv2.imwrite(os.path.join(output_folder, f"{base_name}_leaf_mask.png"), leaf_mask)
    cv2.imwrite(os.path.join(output_folder, f"{base_name}_stem_mask.png"), stem_mask)
    cv2.imwrite(os.path.join(output_folder, f"{base_name}_enhanced_green.png"), cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB))
    cv2.imwrite(os.path.join(output_folder, f"{base_name}_overlay.png"), cv2.cvtColor(overlay_with_text, cv2.COLOR_BGR2RGB))

    print(f"Saved results for {filename}")
