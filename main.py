import cv2
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim

def process_change_detection(input_dir, output_dir):
    # Requirement: Create output folder if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Requirement: Identify 'before' images (X.jpg)
    before_images = [f for f in os.listdir(input_dir) if f.lower().endswith('.jpg') and '~' not in f]

    for filename in before_images:
        base_name = os.path.splitext(filename)[0]
        before_path = os.path.join(input_dir, filename)
        # Requirement: After image naming convention is X~2.jpg
        after_path = os.path.join(input_dir, f"{base_name}~2.jpg")

        if not os.path.exists(after_path):
            continue

        # Load images
        img_before = cv2.imread(before_path)
        img_after = cv2.imread(after_path)

        # Convert to grayscale for structural analysis
        gray_before = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
        gray_after = cv2.cvtColor(img_after, cv2.COLOR_BGR2GRAY)

        # 1. Structural Similarity Index (SSIM)
        # This is powerful because it looks at patterns, not just pixel colors
        (score, diff) = ssim(gray_before, gray_after, full=True)
        diff = (diff * 255).astype("uint8")

        # 2. Thresholding: BINARY_INV makes changes white and background black
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # 3. Morphological Operations: Join small dots into solid objects
        # This ensures small objects like people are captured in one box
        kernel = np.ones((5,5), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=3)

        # 4. Find Contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        annotated_after = img_after.copy()
        for cnt in contours:
            # Set a low area threshold (e.g., 30) to catch tiny objects like hikers
            if cv2.contourArea(cnt) > 30: 
                x, y, w, h = cv2.boundingRect(cnt)
                # Requirement: Draw boxes around missing objects in after image
                cv2.rectangle(annotated_after, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Requirement: Save original before (X.jpg) and annotated after (X~3.jpg)
        cv2.imwrite(os.path.join(output_dir, filename), img_before)
        cv2.imwrite(os.path.join(output_dir, f"{base_name}~3.jpg"), annotated_after)
        
        print(f"Processed: {base_name} - Caught changes with similarity score: {score:.4f}")

if __name__ == "__main__":
    # Update these paths to your desktop locations
    input_folder = r"C:\Users\nagen\OneDrive\Desktop\claude\Task 2 - Change Detection Algorithm\input-images"
    output_folder = r"C:\Users\nagen\OneDrive\Desktop\claude\Task 2 - Change Detection Algorithm\task_2_output"
    
    process_change_detection(input_folder, output_folder)