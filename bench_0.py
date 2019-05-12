import numpy as np
import sympy as sp

from agents.pg import PGAgent
from agents.networks import ParallelMultilayerPerceptron
from environments.buchberger import BuchbergerEnv, LeadMonomialsWrapper
from environments.ideals import random_binomial_ideal

R = sp.ring('x,y,z', sp.FF(32003), 'grevlex')[0]
f = lambda R: random_binomial_ideal(R, 2, 5, homogeneous=True)
env = LeadMonomialsWrapper(BuchbergerEnv(f, ring=R, elimination='none'))
policy = ParallelMultilayerPerceptron(6, [24])
agent = PGAgent(policy, policy_learning_rate=0.0001, gam=1.0, lam=1.0)

r = agent.train(env, 1000, epochs=3, verbose=1)

print(np.mean(r))