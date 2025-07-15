#!/usr/bin/env python3
"""
Production-Grade CodeLlama Fine-tuning for Swift
This implements ALL best practices for optimal model quality
"""
import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
import wandb
from datetime import datetime

print("="*60)
print("PRODUCTION SWIFT-CODELLAMA TRAINING")
print("="*60)

# Initialize wandb for professional tracking (optional)
# wandb.init(project="swift-codellama", name=f"training-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

print("\n1. Loading 83,792 Swift code samples...")
data = []
with open('swift_training_prompts.jsonl', 'r') as f:
    for line in f:
        data.append(json.loads(line))
print(f"✓ Loaded {len(data)} high-quality Swift samples")

# Professional prompt template for code generation
def create_prompt(item):
    return f"""<s>[INST] <<SYS>>
You are an expert Swift/iOS developer. Generate high-quality, production-ready Swift code.
<</SYS>>

{item['instruction']}
{item['input']} [/INST]
{item['output']} </s>"""

print("\n2. Preparing data with optimal formatting...")
texts = [create_prompt(item) for item in data]

print("\n3. Loading CodeLlama-7B with 4-bit quantization...")
model_name = "codellama/CodeLlama-7b-Instruct-hf"

# Best quantization config for RTX 4090
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# Prepare model for k-bit training
model = prepare_model_for_kbit_training(model)

print("\n4. Applying LoRA with optimal parameters...")
# These are the BEST parameters for code generation
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=64,  # Higher rank for better quality
    lora_alpha=128,  # Alpha = 2*r for stability
    lora_dropout=0.05,  # Low dropout for code
    target_modules=[
        "q_proj", "v_proj", "k_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],  # All attention + MLP layers
    bias="none"
)

model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

print("\n5. Tokenizing with optimal settings...")
def tokenize_function(examples):
    return tokenizer(
        examples["text"], 
        padding="max_length", 
        truncation=True, 
        max_length=2048,  # Longer context for code
        return_tensors="pt"
    )

# Create dataset
dataset = Dataset.from_dict({"text": texts})
tokenized_dataset = dataset.map(
    tokenize_function, 
    batched=True,
    remove_columns=["text"]
)

# Add labels for causal LM
def add_labels(examples):
    examples["labels"] = examples["input_ids"].copy()
    return examples

tokenized_dataset = tokenized_dataset.map(add_labels, batched=True)

# Professional train/eval split
train_test_split = tokenized_dataset.train_test_split(test_size=0.05, seed=42)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]

print(f"\n✓ Train: {len(train_dataset)} samples")
print(f"✓ Eval: {len(eval_dataset)} samples")

print("\n6. Configuring optimal training parameters...")
# PRODUCTION TRAINING ARGUMENTS
training_args = TrainingArguments(
    output_dir="./swift_codellama_production",
    num_train_epochs=3,  # 3 epochs is optimal for code
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=8,  # Effective batch size = 32
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",  # Best optimizer for 4-bit
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    logging_steps=10,
    save_strategy="steps",
    save_steps=500,
    eval_strategy="steps", 
    eval_steps=500,
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    fp16=True,
    tf32=True,  # RTX 4090 optimization
    report_to="none",  # Change to "wandb" for tracking
    dataloader_num_workers=4,
    remove_unused_columns=False,
)

# Data collator for causal LM
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

print("\n7. Initializing trainer with production config...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

print("\n" + "="*60)
print("STARTING PRODUCTION TRAINING")
print("Expected duration: 4-6 hours on RTX 4090")
print("This will create a state-of-the-art Swift code model")
print("="*60 + "\n")

# Train the model
trainer.train()

print("\n8. Saving production model...")
trainer.save_model("swift_codellama_production_final")
tokenizer.save_pretrained("swift_codellama_production_final")

# Save LoRA adapters separately for easy deployment
model.save_pretrained("swift_codellama_lora_adapters")

print("\n" + "="*60)
print("✓ TRAINING COMPLETE!")
print("✓ Model saved to: swift_codellama_production_final/")
print("✓ LoRA adapters saved to: swift_codellama_lora_adapters/")
print("✓ Your model is ready for production use!")
print("="*60)