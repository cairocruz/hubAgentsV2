"""
Data loader for Few-Shot Learning examples.
"""
import pandas as pd
import random
from typing import List, Dict
from pathlib import Path


class DataLoader:
    """Loads and manages Few-Shot learning datasets."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize DataLoader.
        
        Args:
            data_dir: Directory containing CSV datasets
        """
        self.data_dir = Path(data_dir)
        self.datasets = {}
        self._load_all_datasets()
    
    def _load_all_datasets(self):
        """Load all 5 datasets into memory."""
        for i in range(1, 6):
            dataset_path = self.data_dir / f"dataset_{i}.csv"
            if dataset_path.exists():
                self.datasets[i] = pd.read_csv(dataset_path)
            else:
                raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    
    def get_few_shot_examples(self, agent_id: int, num_examples: int = 5) -> str:
        """
        Get random Few-Shot examples for a specific agent.
        
        Args:
            agent_id: Agent identifier (1-5)
            num_examples: Number of examples to retrieve
            
        Returns:
            Formatted string with examples
        """
        if agent_id not in self.datasets:
            raise ValueError(f"Invalid agent_id: {agent_id}. Must be 1-5.")
        
        df = self.datasets[agent_id]
        
        # Sample random examples
        if len(df) < num_examples:
            examples = df.to_dict('records')
        else:
            examples = df.sample(n=num_examples).to_dict('records')
        
        # Format examples
        formatted_examples = "=== EXEMPLOS DE CASOS ANTERIORES ===\n\n"
        
        for idx, example in enumerate(examples, 1):
            formatted_examples += f"EXEMPLO {idx}:\n"
            formatted_examples += f"Relato: \"{example['frase']}\"\n"
            formatted_examples += f"Risco: {example['risco']}\n"
            formatted_examples += f"Fator: {example['fator']}\n"
            formatted_examples += f"Taxonomia: {example['taxonomia']}\n"
            formatted_examples += f"Metadata: {example['metadata']}\n"
            formatted_examples += "\n" + "-" * 50 + "\n\n"
        
        return formatted_examples
    
    def get_dataset(self, agent_id: int) -> pd.DataFrame:
        """
        Get full dataset for an agent.
        
        Args:
            agent_id: Agent identifier (1-5)
            
        Returns:
            DataFrame with dataset
        """
        if agent_id not in self.datasets:
            raise ValueError(f"Invalid agent_id: {agent_id}")
        return self.datasets[agent_id].copy()
    
    def get_dataset_stats(self, agent_id: int) -> Dict:
        """
        Get statistics about a dataset.
        
        Args:
            agent_id: Agent identifier (1-5)
            
        Returns:
            Dictionary with statistics
        """
        df = self.get_dataset(agent_id)
        
        return {
            "total_examples": len(df),
            "risk_distribution": df['risco'].value_counts().to_dict(),
            "unique_factors": df['fator'].nunique()
        }
