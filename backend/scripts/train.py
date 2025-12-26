"""
Training Script
Fine-tune Phi-3 model on prepared study material data
"""

import sys
import os
import argparse
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.fine_tune import Phi3FineTuner, FineTuningConfig, run_fine_tuning
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Fine-tune Phi-3 model for AI Study Buddy"
    )
    
    parser.add_argument(
        "--data-path",
        type=str,
        default=os.path.join(settings.training_data_dir, "training_data.json"),
        help="Path to training data JSON file"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=settings.model_path,
        help="Directory to save fine-tuned model"
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Training batch size"
    )
    
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-4,
        help="Learning rate"
    )
    
    parser.add_argument(
        "--lora-r",
        type=int,
        default=16,
        help="LoRA rank"
    )
    
    parser.add_argument(
        "--lora-alpha",
        type=int,
        default=32,
        help="LoRA alpha scaling factor"
    )
    
    parser.add_argument(
        "--max-seq-length",
        type=int,
        default=2048,
        help="Maximum sequence length"
    )
    
    parser.add_argument(
        "--no-4bit",
        action="store_true",
        help="Disable 4-bit quantization (requires more VRAM)"
    )
    
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge LoRA weights with base model after training"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("AI Study Buddy - Phi-3 Fine-Tuning")
    logger.info("=" * 60)
    
    # Check if training data exists
    if not os.path.exists(args.data_path):
        logger.error(f"Training data not found at: {args.data_path}")
        logger.error("Please run 'python scripts/prepare_data.py' first to generate training data.")
        sys.exit(1)
    
    # Create configuration
    config = FineTuningConfig(
        model_name=settings.model_name,
        output_dir=args.output_dir,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        max_seq_length=args.max_seq_length,
        use_4bit=not args.no_4bit
    )
    
    logger.info("\nTraining Configuration:")
    logger.info(f"  Model: {config.model_name}")
    logger.info(f"  Data: {args.data_path}")
    logger.info(f"  Output: {config.output_dir}")
    logger.info(f"  Epochs: {config.num_epochs}")
    logger.info(f"  Batch size: {config.batch_size}")
    logger.info(f"  Learning rate: {config.learning_rate}")
    logger.info(f"  LoRA rank: {config.lora_r}")
    logger.info(f"  LoRA alpha: {config.lora_alpha}")
    logger.info(f"  Max seq length: {config.max_seq_length}")
    logger.info(f"  4-bit quantization: {config.use_4bit}")
    
    # Check GPU availability
    import torch
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        logger.info(f"\nGPU detected: {gpu_name} ({gpu_memory:.1f} GB)")
    else:
        logger.warning("\nNo GPU detected! Training will be very slow on CPU.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    logger.info("\n" + "=" * 60)
    logger.info("Starting Fine-Tuning")
    logger.info("=" * 60 + "\n")
    
    # Initialize tuner
    tuner = Phi3FineTuner(config)
    
    # Load data
    dataset = tuner.load_training_data(args.data_path)
    
    # Split data
    split = dataset.train_test_split(test_size=0.1, seed=config.seed)
    train_dataset = split["train"]
    eval_dataset = split["test"]
    
    logger.info(f"Training samples: {len(train_dataset)}")
    logger.info(f"Evaluation samples: {len(eval_dataset)}")
    
    # Setup model
    logger.info("\nLoading and configuring model...")
    tuner.setup_model()
    
    # Train
    logger.info("\nStarting training...\n")
    tuner.train(train_dataset, eval_dataset)
    
    # Save
    logger.info("\nSaving model...")
    tuner.save_model()
    
    # Optionally merge weights
    if args.merge:
        merged_path = os.path.join(args.output_dir, "merged")
        logger.info(f"\nMerging LoRA weights to: {merged_path}")
        tuner.merge_and_save(merged_path)
    
    logger.info("\n" + "=" * 60)
    logger.info("Fine-Tuning Complete!")
    logger.info("=" * 60)
    logger.info(f"\nModel saved to: {config.output_dir}")
    logger.info("\nTo use the fine-tuned model, update MODEL_PATH in .env:")
    logger.info(f"  MODEL_PATH={config.output_dir}")


if __name__ == "__main__":
    main()
