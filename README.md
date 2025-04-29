# Bagchal RL

A Reinforcement Learning implementation of the traditional Nepalese Bagchal (Tiger & Goat) game using OpenAI Gym and PyTorch DQN agents.

## Structure

- `env/bagchal_env.py`: Custom Gym environment  
- `agents/`: DQN agent and utilities  
- `train.py`: Training loop with checkpoints  
- `evaluate.py`: Evaluate win rates over multiple episodes  
- `ui.py`: Optional Pygame-based visualization  

## Requirements

```bash
pip install gym numpy torch pygame
