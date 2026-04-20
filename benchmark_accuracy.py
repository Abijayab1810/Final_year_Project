from ultralytics import YOLO

# FIXED PATH: This now points directly to the data.yaml in your main project folder!
DATA_YAML = r"D:\projects\Final_year_project\data.yaml"

def run_accuracy_benchmark():
    print("\n" + "="*50)
    print("🧪 1. TESTING ORIGINAL MODEL (bag.pt)")
    print("="*50)
    original_model = YOLO("bag.pt")
    # This checks how accurate the original model is
    orig_metrics = original_model.val(data=DATA_YAML, imgsz=320, plots=False) 
    
    print("\n" + "="*50)
    print("🧪 2. TESTING OPTIMIZED MODEL (OpenVINO)")
    print("="*50)
    optimized_model = YOLO("best_int8_openvino_model", task='detect')
    # This checks how accurate the new fast model is
    opt_metrics = optimized_model.val(data=DATA_YAML, imgsz=320, plots=False)

    print("\n\n" + "🏆 FINAL ACCURACY SCORES 🏆")
    print("="*50)
    print(f"Original Model Accuracy (mAP50):  {orig_metrics.box.map50:.4f}")
    print(f"Optimized Model Accuracy (mAP50): {opt_metrics.box.map50:.4f}")
    print("="*50)

if __name__ == "__main__":
    run_accuracy_benchmark()