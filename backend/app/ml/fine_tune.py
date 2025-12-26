"""
Phi-3 Fine-Tuning Module
LoRA/QLoRA fine-tuning for microsoft/Phi-3-mini-4k-instruct
"""

import os
import json
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass, field

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType
)
from datasets import Dataset, load_dataset

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class FineTuningConfig:
    """Configuration for fine-tuning"""
    
    # Model
    model_name: str = "microsoft/Phi-3-mini-4k-instruct"
    output_dir: str = "./models/phi3-finetuned"
    
    # LoRA Configuration
    lora_r: int = 16  # LoRA rank
    lora_alpha: int = 32  # LoRA alpha scaling
    lora_dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])
    
    # Training
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.03
    max_seq_length: int = 2048
    
    # Quantization
    use_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_quant_type: str = "nf4"
    use_double_quant: bool = True
    
    # Misc
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 100
    seed: int = 42


class Phi3FineTuner:
    """
    Fine-tuning pipeline for Phi-3 model using LoRA/QLoRA.
    """
    
    def __init__(self, config: Optional[FineTuningConfig] = None):
        self.config = config or FineTuningConfig()
        self.model = None
        self.tokenizer = None
        self.trainer = None
    
    def load_training_data(self, data_path: Optional[str] = None) -> Dataset:
        """
        Load and prepare training data.
        
        Args:
            data_path: Path to JSON training data file
            
        Returns:
            HuggingFace Dataset
        """
        data_path = data_path or os.path.join(
            settings.training_data_dir, 
            "training_data.json"
        )
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(
                f"Training data not found at {data_path}. "
                "Run PDF processor first to generate training data."
            )
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data)} training examples")
        
        # Format for Phi-3 instruction format
        formatted_data = []
        for item in data:
            text = self._format_training_example(
                instruction=item.get("instruction", ""),
                context=item.get("context", ""),
                response=item.get("response", "")
            )
            formatted_data.append({"text": text})
        
        return Dataset.from_list(formatted_data)
    
    def _format_training_example(
        self,
        instruction: str,
        context: str,
        response: str
    ) -> str:
        """Format a single training example in Phi-3 chat format"""
        
        system_msg = "You are an intelligent AI Study Buddy, an educational assistant. Provide clear, accurate, and helpful explanations."
        
        if context:
            user_msg = f"Context: {context}\n\nQuestion: {instruction}"
        else:
            user_msg = instruction
        
        return f"""<|system|>
{system_msg}<|end|>
<|user|>
{user_msg}<|end|>
<|assistant|>
{response}<|end|>"""
    
    def setup_model(self):
        """Initialize model with quantization and LoRA"""
        
        logger.info(f"Loading model: {self.config.model_name}")
        
        # Quantization config for memory efficiency
        if self.config.use_4bit:
            compute_dtype = getattr(torch, self.config.bnb_4bit_compute_dtype)
            
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=compute_dtype,
                bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=self.config.use_double_quant
            )
        else:
            bnb_config = None
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Prepare for k-bit training
        if self.config.use_4bit:
            self.model = prepare_model_for_kbit_training(self.model)
        
        # Configure LoRA
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.target_modules,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )
        
        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)
        
        # Print trainable parameters
        trainable_params = sum(
            p.numel() for p in self.model.parameters() if p.requires_grad
        )
        total_params = sum(p.numel() for p in self.model.parameters())
        
        logger.info(
            f"Trainable params: {trainable_params:,} || "
            f"Total params: {total_params:,} || "
            f"Trainable%: {100 * trainable_params / total_params:.2f}%"
        )
    
    def tokenize_dataset(self, dataset: Dataset) -> Dataset:
        """Tokenize the dataset"""
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=self.config.max_seq_length,
                padding="max_length"
            )
        
        tokenized = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
            desc="Tokenizing"
        )
        
        return tokenized
    
    def train(
        self,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None
    ):
        """
        Run the fine-tuning process.
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Optional evaluation dataset
        """
        
        if self.model is None:
            self.setup_model()
        
        # Tokenize datasets
        train_tokenized = self.tokenize_dataset(train_dataset)
        eval_tokenized = self.tokenize_dataset(eval_dataset) if eval_dataset else None
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            warmup_ratio=self.config.warmup_ratio,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps if eval_tokenized else None,
            evaluation_strategy="steps" if eval_tokenized else "no",
            save_total_limit=3,
            load_best_model_at_end=True if eval_tokenized else False,
            fp16=True,
            optim="paged_adamw_8bit",
            seed=self.config.seed,
            report_to="none"  # Disable wandb/tensorboard
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Initialize trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_tokenized,
            eval_dataset=eval_tokenized,
            data_collator=data_collator
        )
        
        logger.info("Starting fine-tuning...")
        
        # Train
        self.trainer.train()
        
        logger.info("Fine-tuning completed!")
    
    def save_model(self, output_path: Optional[str] = None):
        """Save the fine-tuned model"""
        
        output_path = output_path or self.config.output_dir
        
        logger.info(f"Saving model to {output_path}")
        
        # Save LoRA adapters
        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        
        # Save config
        config_path = os.path.join(output_path, "training_config.json")
        with open(config_path, 'w') as f:
            json.dump({
                "model_name": self.config.model_name,
                "lora_r": self.config.lora_r,
                "lora_alpha": self.config.lora_alpha,
                "num_epochs": self.config.num_epochs,
                "learning_rate": self.config.learning_rate
            }, f, indent=2)
        
        logger.info("Model saved successfully")
    
    def merge_and_save(self, output_path: str):
        """
        Merge LoRA weights with base model and save.
        Creates a standalone model without needing PEFT at inference.
        """
        
        logger.info("Merging LoRA weights with base model...")
        
        # Merge weights
        merged_model = self.model.merge_and_unload()
        
        # Save merged model
        merged_model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        
        logger.info(f"Merged model saved to {output_path}")


def run_fine_tuning(
    data_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    config: Optional[FineTuningConfig] = None
) -> Dict:
    """
    Convenience function to run the full fine-tuning pipeline.
    
    Args:
        data_path: Path to training data JSON
        output_dir: Output directory for fine-tuned model
        config: Optional fine-tuning configuration
        
    Returns:
        Dictionary with training results
    """
    config = config or FineTuningConfig()
    
    if output_dir:
        config.output_dir = output_dir
    
    tuner = Phi3FineTuner(config)
    
    # Load data
    dataset = tuner.load_training_data(data_path)
    
    # Split into train/eval
    split = dataset.train_test_split(test_size=0.1, seed=config.seed)
    train_dataset = split["train"]
    eval_dataset = split["test"]
    
    logger.info(f"Train samples: {len(train_dataset)}, Eval samples: {len(eval_dataset)}")
    
    # Setup and train
    tuner.setup_model()
    tuner.train(train_dataset, eval_dataset)
    
    # Save
    tuner.save_model()
    
    return {
        "status": "completed",
        "train_samples": len(train_dataset),
        "eval_samples": len(eval_dataset),
        "output_dir": config.output_dir
    }
