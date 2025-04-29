import gym
import numpy as np
import torch
import torch.nn.functional as F
from agents.dqn_agent import DQNAgent
from env.bagchal_env import BagchalEnv

def train(num_episodes=500):
    env = BagchalEnv()
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.nvec[0] * env.action_space.nvec[1]  # Flattened MultiDiscrete

    agent = DQNAgent(state_dim, action_dim)

    for episode in range(num_episodes):
        state = env.reset()
        done = False
        total_reward = 0

        while not done:
            # Get action from agent
            action = agent.select_action(state)

            # Decode action: flatten index -> (from_pos, to_pos)
            from_idx = action // (env.size ** 2)
            to_idx = action % (env.size ** 2)
            from_pos = (from_idx // env.size, from_idx % env.size)
            to_pos = (to_idx // env.size, to_idx % env.size)

            # Step in environment
            next_state, reward, done, _ = env.step((from_pos, to_pos))
            total_reward += reward

            # Store in replay memory
            agent.store_transition(state, action, reward, next_state, done)

            # Train the agent
            agent.train_step()

            state = next_state

        print(f"Episode {episode + 1}, Total Reward: {total_reward}")

        # Optional: save model every N episodes
        if (episode + 1) % 100 == 0:
            agent.save(f"checkpoint_episode_{episode+1}.pth")

    print("Training completed.")

if __name__ == "__main__":
    train()
