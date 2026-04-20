import time
from ultralytics import YOLO

# 1. Point to your ORIGINAL PyTorch model
MODEL_PATH = "bag.pt" 

# 2. Your exact test image
TEST_IMAGE = r"D:\projects\Final_year_project\bags_only_dataset\bags_only_dataset\images\test\backpack_3_jpeg.rf.e31982d18a1502e018ddb690eb05cd2f.jpg"

def run_baseline_benchmark():
    print("🚀 Loading ORIGINAL FP32 PyTorch Model for Benchmarking...")
    model = YOLO(MODEL_PATH, task='detect')

    print("🔥 Warming up the CPU...")
    for _ in range(5):
        model(TEST_IMAGE, imgsz=320, verbose=False) 

    print("⏱️ Running Baseline Benchmark (100 iterations)...")
    start_time = time.time()

    iterations = 100
    for _ in range(iterations):
        model(TEST_IMAGE, imgsz=320, verbose=False)

    end_time = time.time()
    
    total_time = end_time - start_time
    fps = iterations / total_time
    latency_ms = (total_time / iterations) * 1000

    print("\n" + "=" * 50)
    print("📉 ORIGINAL MODEL (BASELINE) RESULTS")
    print("=" * 50)
    print(f"Hardware:        Standard Laptop CPU")
    print(f"Format:          Standard PyTorch (FP32)")
    print(f"Total Time:      {total_time:.2f} seconds for 100 images")
    print(f"Average Speed:   {fps:.2f} Frames Per Second (FPS)")
    print(f"Latency:         {latency_ms:.2f} milliseconds per image")
    print("=" * 50)

if __name__ == "__main__":
    run_baseline_benchmark()