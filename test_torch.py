# Check if CUDA is available
import torch.cuda


if torch.cuda.is_available():
    # Print the number of available GPUs
    print(f"CUDA is available! Number of GPUs: {torch.cuda.device_count()}")
    
    # Get the name of the current GPU
    gpu_name = torch.cuda.get_device_name(0)
    print(f"GPU Name: {gpu_name}")
else:
    print("CUDA is not available.")