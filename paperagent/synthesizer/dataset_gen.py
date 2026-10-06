import textwrap
from typing import Optional

from paperagent.models import PaperProject, SyntheticDatasetFixture

class SyntheticDatasetGenerator:
    """
    Synthesizes self-contained Python generator code producing realistic toy tensors/inputs.
    Provides PyTorch Dataset and DataLoader classes matching paper dimension specs.
    """

    def generate_dataset_fixture(
        self, project: PaperProject, num_samples: int = 1000
    ) -> SyntheticDatasetFixture:
        """
        Generates fully offline deterministic code synthesis for a synthetic dataset fixture.

        Args:
            project: The paper project to generate the dataset for.
            num_samples: Number of samples in the synthetic dataset.

        Returns:
            SyntheticDatasetFixture containing the generator code and sample batch summary.
        """
        # Determine dataset name from project or use default
        dataset_name = f"Synthetic{project.id.capitalize()}Dataset" if project and project.id else "SyntheticDataset"
        
        # Hardcoded realistic tensor dimensions (batch_size, sequence_length, embedding_dim)
        batch_size = 32
        seq_length = 128
        embed_dim = 256

        generator_code = textwrap.dedent(
            f'''\
            import torch
            from torch.utils.data import Dataset, DataLoader

            class {dataset_name}(Dataset):
                """Synthetic dataset generated for {dataset_name}."""
                def __init__(self, num_samples: int = {num_samples}):
                    self.num_samples = num_samples
                    # Deterministic generation for reproducibility
                    torch.manual_seed(42)
                    
                    # Generate realistic toy tensors matching typical dimensions
                    # E.g. input shape: (sequence_length, embedding_dim)
                    self.inputs = torch.randn(num_samples, {seq_length}, {embed_dim})
                    
                    # Generate targets / masks
                    self.targets = torch.randint(0, 2, (num_samples,))

                def __len__(self) -> int:
                    return self.num_samples

                def __getitem__(self, idx: int):
                    return self.inputs[idx], self.targets[idx]

            def get_dataloader(batch_size: int = {batch_size}) -> DataLoader:
                """Returns a DataLoader for {dataset_name}."""
                dataset = {dataset_name}()
                return DataLoader(dataset, batch_size=batch_size, shuffle=True)
            '''
        )

        sample_batch_summary = (
            f"Dataset: {dataset_name}\n"
            f"Samples: {num_samples}\n"
            f"Input Shape: [batch_size, {seq_length}, {embed_dim}]\n"
            f"Target Shape: [batch_size]\n"
        )

        return SyntheticDatasetFixture(
            dataset_name=dataset_name,
            generator_code=generator_code,
            sample_batch_summary=sample_batch_summary,
            num_samples=num_samples,
        )