import json
import logging
from typing import Optional

from paperagent.models import PaperProject, DistributedLaunchBundle
from paperagent.engine.llm_client import LLMClient

logger = logging.getLogger(__name__)

DISTRIBUTED_LAUNCH_PROMPT = """
You are an expert machine learning systems engineer writing PyTorch distributed training code.
Given the following self-contained PyTorch algorithm implementation, write a multi-GPU distributed launcher bundle.

The bundle must include:
1. `ddp_launcher_script_py`: A Python script using `torch.distributed` (DDP), `DistributedSampler`, and `mp.spawn` or `torchrun` compatibility to train the model across multiple GPUs. It must be self-contained and import standard libraries/torch.
2. `fsdp_config_yaml`: A YAML configuration file specifying Fully Sharded Data Parallel (FSDP) auto-wrap policies, mixed precision settings, and sharding strategies.
3. `slurm_batch_script_sh`: A bash script for submitting this distributed job to a Slurm HPC cluster, including `#SBATCH` directives for nodes, gpus, tasks, and memory.

Original PyTorch Implementation:
```python
{source_code}
```

Provide the result as a JSON object adhering to the specified format. The `ddp_launcher_script_py` must not contain markdown formatting and must be valid Python code. The `fsdp_config_yaml` must be valid YAML.
"""

def _get_fallback_distributed_bundle(world_size: int = 8) -> DistributedLaunchBundle:
    """Returns a realistic mock distributed bundle when the LLM is offline or in mock mode."""
    ddp_script = '''
import os
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.distributed import DistributedSampler

class DummyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net = torch.nn.Linear(10, 10)
    
    def forward(self, x):
        return self.net(x)

class DummyDataset(Dataset):
    def __len__(self):
        return 100
    def __getitem__(self, idx):
        return torch.randn(10), torch.randn(10)

def setup(rank, world_size):
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def cleanup():
    dist.destroy_process_group()

def train(rank, world_size):
    setup(rank, world_size)
    
    dataset = DummyDataset()
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)
    dataloader = DataLoader(dataset, batch_size=8, sampler=sampler)
    
    model = DummyModel().to(rank)
    ddp_model = DDP(model, device_ids=[rank])
    
    optimizer = torch.optim.SGD(ddp_model.parameters(), lr=0.001)
    
    for epoch in range(2):
        sampler.set_epoch(epoch)
        for data, target in dataloader:
            data, target = data.to(rank), target.to(rank)
            optimizer.zero_grad()
            output = ddp_model(data)
            loss = torch.nn.functional.mse_loss(output, target)
            loss.backward()
            optimizer.step()
    
    cleanup()

def main():
    world_size = {world_size}
    if torch.cuda.device_count() < world_size:
        print(f"Warning: Only {torch.cuda.device_count()} GPUs available, but requested {world_size}.")
        world_size = torch.cuda.device_count()
    if world_size > 0:
        mp.spawn(train, args=(world_size,), nprocs=world_size, join=True)
    else:
        print("No GPUs available for DDP testing.")

if __name__ == "__main__":
    main()
'''
    
    fsdp_yaml = '''
fsdp_config:
  sharding_strategy: FULL_SHARD
  mixed_precision:
    param_dtype: bfloat16
    reduce_dtype: bfloat16
    buffer_dtype: bfloat16
  auto_wrap_policy:
    module_classes:
      - Linear
      - Conv2d
  activation_checkpointing: true
  limit_all_gathers: true
'''
    
    slurm_script = '''#!/bin/bash
#SBATCH --job-name=distributed_training
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=8
#SBATCH --mem=256G
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
#SBATCH --partition=gpu

module load cuda/11.8

export MASTER_PORT=12340
export WORLD_SIZE=$(($SLURM_NNODES * $SLURM_NTASKS_PER_NODE))
export MASTER_ADDR=$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)

srun torchrun \
    --nnodes=$SLURM_NNODES \
    --nproc_per_node=$SLURM_NTASKS_PER_NODE \
    --rdzv_id=$SLURM_JOB_ID \
    --rdzv_backend=c10d \
    --rdzv_endpoint=$MASTER_ADDR:$MASTER_PORT \
    ddp_launcher.py
'''
    
    return DistributedLaunchBundle(
        model_name="SynthesizedDistributedModel",
        ddp_launcher_script_py=ddp_script.replace('{world_size}', str(world_size)).strip(),
        fsdp_config_yaml=fsdp_yaml.strip(),
        slurm_batch_script_sh=slurm_script.strip(),
        recommended_world_size=world_size
    )


class DistributedLaunchGenerator:
    """Generates distributed training launchers (DDP, FSDP, Slurm) for PyTorch algorithms."""
    
    def __init__(self, client: Optional[LLMClient] = None):
        self.client = client or LLMClient()

    def generate_distributed_bundle(self, project: PaperProject, world_size: int = 8) -> DistributedLaunchBundle:
        """
        Takes synthesized PyTorch code and generates DDP scripts, FSDP configs, and Slurm scripts.
        """
        if project.synthesis is None or not project.synthesis.target_module_code:
            logger.info("Project missing target_module_code. Using fallback.")
            return _get_fallback_distributed_bundle(world_size=world_size)

        if not self.client.gemini_api_key and not self.client.openai_api_key:
            logger.info("No LLM API keys configured. Using fallback DistributedLaunchBundle.")
            return _get_fallback_distributed_bundle(world_size=world_size)

        prompt = DISTRIBUTED_LAUNCH_PROMPT.format(source_code=project.synthesis.target_module_code)
        
        try:
            result = self.client.generate_structured(
                prompt=prompt,
                response_model=DistributedLaunchBundle
            )
            return result
        except Exception as e:
            logger.error(f"Failed to generate DistributedLaunchBundle via LLM: {e}. Using fallback.")
            return _get_fallback_distributed_bundle(world_size=world_size)