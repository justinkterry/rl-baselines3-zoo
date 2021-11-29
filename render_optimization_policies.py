import os
from os.path import exists
import numpy as np
import supersuit as ss
from array2gif import write_gif
from pettingzoo.butterfly import cooperative_pong_v3
from stable_baselines3 import PPO

n_agents = 2

env = cooperative_pong_v3.parallel_env()
player1 = env.possible_agents[0]


def invert_agent_indication(obs, agent):
    if len(obs.shape) == 2:
        obs = obs.reshape(obs.shape + (1,))
    obs2 = obs if agent == player1 else 255 - obs
    return np.concatenate([obs, obs2], axis=2)


env = cooperative_pong_v3.env()
env = ss.color_reduction_v0(env, mode="B")
env = ss.resize_v0(env, x_size=84, y_size=84)
env = ss.observation_lambda_v0(env, invert_agent_indication)
env = ss.frame_stack_v1(env, 3)

policies = os.listdir("./optimization_policies/")

for policy in policies:
    filepath = "./optimization_policies/" + policy + "/best_model"
    if not exists(filepath + '.zip'):
        continue
    print("Loading new policy ", filepath)
    model = PPO.load(filepath)

    obs_list = []
    i = 0
    env.reset()
    reward = 0

    try:
        while True:
            for agent in env.agent_iter():
                observation, reward, done, _ = env.last()
                action = (model.predict(observation, deterministic=False)[0] if not done else None)
                reward += reward

                env.step(action)
                i += 1
                if i % (len(env.possible_agents) + 1) == 0:
                    obs_list.append(
                        np.transpose(env.render(mode="rgb_array"), axes=(1, 0, 2))
                    )

            break

        reward = reward / n_agents
        print("writing gif")
        write_gif(
            obs_list, "./optimization_gifs/" + policy + "_" + str(reward)[:5] + ".gif", fps=15
        )
    except:
        print("error")
