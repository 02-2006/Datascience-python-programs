import cv2
import numpy as np

# Create a black image
img = np.zeros((300, 768, 3), dtype=np.uint8)

# Blue gradient
for i in range(256):
    img[:, i] = (i, 0, 0)

# Green gradient
for i in range(256):
    img[:, i + 256] = (0, i, 0)

# Red gradient
for i in range(256):
    img[:, i + 512] = (0, 0, i)

# Display the image
while True:
    cv2.imshow("RGB Color Gradient", img)

    key = cv2.waitKey(1) & 0xFF

    # Press ESC to exit
    if key == 27:
        break

cv2.destroyAllWindows()