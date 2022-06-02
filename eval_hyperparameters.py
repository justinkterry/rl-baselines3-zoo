import json
import sys

import fle.flocking_env as flocking_env
import supersuit as ss
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.vec_env import VecMonitor
from torch import nn as nn

num = sys.argv[1]

n_evaluations = 20
n_agents = 9
n_envs = 4
total_energy_j = 24164
total_distance_m = 894
hz = 500
crash_reward = -10
episodes = 12000
nerve_impulse_hz = 200
reaction_frames = 0
n_timesteps = hz * n_agents * episodes  # real number is skip frames times larger
distance_reward_per_m = 100 / total_distance_m
energy_reward_per_j = -10 / total_energy_j
skip_frames = int(hz / nerve_impulse_hz)

with open("./hyperparameter_jsons/" + "hyperparameters_" + num + ".json") as f:
    params = json.load(f)

print(params)

net_arch = {
    "small": [dict(pi=[64, 64], vf=[64, 64])],
    "medium": [dict(pi=[256, 256], vf=[256, 256])],
    "large": [dict(pi=[400, 300], vf=[400, 300])],
    "extra_large": [dict(pi=[750, 750, 500], vf=[750, 750, 500])],
}[params["net_arch"]]
activation_fn = {
    "tanh": nn.Tanh,
    "relu": nn.ReLU,
    "elu": nn.ELU,
    "leaky_relu": nn.LeakyReLU,
}[params["activation_fn"]]
ortho_init = params["ortho_init"]

params["policy_kwargs"] = dict(net_arch=net_arch, activation_fn=activation_fn, ortho_init=ortho_init)

del params["net_arch"]
del params["activation_fn"]
del params["ortho_init"]

env = flocking_env.parallel_env(
    N=n_agents,
    h=1 / hz,
    energy_reward=energy_reward_per_j,
    forward_reward=distance_reward_per_m,
    crash_reward=crash_reward,
    LIA=True,
)
env = ss.delay_observations_v0(env, reaction_frames)
env = ss.frame_skip_v0(env, skip_frames)
env = ss.frame_stack_v1(env, 4)
env = ss.pettingzoo_env_to_vec_env_v1(env)
env = ss.concat_vec_envs_v1(env, n_envs, num_cpus=1, base_class="stable_baselines3")
env = VecMonitor(env)

eval_env = flocking_env.parallel_env(
    N=n_agents,
    h=1 / hz,
    energy_reward=energy_reward_per_j,
    forward_reward=distance_reward_per_m,
    crash_reward=crash_reward,
    LIA=True,
)
eval_env = ss.delay_observations_v0(eval_env, reaction_frames)
eval_env = ss.frame_skip_v0(eval_env, skip_frames)
eval_env = ss.frame_stack_v1(eval_env, 4)
eval_env = ss.pettingzoo_env_to_vec_env_v1(eval_env)
eval_env = ss.concat_vec_envs_v1(eval_env, 1, num_cpus=1, base_class="stable_baselines3")
eval_env = VecMonitor(eval_env)

eval_freq = int(n_timesteps / n_evaluations)
eval_freq = max(eval_freq // (n_envs * n_agents), 1)


all_mean_rewards = []
for i in range(10):
    try:
        model = PPO("MlpPolicy", env, verbose=3, **params)
        eval_callback = EvalCallback(
            eval_env,
            best_model_save_path="./eval_logs/" + num + "/" + str(i) + "/",
            log_path="./eval_logs/" + num + "/" + str(i) + "/",
            eval_freq=eval_freq,
            deterministic=True,
            render=False,
        )
        model.learn(total_timesteps=n_timesteps, callback=eval_callback)
        model = PPO.load("./eval_logs/" + num + "/" + str(i) + "/" + "best_model")
        mean_reward, std_reward = evaluate_policy(model, eval_env, deterministic=True, n_eval_episodes=25)
        print(mean_reward)
        print(std_reward)
        all_mean_rewards.append(mean_reward)
        if mean_reward > 50:
            model.save("./mature_policies/" + str(num) + "/" + str(i) + "_" + str(mean_reward).split(".")[0] + ".zip")
    except:
        print("error")

if len(all_mean_rewards) > 0:
    print(sum(all_mean_rewards) / len(all_mean_rewards))
else:
    print("No mature policies found")
