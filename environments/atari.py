# atari.py
# Dylan Peifer
# 18 Feb 2019
"""A wrapper for Atari environments from OpenAI gym."""

from collections import deque
import gym
import numpy as np


class AtariEnv:

    def __init__(self, game, no_op_max=30, reset_on_death=True):
        self.game = game
        self.env = gym.make(game)
        self.action_size = self.env.action_space.n
        self.no_op_max = no_op_max
        self.history = None
        self.lives = 0
        self.reset_on_death = reset_on_death

    def reset(self):
        if self.lives == 0:
            state = self.env.reset()
            self.lives = self.env.unwrapped.ale.lives()
            done = False
        else:
            state, _, done, _ = self.env.step(0)

        frame = np.mean(state[::2, ::2], axis=2).astype(np.uint8)
        self.history = deque([frame] * 4)
        state = np.stack(self.history, axis=-1)

        no_ops = np.random.randint(self.no_op_max)
        for _ in range(no_ops):
            state, _, done, _ = self.step(0)
            if done:
                break

        return state if not done else self.reset()

    def step(self, action):
        state, reward, done, info = self.env.step(action)

        if info['ale.lives'] < self.lives and self.reset_on_death:
            done = True
            self.lives = info['ale.lives']

        frame = np.mean(state[::2, ::2], axis=2).astype(np.uint8)
        self.history.pop()
        self.history.appendleft(frame)

        return np.stack(self.history, axis=-1), np.sign(reward), done, info

    def render(self):
        self.env.render()

    def close(self):
        self.env.close()