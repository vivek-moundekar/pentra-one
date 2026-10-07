from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

BASE_MODEL = r"E:\udaan\models\qwen2.5-1.5b"
LORA_MODEL = r"E:\udaan\models\udaan-education-lora"
OUTPUT_MODEL = r"E:\udaan\models\udaan-education-merged"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

print("Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.float16,
    device_map="cpu",
    low_cpu_mem_usage=True
)

print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(
    base_model,
    LORA_MODEL
)

print("Merging...")
merged_model = model.merge_and_unload()

print("Saving merged model...")
merged_model.save_pretrained(
    OUTPUT_MODEL,
    safe_serialization=True
)

tokenizer.save_pretrained(OUTPUT_MODEL)

print("Done.")
print("Saved at:", OUTPUT_MODEL)