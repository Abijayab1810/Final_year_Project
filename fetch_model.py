import shutil
import os

# The exact path from your terminal screenshot
source_folder = r"C:\Users\abija\runs\detect\ptq_refinement_320\weights\best_int8_openvino_model"

# The destination (your current project folder)
destination_folder = "best_int8_openvino_model"

def fetch_my_model():
    print(f"🔍 Looking for model at: {source_folder}")
    
    if not os.path.exists(source_folder):
        print("❌ Error: Could not find the folder. Did the path change?")
        return

    # Copy the folder over
    if os.path.exists(destination_folder):
        print("⚠️ The folder already exists in your project! You are good to go.")
    else:
        print("📦 Found it! Copying to your project folder...")
        shutil.copytree(source_folder, destination_folder)
        print("✅ SUCCESS! The 'best_int8_openvino_model' folder is now in your project directory.")

if __name__ == "__main__":
    fetch_my_model()