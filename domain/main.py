from dataset import Dataset
from env import KeksasEnv
from stable_baselines3.common.env_checker import check_env

dataset = Dataset(csv_file='data/binance_BTCUSDT_1m_2023-05-01_2023-06-01.csv', ema_lengths=[5, 20, 50])

env = KeksasEnv(dataset=dataset)
check_env(env, warn=True)
