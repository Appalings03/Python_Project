# factorio_env.py
import time
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import mss
import cv2
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

# ─── Constantes configurables ────────────────────────────────────────────────

SCREEN_REGION = {"top": 0, "left": 0, "width": 1920, "height": 1080}
OBS_SHAPE = (84, 84, 1)          # frame grayscale redimensionnée
STATE_DIM = 8                    # vecteur d'état structuré (ressources, etc.)
STEP_DELAY = 0.1                 # secondes entre chaque action (≈10 Hz max)
MAX_STEPS = 1000                 # durée max d'un épisode

# Actions discrètes : index → signification
ACTION_MAP = {
    0: ("move", "up"),
    1: ("move", "down"),
    2: ("move", "left"),
    3: ("move", "right"),
    4: ("mine", None),           # clic gauche maintenu
    5: ("interact", None),       # clic droit
    6: ("open_inventory", None), # touche E
    7: ("wait", None),           # aucune action (important pour l'exploration)
}

# ─── Module Perception ───────────────────────────────────────────────────────

class PerceptionModule:
    """Capture et prétraite les frames du jeu."""

    def __init__(self):
        self.sct = mss.mss()

    def capture_frame(self) -> np.ndarray:
        """Retourne une frame 84x84 grayscale normalisée [0,1]."""
        raw = self.sct.grab(SCREEN_REGION)
        img = np.array(raw)                          # BGRA HxWx4
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)
        return resized[..., np.newaxis].astype(np.float32) / 255.0

    def extract_state_vector(self, frame_bgr: np.ndarray) -> np.ndarray:
        """
        Extrait un vecteur d'état structuré depuis la frame brute.
        À implémenter progressivement : OCR, template matching, HSV masking.
        Pour le MVP, retourne un vecteur aléatoire en placeholder.
        """
        # TODO : détecter les valeurs de ressources dans l'UI
        # TODO : lire la position sur la minimap
        # TODO : compter les bâtiments visibles
        return np.zeros(STATE_DIM, dtype=np.float32)  # placeholder

# ─── Module Contrôle ─────────────────────────────────────────────────────────

class ActionExecutor:
    """Traduit les actions discrètes en entrées souris/clavier."""

    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

    def execute(self, action_idx: int):
        action_type, param = ACTION_MAP[action_idx]

        if action_type == "move":
            # Simule les touches WASD
            key_map = {"up": "w", "down": "s", "left": "a", "right": "d"}
            key = key_map[param]
            self.keyboard.press(key)
            time.sleep(0.05)
            self.keyboard.release(key)

        elif action_type == "mine":
            # Clic gauche maintenu brièvement (minage)
            self.mouse.press(Button.left)
            time.sleep(0.15)
            self.mouse.release(Button.left)

        elif action_type == "interact":
            self.mouse.click(Button.right, 1)

        elif action_type == "open_inventory":
            self.keyboard.press("e")
            time.sleep(0.05)
            self.keyboard.release("e")

        elif action_type == "wait":
            time.sleep(STEP_DELAY)  # inaction explicite

# ─── Reward Function ─────────────────────────────────────────────────────────

class RewardFunction:
    """
    Design progressif sparse → dense.
    Phase 1 : rewards denses simples pour amorcer l'apprentissage.
    Phase 2+ : ajouter paliers tech tree, pénalités de blocage.
    """

    def __init__(self):
        self.prev_resources = np.zeros(STATE_DIM, dtype=np.float32)
        self.steps_without_progress = 0
        self.STAGNATION_THRESHOLD = 60

    def compute(
        self,
        state_vec: np.ndarray,
        done: bool,
        info: dict,
    ) -> float:
        reward = 0.0

        # ── Rewards positifs ────────────────────────────────────────
        resource_delta = state_vec - self.prev_resources
        reward += np.sum(np.clip(resource_delta, 0, None)) * 0.1  # collecte

        if info.get("building_placed", False):
            reward += 5.0   # bâtiment posé

        if info.get("tech_unlocked", False):
            reward += 20.0  # technologie débloquée

        # ── Pénalités ───────────────────────────────────────────────
        if done and info.get("death", False):
            reward -= 10.0

        if np.allclose(resource_delta, 0):
            self.steps_without_progress += 1
        else:
            self.steps_without_progress = 0

        if self.steps_without_progress > self.STAGNATION_THRESHOLD:
            reward -= 0.1   # pénalité d'inaction progressive

        self.prev_resources = state_vec.copy()
        return float(reward)

    def reset(self):
        self.prev_resources = np.zeros(STATE_DIM, dtype=np.float32)
        self.steps_without_progress = 0

