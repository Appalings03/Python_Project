# training/curriculum.py
from enum import IntEnum
from dataclasses import dataclass

class Milestone(IntEnum):
    """Jalons de progression, du plus simple au plus complexe."""
    SURVIVE_60S        = 0   # rester en vie 60 secondes
    COLLECT_IRON       = 1   # accumuler 50 minerais de fer
    BUILD_FIRST_DRILL  = 2   # poser un burner mining drill
    BUILD_FURNACE      = 3   # poser une stone furnace et produire des plaques
    AUTOMATE_IRON      = 4   # production automatique de plaques de fer
    RESEARCH_FIRST     = 5   # débloquer la première technologie
    BUILD_ASSEMBLER    = 6   # poser un assembler machine
    # ... jusqu'à LAUNCH_ROCKET

@dataclass
class CurriculumManager:
    """
    Ajuste dynamiquement la reward function et l'action space
    selon le jalon courant de l'agent.
    """
    current_milestone: Milestone = Milestone.SURVIVE_60S
    milestone_threshold: int = 3  # épisodes consécutifs réussis pour avancer

    _success_count: int = 0

    def get_reward_weights(self) -> dict:
        """Retourne les poids de reward selon le jalon courant."""
        weights = {
            Milestone.SURVIVE_60S:       {"survival": 1.0, "resources": 0.0},
            Milestone.COLLECT_IRON:      {"survival": 0.5, "resources": 1.0},
            Milestone.BUILD_FIRST_DRILL: {"survival": 0.3, "resources": 0.5, "building": 2.0},
            Milestone.AUTOMATE_IRON:     {"survival": 0.2, "resources": 0.3, "automation": 3.0},
            Milestone.RESEARCH_FIRST:    {"survival": 0.1, "resources": 0.2, "tech": 5.0},
        }
        return weights.get(self.current_milestone, {"survival": 1.0})

    def evaluate_episode(self, episode_info: dict) -> bool:
        """Retourne True si le jalon courant est atteint dans cet épisode."""
        m = self.current_milestone

        if m == Milestone.SURVIVE_60S:
            return episode_info.get("steps", 0) >= 600  # 60s à 10Hz

        elif m == Milestone.COLLECT_IRON:
            return episode_info.get("max_iron", 0) >= 50

        elif m == Milestone.BUILD_FIRST_DRILL:
            return episode_info.get("drills_placed", 0) >= 1

        return False

    def maybe_advance(self, episode_info: dict):
        """Avance au jalon suivant si assez d'épisodes réussis."""
        if self.evaluate_episode(episode_info):
            self._success_count += 1
        else:
            self._success_count = 0

        if self._success_count >= self.milestone_threshold:
            next_m = self.current_milestone + 1
            if next_m <= Milestone.BUILD_ASSEMBLER:
                print(f"[Curriculum] Avancement : {self.current_milestone.name} → {Milestone(next_m).name}")
                self.current_milestone = Milestone(next_m)
                self._success_count = 0