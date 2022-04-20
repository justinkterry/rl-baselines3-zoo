source venv/bin/activate
mkdir -p ./optimize_logs
rm -rf optimize_logs/*

mkdir -p ./optimization_policies
rm -rf optimization_policies/*

CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 nohup python3 train.py --algo ppo --env LunarLanderContinuous-v2 -n 54000000 -optimize --optimization-log-path optimization_policies --n-trials 150 --sampler tpe --pruner median --study-name $1 --storage mysql://database:ZrWdchqeNpmbuAXYpy2V@35.194.57.226/kaz7 --verbose 2 &> ./optimize_logs/optimize_0.out &
sleep 3
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 nohup python3 train.py --algo ppo --env LunarLanderContinuous-v2 -n 54000000 -optimize --optimization-log-path optimization_policies --n-trials 150 --sampler tpe --pruner median --study-name $1 --storage mysql://database:ZrWdchqeNpmbuAXYpy2V@35.194.57.226/kaz7 --verbose 2 &> ./optimize_logs/optimize_1.out &
sleep 3
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=1 nohup python3 train.py --algo ppo --env LunarLanderContinuous-v2 -n 54000000 -optimize --optimization-log-path optimization_policies --n-trials 150 --sampler tpe --pruner median --study-name $1 --storage mysql://database:ZrWdchqeNpmbuAXYpy2V@35.194.57.226/kaz7 --verbose 2 &> ./optimize_logs/optimize_2.out &
sleep 3
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=1 nohup python3 train.py --algo ppo --env LunarLanderContinuous-v2 -n 54000000 -optimize --optimization-log-path optimization_policies --n-trials 150 --sampler tpe --pruner median --study-name $1 --storage mysql://database:ZrWdchqeNpmbuAXYpy2V@35.194.57.226/kaz7 --verbose 2 &> ./optimize_logs/optimize_3.out &
sleep 3
