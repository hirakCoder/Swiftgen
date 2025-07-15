#!/usr/bin/env python3
import subprocess
import sys
import os

# Step 1: Install all requirements
print("Installing production dependencies...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_training.txt"])

# Step 2: Verify GPU is available
import torch
print(f"\nGPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("ERROR: No GPU found! This will be very slow.")

# Step 3: Configure training parameters
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["WANDB_MODE"] = "offline"  # For now, we'll track locally

# Step 4: Verify data file exists
if not os.path.exists("training_data.json"):
    print("ERROR: training_data.json not found!")
    sys.exit(1)

# Step 5: Run the actual training
print("\nStarting production training...")
print("This will take 4-6 hours on RTX 4090...")
subprocess.run([sys.executable, "llama_finetuning_pipeline.py"])