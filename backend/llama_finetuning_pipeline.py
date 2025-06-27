#!/usr/bin/env python3
"""
Llama Fine-tuning Pipeline for Swift Code Generation
Supports Llama 3, CodeLlama, and other compatible models
"""

import os
import json
import torch
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import random
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from datasets import Dataset, DatasetDict
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType
)
import evaluate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LlamaFineTuner:
    """Fine-tune Llama models for Swift code generation"""
    
    def __init__(self, 
                 model_name: str = "meta-llama/Llama-2-7b-hf",
                 output_dir: str = "swift_llama_model"):
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Model and tokenizer will be loaded when needed
        self.model = None
        self.tokenizer = None
        
        # Training configuration
        self.max_length = 2048
        self.batch_size = 4
        self.learning_rate = 2e-4
        self.num_epochs = 3
        
        # LoRA configuration for efficient fine-tuning
        self.lora_config = LoraConfig(
            r=16,  # Rank
            lora_alpha=32,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
            lora_dropout=0.1,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )
    
    def prepare_model(self, use_8bit: bool = True):
        """Load and prepare model for fine-tuning"""
        logger.info(f"Loading model: {self.model_name}")
        
        # Quantization config for 8-bit training (reduces memory usage)
        bnb_config = None
        if use_8bit:
            bnb_config = BitsAndBytesConfig(
                load_in_8bit=True,
                bnb_8bit_compute_dtype=torch.float16
            )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Prepare for k-bit training
        if use_8bit:
            self.model = prepare_model_for_kbit_training(self.model)
        
        # Apply LoRA
        self.model = get_peft_model(self.model, self.lora_config)
        self.model.print_trainable_parameters()
        
        logger.info("Model prepared for fine-tuning")
    
    def load_training_data(self, data_path: str) -> DatasetDict:
        """Load and prepare training data"""
        logger.info(f"Loading training data from: {data_path}")
        
        # Load JSONL file
        data = []
        with open(data_path, 'r') as f:
            for line in f:
                data.append(json.loads(line))
        
        # Shuffle and split data
        random.shuffle(data)
        split_idx = int(len(data) * 0.9)
        train_data = data[:split_idx]
        val_data = data[split_idx:]
        
        # Create datasets
        train_dataset = Dataset.from_list(train_data)
        val_dataset = Dataset.from_list(val_data)
        
        # Tokenize datasets
        train_dataset = train_dataset.map(
            self._tokenize_function,
            batched=True,
            remove_columns=train_dataset.column_names
        )
        
        val_dataset = val_dataset.map(
            self._tokenize_function,
            batched=True,
            remove_columns=val_dataset.column_names
        )
        
        return DatasetDict({
            "train": train_dataset,
            "validation": val_dataset
        })
    
    def _tokenize_function(self, examples):
        """Tokenize examples for training"""
        # Format as instruction-following
        prompts = []
        for prompt, completion in zip(examples["prompt"], examples["completion"]):
            # Use Llama's instruction format
            text = f"""<s>[INST] {prompt} [/INST] {completion}</s>"""
            prompts.append(text)
        
        # Tokenize
        model_inputs = self.tokenizer(
            prompts,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Set labels (same as input_ids for language modeling)
        model_inputs["labels"] = model_inputs["input_ids"].clone()
        
        return model_inputs
    
    def create_trainer(self, train_dataset, val_dataset):
        """Create Hugging Face Trainer"""
        training_args = TrainingArguments(
            output_dir=str(self.output_dir / "checkpoints"),
            overwrite_output_dir=True,
            num_train_epochs=self.num_epochs,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            gradient_accumulation_steps=4,
            gradient_checkpointing=True,
            optim="adamw_torch",
            learning_rate=self.learning_rate,
            warmup_steps=100,
            logging_steps=25,
            save_strategy="epoch",
            evaluation_strategy="epoch",
            save_total_limit=2,
            load_best_model_at_end=True,
            report_to="none",  # Can be "wandb" if you want to track
            fp16=True,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
        )
        
        return trainer
    
    def train(self, data_path: str):
        """Run the complete training pipeline"""
        # Prepare model
        self.prepare_model()
        
        # Load data
        datasets = self.load_training_data(data_path)
        
        # Create trainer
        trainer = self.create_trainer(
            datasets["train"],
            datasets["validation"]
        )
        
        # Train
        logger.info("Starting training...")
        trainer.train()
        
        # Save model
        logger.info("Saving fine-tuned model...")
        trainer.save_model(str(self.output_dir / "final_model"))
        self.tokenizer.save_pretrained(str(self.output_dir / "final_model"))
        
        logger.info("Training complete!")
    
    def generate_swift_code(self, prompt: str, max_length: int = 1024) -> str:
        """Generate Swift code using the fine-tuned model"""
        if self.model is None:
            # Load the fine-tuned model
            self.model = AutoModelForCausalLM.from_pretrained(
                str(self.output_dir / "final_model"),
                device_map="auto",
                torch_dtype=torch.float16
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.output_dir / "final_model")
            )
        
        # Format prompt
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        
        # Tokenize
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=0.7,
                do_sample=True,
                top_p=0.95,
                repetition_penalty=1.15,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the generated code (after the instruction)
        if "[/INST]" in generated:
            code = generated.split("[/INST]")[-1].strip()
            return code
        
        return generated