# ─── Environnement Gym ───────────────────────────────────────────────────────

class FactorioEnv(gym.Env):
    """
    Environnement Gymnasium custom pour Factorio.
    Compatible Stable-Baselines3 (MultiInputPolicy pour Dict observation).
    """

    metadata = {"render_modes": ["rgb_array"]}

    def __init__(self):
        super().__init__()

        self.perception = PerceptionModule()
        self.executor = ActionExecutor()
        self.reward_fn = RewardFunction()

        # Observation : frame CNN + vecteur structuré MLP
        self.observation_space = spaces.Dict({
            "frame": spaces.Box(
                low=0.0, high=1.0,
                shape=OBS_SHAPE,          # (84, 84, 1)
                dtype=np.float32,
            ),
            "state_vec": spaces.Box(
                low=-np.inf, high=np.inf,
                shape=(STATE_DIM,),
                dtype=np.float32,
            ),
        })

        # Action space discret — à étendre progressivement
        self.action_space = spaces.Discrete(len(ACTION_MAP))

        self.step_count = 0
        self._last_frame_bgr = None

    # ── Helpers internes ─────────────────────────────────────────────────────

    def _get_obs(self) -> dict:
        frame = self.perception.capture_frame()           # (84,84,1) float32
        # Capture brute pour l'extraction d'état (avant resize)
        raw = self.perception.sct.grab(SCREEN_REGION)
        bgr = cv2.cvtColor(np.array(raw), cv2.COLOR_BGRA2BGR)
        self._last_frame_bgr = bgr
        state_vec = self.perception.extract_state_vector(bgr)
        return {"frame": frame, "state_vec": state_vec}

    def _is_dead(self) -> bool:
        """
        Détecte la mort via template matching sur l'écran de respawn.
        À implémenter : charger un template PNG de l'écran de mort.
        """
        # TODO: cv2.matchTemplate(self._last_frame_bgr, death_template, ...)
        return False

    # ── API Gymnasium ─────────────────────────────────────────────────────────

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0
        self.reward_fn.reset()

        # Optionnel : recharger la sauvegarde Factorio via pyautogui si nécessaire
        # Pour le MVP, on suppose que le jeu est déjà en cours
        time.sleep(1.0)  # laisser le jeu se stabiliser après reset

        obs = self._get_obs()
        info = {}
        return obs, info

    def step(self, action: int):
        assert self.action_space.contains(action), f"Action invalide : {action}"

        # 1. Exécuter l'action dans le jeu
        self.executor.execute(action)

        # Délai de synchronisation : laisser le jeu réagir
        time.sleep(STEP_DELAY)

        # 2. Observer le nouvel état
        obs = self._get_obs()

        # 3. Détecter fin d'épisode
        dead = self._is_dead()
        timeout = self.step_count >= MAX_STEPS
        terminated = dead
        truncated = timeout

        # 4. Informations contextuelles pour la reward function
        info = {
            "death": dead,
            "building_placed": False,   # TODO : détecter via OCR/template
            "tech_unlocked": False,     # TODO
            "step": self.step_count,
        }

        # 5. Calculer le reward
        reward = self.reward_fn.compute(obs["state_vec"], terminated, info)

        self.step_count += 1
        return obs, reward, terminated, truncated, info

    def render(self):
        """Retourne la dernière frame BGR pour visualisation externe."""
        return self._last_frame_bgr

    def close(self):
        pass