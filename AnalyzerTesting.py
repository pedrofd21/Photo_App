#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 15:02:39 2025

@author: pedrodorea
"""

import cv2
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt


input_folder = "/Users/pedrodorea/Downloads/images/inputs/2b5b33e6-90c7-4a80-b79d-dc6a494eea6c.jpeg"

image_pil = Image.open(input_folder).convert("RGB")
image = np.array(image_pil)
image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


plt.imshow(image)
plt.axis('off')
plt.title("test")
plt.show()



hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

plt.imshow(hsv)
plt.axis('off')
plt.title("test")
plt.show()


# Green mask
lower_green = np.array([30, 40, 40])
upper_green = np.array([90, 255, 255])
green_mask = cv2.inRange(hsv, lower_green, upper_green)

plt.imshow(green_mask)
plt.axis('off')
plt.title("test")
plt.show()

# Dried mask (yellow/brown)
lower_dried = np.array([10, 20, 100])
upper_dried = np.array([30, 255, 255])
dried_mask = cv2.inRange(hsv, lower_dried, upper_dried)

plt.imshow(dried_mask)
plt.axis('off')
plt.title("test")
plt.show()


