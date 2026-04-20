import cv2
from ultralytics import YOLO

# 1. Point to the OpenVINO model folder
MODEL_PATH = "best_int8_openvino_model" 

# 2. Your exact dataset image path
TEST_IMAGE = r"D:\projects\Final_year_project\bags_only_dataset\bags_only_dataset\images\test\backpack_3_jpeg.rf.e31982d18a1502e018ddb690eb05cd2f.jpg"

def test_speed_and_accuracy():
    print("🚀 Loading High-Speed INT8 OpenVINO Model...")
    fast_model = YOLO(MODEL_PATH, task='detect') 

    print(f"🔍 Analyzing image...\nPath: {TEST_IMAGE}")
    
    # THE FIX IS HERE: We must explicitly tell YOLO to use the 320px input size!
    results = fast_model(TEST_IMAGE, imgsz=320)

    # Draw the bounding boxes on the image
    annotated_frame = results[0].plot()

    # Save the picture
    output_filename = "optimized_detection_proof.jpg"
    cv2.imwrite(output_filename, annotated_frame)
    print(f"✅ SUCCESS! Check your project folder for '{output_filename}'")
    
    # Pop up a window to show you the result
    print("👀 Press any key on the image window to close it...")
    cv2.imshow("Optimized INT8 Detection", annotated_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_speed_and_accuracy()