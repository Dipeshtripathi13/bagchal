import torch
import numpy as np
from env.bagchal_env import BagchalEnv
from agents.dqn_agent import DQNAgent

def evaluate(model_path, episodes=10):
    env = BagchalEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = np.prod(env.action_space.nvec)
    agent = DQNAgent(state_dim, action_dim)

    # Load the trained model
    agent.model.load_state_dict(torch.load(model_path, map_location=agent.device))
    agent.model.eval()

    print(f"Evaluating model from {model_path} for {episodes} episodes...\n")

    for ep in range(episodes):
        state = env.reset()
        done = False
        total_reward = 0
        step = 0

        while not done:
            action = agent.select_action(state)  # uses epsilon=1.0 by default
            from_pos = action // 25
            to_pos = action % 25
            next_state, reward, done, _ = env.step((from_pos, to_pos))
            state = next_state
            total_reward += reward
            step += 1

        print(f"Episode {ep+1}: Total Reward = {total_reward}, Steps = {step}")

if __name__ == "__main__":
    evaluate("checkpoint_episode_100.pth", episodes=10)
