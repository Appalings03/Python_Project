# train.py — Point d'entrée pour lancer l'entraînement
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from factorio_env import FactorioEnv

def make_env():
    return FactorioEnv()

env = DummyVecEnv([make_env])

model = PPO(
    policy="MultiInputPolicy",   # gère Dict observation (CNN + MLP)
    env=env,
    learning_rate=3e-4,
    n_steps=512,                 # steps par update (faible car lent en temps réel)
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.01,               # coefficient d'entropie : favorise l'exploration
    verbose=1,
    tensorboard_log="./tb_logs/",
    device="auto",               # CUDA si dispo, sinon CPU
)

checkpoint_cb = CheckpointCallback(
    save_freq=5000,
    save_path="./checkpoints/",
    name_prefix="factorio_ppo",
)

model.learn(
    total_timesteps=500_000,
    callback=checkpoint_cb,
    progress_bar=True,
)

model.save("factorio_ppo_final")