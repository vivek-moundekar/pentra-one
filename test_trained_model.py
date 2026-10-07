from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

BASE_MODEL_PATH = r"E:\udaan\models\qwen2.5-1.5b"
LORA_PATH = r"E:\udaan\models\udaan-education-lora"

print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    LORA_PATH
)

print("Loading base model...")

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    dtype=torch.float16,
    device_map="cpu",
    low_cpu_mem_usage=True
)

print("Loading trained LoRA adapter...")

model = PeftModel.from_pretrained(
    base_model,
    LORA_PATH
)

model.eval()

print("\n====================================")
print("UDAAN AI MODEL LOADED SUCCESSFULLY")
print("====================================")

while True:

    question = input("\nAsk Udaan AI (type exit to stop): ")

    if question.lower() == "exit":
        print("Chat ended.")
        break

    messages = [
        {
            "role": "system",
            "content": (
                "You are Udaan AI, an educational tutor. "
                "Answer students clearly and simply. "
                "Explain step by step when necessary."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(
        text,
        return_tensors="pt"
    )

    print("\nThinking...\n")

    with torch.no_grad():

        output = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=False,
            repetition_penalty=1.1
        )

    generated_tokens = output[0][
        inputs["input_ids"].shape[1]:
    ]

    answer = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    print("Udaan AI:")
    print(answer)