class CodeLlamaFineTuner(LlamaFineTuner):
    """Specialized fine-tuner for CodeLlama models"""
    
    def __init__(self, output_dir: str = "swift_codellama_model"):
        # Use CodeLlama model
        super().__init__(
            model_name="codellama/CodeLlama-7b-Instruct-hf",
            output_dir=output_dir
        )
        
        # CodeLlama specific config
        self.lora_config = LoraConfig(
            r=32,  # Higher rank for code
            lora_alpha=64,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout=0.1,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )
    
    def _tokenize_function(self, examples):
        """CodeLlama specific tokenization"""
        prompts = []
        for prompt, completion in zip(examples["prompt"], examples["completion"]):
            # CodeLlama format
            text = f"""### Instruction:
{prompt}

### Response:
{completion}"""
            prompts.append(text)
        
        model_inputs = self.tokenizer(
            prompts,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        model_inputs["labels"] = model_inputs["input_ids"].clone()
        return model_inputs


def create_swift_training_prompts(scraped_data_dir: str) -> str:
    """Convert scraped data to training prompts"""
    output_file = "swift_training_prompts.jsonl"
    
    with open(output_file, 'w') as out_f:
        # Load scraped data
        data_path = Path(scraped_data_dir)
        
        # Process SwiftUI apps
        for json_file in (data_path / "swiftui_apps").glob("*.json"):
            with open(json_file, 'r') as f:
                data = json.load(f)
                
                # Create variations of prompts
                prompts = [
                    f"Create a SwiftUI app: {data['description']}",
                    f"Build an iOS app called {data['repo']} that {data['description']}",
                    f"Generate Swift code for: {data['description']}"
                ]
                
                for prompt in prompts:
                    out_f.write(json.dumps({
                        "prompt": prompt,
                        "completion": data['content']
                    }) + '\n')
        
        # Process view components
        for json_file in (data_path / "view_components").glob("*.json"):
            with open(json_file, 'r') as f:
                data = json.load(f)
                
                # Extract component info
                content = data['content']
                view_match = re.search(r'struct\s+(\w+)\s*:\s*View', content)
                if view_match:
                    view_name = view_match.group(1)
                    
                    prompts = [
                        f"Create a SwiftUI view component called {view_name}",
                        f"Build a {view_name} view in SwiftUI",
                        f"Generate a SwiftUI component: {view_name}"
                    ]
                    
                    for prompt in prompts:
                        out_f.write(json.dumps({
                            "prompt": prompt,
                            "completion": content
                        }) + '\n')
    
    logger.info(f"Created training prompts file: {output_file}")
    return output_file


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Fine-tune Llama for Swift code generation")
    parser.add_argument("--model", choices=["llama", "codellama"], default="codellama",
                       help="Model to fine-tune")
    parser.add_argument("--data", type=str, default="swift_training_data",
                       help="Path to scraped data directory")
    parser.add_argument("--train", action="store_true",
                       help="Run training")
    parser.add_argument("--generate", type=str,
                       help="Generate code with prompt")
    
    args = parser.parse_args()
    
    if args.train:
        # Create training prompts from scraped data
        training_file = create_swift_training_prompts(args.data)
        
        # Initialize fine-tuner
        if args.model == "codellama":
            tuner = CodeLlamaFineTuner()
        else:
            tuner = LlamaFineTuner()
        
        # Train
        tuner.train(training_file)
    
    elif args.generate:
        # Load and generate
        if args.model == "codellama":
            tuner = CodeLlamaFineTuner()
        else:
            tuner = LlamaFineTuner()
        
        code = tuner.generate_swift_code(args.generate)
        print(code)