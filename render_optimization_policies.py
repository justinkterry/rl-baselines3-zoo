import os
from os.path import exists

import numpy as np
import pettingzoo.butterfly.pistonball_v5 as pistonball_v5
import supersuit as ss
from array2gif import write_gif
from stable_baselines3 import PPO

n_agents = 20

env = pistonball_v5.env()
env = ss.color_reduction_v0(env, mode="B")
env = ss.resize_v0(env, x_size=84, y_size=84)
env = ss.frame_stack_v1(env, 3)

policies = os.listdir("./optimization_policies/")

for policy in policies:
    filepath = "./optimization_policies/" + policy + "/best_model"
    if not exists(filepath + ".zip"):
        continue
    print("Loading new policy ", filepath)
    model = PPO.load(filepath)

    obs_list = []
    i = 0
    env.reset()
    total_reward = 0

    try:
        while True:
            for agent in env.agent_iter():
                observation, reward, done, _ = env.last()
                action = (
                    model.predict(observation, deterministic=True)[0]
                    if not done
                    else None
                )
                total_reward += reward

                env.step(action)
                i += 1
                if i % (len(env.possible_agents) + 1) == 0:
                    obs_list.append(
                        np.transpose(env.render(mode="rgb_array"), axes=(1, 0, 2))
                    )

            break

        total_reward = total_reward / n_agents
        print("writing gif")
        write_gif(
            obs_list,
            "./optimization_gifs/" + policy + "_" + str(total_reward)[:5] + ".gif",
            fps=15,
        )
    except:
        print("error")
