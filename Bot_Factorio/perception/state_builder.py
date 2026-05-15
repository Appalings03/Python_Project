# perception/state_builder.py
import numpy as np
from dataclasses import dataclass, field

@dataclass
class FactorioState:
    """
    Représentation structurée de l'état du jeu à un instant t.
    Sert de pont entre la perception brute et l'observation Gym.
    """
    # Ressources en inventaire (normalisées par un max raisonnable)
    iron_ore:     float = 0.0
    copper_ore:   float = 0.0
    coal:         float = 0.0
    stone:        float = 0.0
    iron_plate:   float = 0.0
    copper_plate: float = 0.0

    # Progression
    buildings_placed: float = 0.0   # compteur normalisé
    tech_progress:    float = 0.0   # 0.0 → 1.0

    # Danger
    health_ratio:     float = 1.0   # 0.0 (mort) → 1.0 (pleine santé)

    # Contexte spatial (position normalisée sur la minimap)
    pos_x: float = 0.5
    pos_y: float = 0.5

    def to_vector(self) -> np.ndarray:
        """Convertit en vecteur numpy normalisé pour le réseau."""
        MAX_RESOURCES = 500.0  # normalisation
        return np.array([
            self.iron_ore     / MAX_RESOURCES,
            self.copper_ore   / MAX_RESOURCES,
            self.coal         / MAX_RESOURCES,
            self.stone        / MAX_RESOURCES,
            self.iron_plate   / MAX_RESOURCES,
            self.copper_plate / MAX_RESOURCES,
            self.buildings_placed / 50.0,
            self.tech_progress,
            self.health_ratio,
            self.pos_x,
            self.pos_y,
        ], dtype=np.float32)

    @property
    def dim(self) -> int:
        return 11  # à synchroniser avec STATE_DIM dans factorio_env.py