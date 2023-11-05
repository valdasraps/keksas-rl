import gymnasium as gym
import numpy as np
from gymnasium import spaces

from dataset import Dataset


class KeksasEnv(gym.Env):

    def __init__(self, dataset: Dataset) -> None:
        self._dataset = dataset
        super(KeksasEnv, self).__init__()

        self.action_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)
        self.observation_space = spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32)

    def step(self, action):

        return observation, self.reward, self.done, info

    def reset(self):

        return observation