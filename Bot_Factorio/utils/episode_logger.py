# utils/episode_logger.py
import json
import time
from pathlib import Path

class EpisodeLogger:
    """
    Sauvegarde les métriques par épisode pour analyse post-entraînement.
    Complète TensorBoard avec des données spécifiques à Factorio.
    """

    def __init__(self, log_dir: str = "./logs/episodes/"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_episode: dict = {}
        self.episode_id = 0

    def begin_episode(self):
        self.current_episode = {
            "id": self.episode_id,
            "start_time": time.time(),
            "steps": 0,
            "total_reward": 0.0,
            "max_iron": 0,
            "drills_placed": 0,
            "techs_unlocked": 0,
            "cause_of_end": "timeout",
        }

    def log_step(self, reward: float, info: dict, state_vec):
        self.current_episode["steps"] += 1
        self.current_episode["total_reward"] += reward
        self.current_episode["max_iron"] = max(
            self.current_episode["max_iron"],
            int(state_vec[0] * 500)
        )
        if info.get("building_placed"):
            self.current_episode["drills_placed"] += 1
        if info.get("death"):
            self.current_episode["cause_of_end"] = "death"

    def end_episode(self):
        self.current_episode["duration_s"] = (
            time.time() - self.current_episode["start_time"]
        )
        path = self.log_dir / f"episode_{self.episode_id:05d}.json"
        with open(path, "w") as f:
            json.dump(self.current_episode, f, indent=2)
        self.episode_id += 1
        return self.current_episode.copy()