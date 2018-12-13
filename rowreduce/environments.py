# environments.py
# Dylan Peifer
# 10 May 2018
"""Several environments for reinforcement learning in computer algebra.

The structure of Q-learning involves an agent and an environment. The agent
gives the environment actions and gets from the environment states, rewards,
and if the current episode is done. The classes in this file are environments
that implement methods reset() and step(action).
"""

import numpy as np


class RowEchelonEnvironment:
    """A simple environment for matrix row reduction. Agents can add or swap
    rows, and the environment is done when the matrix is in row echelon form.
    """

    def __init__(self, shape, modulus):
        self.N = shape[0]
        self.M = shape[1]
        self.F = modulus
        self.matrix = np.zeros((self.N, self.M))
        self.action_tuples = [('swap', i, j) for i in range(self.N) for j in range(i)] \
            + [('add', i, j) for i in range(self.N) for j in range(self.N) if i != j]
        self.action_size = len(self.action_tuples)

    def reset(self):
        """Reset the state of the environment to a matrix that is not row
        reduced.
        """
        self.matrix = self._random_matrix()
        while self._is_row_echelon():
            self.matrix = self._random_matrix()
        return np.copy(self.matrix)

    def step(self, action):
        """Perform a step from current state using action."""
        action = self.action_tuples[action]
        if action[0] == 'add':
            self._add_rows(action[1:])
        else:
            self._swap_rows(action[1:])
        return np.copy(self.matrix), -1, self._is_row_echelon()

    def _add_rows(self, pair):
        """Add the rows given by pair."""
        self.matrix[pair[1], :] = (self.matrix[pair[1], :] + self.matrix[pair[0], :]) % self.F

    def _swap_rows(self, pair):
        """Swap the rows given by pair."""
        self.matrix[pair, :] = self.matrix[(pair[1], pair[0]), :]

    def _is_row_echelon(self):
        """Return true if the matrix is in row echelon form."""
        prev_lead = -1
        for row in range(self.N):
            next_lead = next((i for i, x in enumerate(self.matrix[row,:]) if x != 0), None)
            if next_lead is not None:
                if prev_lead is None or prev_lead >= next_lead:
                    return False
            prev_lead = next_lead
        return True

    def _random_matrix(self):
        """Return a new random matrix."""
        return np.random.randint(self.F, size=(self.N, self.M))


class RowChoiceEnvironment:
    """An environment for matrix row reduction over F2. Agents choose a row
    to use, and this row is then used as a pivot.
    """

    def __init__(self, shape, density):
        self.N = shape[0]
        self.M = shape[1]
        self.density = density
        self.matrix = np.zeros((self.N, self.M))
        self.action_size = self.N

    def reset(self):
        """Reset the state of the environment to a matrix that is not
        reduced.
        """
        self.matrix = self._random_matrix()
        while self._is_reduced():
            self.matrix = self._random_matrix()
        return np.copy(self.matrix)

    def step(self, action):
        """Perform a step from current state using action."""
        lead = next((i for i, x in enumerate(self.matrix[action, :]) if x != 0), None)
        if lead is None:
            return (np.copy(self.matrix),
                    -100,
                    self._is_reduced())
        moves = 0
        for i in range(self.N):
            if i != action and self.matrix[i, lead] != 0:
                self.matrix[i, :] = (self.matrix[i, :] + self.matrix[action, :]) % 2
                moves += 1
        if moves == 0:
            return (np.copy(self.matrix),
                    -100,
                    self._is_reduced())
        else:
            return (np.copy(self.matrix),
                    -moves,
                    self._is_reduced())

    def _is_reduced(self):
        """Return true if the current matrix is reduced."""
        for row in range(self.N):
            # find index of lead term in this row
            lead = next((i for i, x in enumerate(self.matrix[row, :]) if x != 0), None)
            # if this row has lead then everything in lead's column must be 0
            if lead is not None:
                for i in range(self.N):
                    if i != row and self.matrix[i, lead] != 0:
                        return False
        return True

    def _random_matrix(self):
        """Return a new random matrix."""
        return 1 * (np.random.rand(self.N, self.M) > (1 - self.density))


class RowChoiceEnvironmentExtra:
    """An environment for matrix row reduction over F2. Agents choose a row
    to use, and this row is then used as a pivot. The environment also returns
    an additional column vector that stores which rows have not been used.
    """

    def __init__(self, shape, density):
        self.N = shape[0]
        self.M = shape[1]
        self.density = density
        self.matrix = np.zeros((self.N, self.M))
        self.rows = np.ones(self.N)
        self.action_size = self.N

    def reset(self):
        """Reset the state of the environment to a matrix that is not
        reduced.
        """
        self.matrix = self._random_matrix()
        while self._is_reduced():
            self.matrix = self._random_matrix()
        self.rows = np.ones((self.N, 1))
        return np.copy(self.rows), np.copy(self.matrix)

    def step(self, action):
        """Perform a step from current state using action."""
        is_new = self.rows[action, 0]  # is 1 if row has not been used
        self.rows[action] = 0
        lead = next((i for i, x in enumerate(self.matrix[action, :]) if x != 0), None)
        if lead is None:
            return ((np.copy(self.rows), np.copy(self.matrix)),
                    1000 * (is_new - 1),
                    self._is_reduced())
        moves = 0
        for i in range(self.N):
            if i != action and self.matrix[i, lead] != 0:
                self.matrix[i, :] = (self.matrix[i, :] + self.matrix[action, :]) % 2
                moves += 1
        if moves == 0:
            return ((np.copy(self.rows), np.copy(self.matrix)),
                    1000 * (is_new - 1),
                    self._is_reduced())
        else:
            return ((np.copy(self.rows), np.copy(self.matrix)),
                    - moves,
                    self._is_reduced())

    def _is_reduced(self):
        """Return true if the current matrix is reduced."""
        for row in range(self.N):
            # find index of lead term in this row
            lead = next((i for i, x in enumerate(self.matrix[row, :]) if x != 0), None)
            # if this row has lead term then zero everything else in column
            if lead is not None:
                for i in range(self.N):
                    if i != row and self.matrix[i, lead] != 0:
                        return False
        return True

    def _random_matrix(self):
        """Return a new random matrix."""
        return 1.0 * (np.random.rand(self.N, self.M) > (1 - self.density))
