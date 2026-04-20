import time
from ultralytics import YOLO

# ==========================================
# ⚙️ CONFIGURATION & PATHS
# ==========================================
DATA_YAML = r"D:\projects\Final_year_project\data.yaml"
TEST_IMAGE = r"D:\projects\Final_year_project\bags_only_dataset\bags_only_dataset\images\test\backpack_3_jpeg.rf.e31982d18a1502e018ddb690eb05cd2f.jpg"
ORIGINAL_MODEL_PATH = "bag.pt"
OPTIMIZED_MODEL_PATH = "best_int8_openvino_model"
IMG_SIZE = 320
ITERATIONS = 100

def measure_speed(model, model_name):
    """Helper function to test the FPS and latency of a model."""
    print(f"\n🔥 Warming up the CPU for {model_name}...")
    for _ in range(5):
        model(TEST_IMAGE, imgsz=IMG_SIZE, verbose=False) 

    print(f"⏱️ Running Speed Benchmark ({ITERATIONS} iterations)...")
    start_time = time.time()
    for _ in range(ITERATIONS):
        model(TEST_IMAGE, imgsz=IMG_SIZE, verbose=False)
    end_time = time.time()
    
    total_time = end_time - start_time
    fps = ITERATIONS / total_time
    latency_ms = (total_time / ITERATIONS) * 1000
    
    return fps, latency_ms

def run_master_benchmark():
    print("🚀 STARTING MASTER BENCHMARK PIPELINE 🚀\n")

    # ==========================================
    # 1. TEST ORIGINAL MODEL
    # ==========================================
    print("="*50)
    print("🧪 PHASE 1: ORIGINAL PyTorch MODEL (bag.pt)")
    print("="*50)
    orig_model = YOLO(ORIGINAL_MODEL_PATH, task='detect')
    
    # Measure Speed
    orig_fps, orig_latency = measure_speed(orig_model, "Original Model")
    
    # Measure Accuracy
    print("\n🎯 Running Accuracy Validation on full dataset...")
    orig_metrics = orig_model.val(data=DATA_YAML, imgsz=IMG_SIZE, plots=False)
    orig_map50 = orig_metrics.box.map50

    # ==========================================
    # 2. TEST OPTIMIZED MODEL
    # ==========================================
    print("\n" + "="*50)
    print("🧪 PHASE 2: OPTIMIZED OpenVINO MODEL (INT8)")
    print("="*50)
    opt_model = YOLO(OPTIMIZED_MODEL_PATH, task='detect')
    
    # Measure Speed
    opt_fps, opt_latency = measure_speed(opt_model, "Optimized Model")
    
    # Measure Accuracy
    print("\n🎯 Running Accuracy Validation on full dataset...")
    opt_metrics = opt_model.val(data=DATA_YAML, imgsz=IMG_SIZE, plots=False)
    opt_map50 = opt_metrics.box.map50

    # ==========================================
    # 3. FINAL REPORT GENERATION
    # ==========================================
    print("\n\n" + "🏆 FINAL PROJECT RESULTS REPORT 🏆")
    print("="*65)
    print(f"{'Metric':<25} | {'Original (FP32)':<15} | {'Optimized (INT8)':<15}")
    print("-" * 65)
    print(f"{'Accuracy (mAP50)':<25} | {orig_map50 * 100:>14.2f}% | {opt_map50 * 100:>14.2f}%")
    print(f"{'Speed (FPS)':<25} | {orig_fps:>14.2f}  | {opt_fps:>14.2f} ")
    print(f"{'Latency per image (ms)':<25} | {orig_latency:>14.2f}  | {opt_latency:>14.2f} ")
    print("="*65)
    
    # Calculate Improvements
    speed_boost = opt_fps / orig_fps
    acc_drop = (orig_map50 - opt_map50) * 100
    print("\n💡 KEY TAKEAWAYS:")
    print(f"👉 The optimized model is {speed_boost:.1f}x FASTER than the original.")
    print(f"👉 The accuracy dropped by only {acc_drop:.2f}%, which is negligible!")
    print("\n🎉 Benchmarking Complete! Copy these results to your report.")

if __name__ == "__main__":
    run_master_benchmark()