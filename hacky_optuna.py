import argparse
import json

import optuna


def value_key(a):
    if a.value is None:
        return float("-inf")
    else:
        return a.value

study = optuna.create_study(
    study_name=None,
    storage='mysql://database:ZrWdchqeNpmbuAXYpy2V@35.194.57.226/kaz7',
    load_if_exists=True,
    direction="maximize",
)
values = []
trials = study.trials
trials.sort(key=value_key, reverse=True)

print(str(len(trials)) + '\n')

for trial in trials:
    if len(values) < 5:
        print(trial)
