# test_loop.py
"""
Test de la boucle step() sans agent RL.
Actions aléatoires pendant N épisodes, overlay OpenCV en fenêtre séparée.
Objectif : valider capture → action → délai → observation sans crash.

Lancer APRÈS avoir ouvert Factorio en plein écran.
Laisser 3 secondes pour basculer sur Factorio après le lancement du script.
"""

import time
import random
import cv2
import numpy as np
import mss
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

# ─── Config ───────────────────────────────────────────────────────────────────

SCREEN_REGION = {
    "top":    0,
    "left":   0,
    "width":  2560,
    "height": 1600,
}

OBS_SIZE     = (84, 84)      # taille de la frame réduite envoyée à l'agent
OVERLAY_SIZE = (960, 600)    # taille de la fenêtre de debug (≈ 37% de 2560x1600)
STEP_DELAY   = 0.15          # secondes entre chaque action (~6-7 Hz)
N_EPISODES   = 3             # nombre d'épisodes à jouer
MAX_STEPS    = 50            # steps par épisode (court pour le test)
WARMUP_S     = 3             # secondes avant de commencer (pour basculer sur Factorio)

# Actions discrètes testées
ACTION_MAP = {
    0: ("move",      "z"),
    1: ("move",      "s"),
    2: ("move",      "q"),
    3: ("move",      "d"),
    4: ("mine",      None),
    5: ("interact",  None),
    6: ("inventory", None),
    7: ("wait",      None),
}

# ─── Capture ──────────────────────────────────────────────────────────────────

class Capture:
    def __init__(self):
        self.sct = mss.mss()
        self._last_raw = None

    def grab(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Retourne (frame_obs, frame_display).
        frame_obs     : (84, 84, 1) float32 normalisé — pour l'agent
        frame_display : BGR 2560x1600 — pour l'overlay
        """
        t0 = time.perf_counter()
        raw = self.sct.grab(SCREEN_REGION)
        bgr = cv2.cvtColor(np.array(raw), cv2.COLOR_BGRA2BGR)
        latency_ms = (time.perf_counter() - t0) * 1000
        self._last_latency = latency_ms

        gray   = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, OBS_SIZE, interpolation=cv2.INTER_AREA)
        frame_obs = resized[..., np.newaxis].astype(np.float32) / 255.0

        return frame_obs, bgr

    @property
    def last_latency_ms(self) -> float:
        return getattr(self, "_last_latency", 0.0)

# ─── Contrôle ─────────────────────────────────────────────────────────────────

class Controller:
    def __init__(self):
        self.mouse    = MouseController()
        self.keyboard = KeyboardController()

    def execute(self, action_idx: int) -> str:
        action_type, param = ACTION_MAP[action_idx]

        if action_type == "move":
            self.keyboard.press(param)
            time.sleep(0.05)
            self.keyboard.release(param)
            return f"move({param})"

        elif action_type == "mine":
            self.mouse.press(Button.left)
            time.sleep(0.12)
            self.mouse.release(Button.left)
            return "mine"

        elif action_type == "interact":
            self.mouse.click(Button.right, 1)
            return "interact"

        elif action_type == "inventory":
            self.keyboard.press("e")
            time.sleep(0.05)
            self.keyboard.release("e")
            return "inventory"

        elif action_type == "wait":
            return "wait"

        return "unknown"

# ─── Overlay debug ────────────────────────────────────────────────────────────

class DebugWindow:
    WINDOW = "Factorio Bot — Debug"

    def __init__(self):
        cv2.namedWindow(self.WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.WINDOW, *OVERLAY_SIZE)

    def render(
        self,
        frame_bgr:   np.ndarray,
        frame_obs:   np.ndarray,
        action_name: str,
        episode:     int,
        step:        int,
        latency_ms:  float,
        step_time_ms: float,
    ):
        display = cv2.resize(frame_bgr, OVERLAY_SIZE)

        # ── Miniature de l'observation (ce que verra l'agent) ─────────────
        obs_vis = cv2.resize(
            (frame_obs[..., 0] * 255).astype(np.uint8),
            (168, 168),                          # 2× la taille obs pour la lisibilité
            interpolation=cv2.INTER_NEAREST,
        )
        obs_bgr = cv2.cvtColor(obs_vis, cv2.COLOR_GRAY2BGR)

        # Bordure orange autour de la miniature
        cv2.rectangle(obs_bgr, (0, 0), (167, 167), (0, 165, 255), 2)

        # Coller la miniature en haut à droite
        x_off = OVERLAY_SIZE[0] - 178
        display[10:178, x_off:x_off+168] = obs_bgr

        # Label "Agent POV"
        cv2.putText(display, "Agent POV (84x84)",
                    (x_off, 193),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 165, 255), 1)

        # ── HUD principal ─────────────────────────────────────────────────
        hud = [
            f"Episode : {episode + 1} / {N_EPISODES}",
            f"Step    : {step + 1} / {MAX_STEPS}",
            f"Action  : {action_name}",
            f"Capture : {latency_ms:.1f} ms",
            f"Step    : {step_time_ms:.1f} ms",
            f"FPS     : {1000/max(step_time_ms,1):.1f}",
        ]
        for i, line in enumerate(hud):
            # Ombre
            cv2.putText(display, line, (11, 26 + i * 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0, 0, 0), 3)
            # Texte
            color = (0, 255, 180) if i < 2 else (255, 255, 255)
            cv2.putText(display, line, (10, 25 + i * 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.58, color, 1)

        # ── Barre de progression de l'épisode ─────────────────────────────
        bar_w  = OVERLAY_SIZE[0] - 20
        bar_h  = 8
        bar_y  = OVERLAY_SIZE[1] - 16
        filled = int(bar_w * (step + 1) / MAX_STEPS)
        cv2.rectangle(display, (10, bar_y), (10 + bar_w, bar_y + bar_h),
                      (60, 60, 60), -1)
        cv2.rectangle(display, (10, bar_y), (10 + filled, bar_y + bar_h),
                      (0, 200, 100), -1)

        cv2.imshow(self.WINDOW, display)
        cv2.waitKey(1)  # non-bloquant

    def close(self):
        cv2.destroyAllWindows()

# ─── Boucle principale ────────────────────────────────────────────────────────

def run_test():
    print(f"[INFO] Démarrage dans {WARMUP_S}s — bascule sur Factorio maintenant")
    for i in range(WARMUP_S, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print("[INFO] C'est parti !\n")

    capture    = Capture()
    controller = Controller()
    debug_win  = DebugWindow()

    stats = {
        "total_steps":    0,
        "latencies_ms":   [],
        "step_times_ms":  [],
        "actions_count":  {v[0]: 0 for v in ACTION_MAP.values()},
    }

    try:
        for episode in range(N_EPISODES):
            print(f"[Episode {episode + 1}/{N_EPISODES}]")

            for step in range(MAX_STEPS):
                t_step_start = time.perf_counter()

                # 1. Capturer
                frame_obs, frame_bgr = capture.grab()

                # 2. Action aléatoire
                action_idx  = random.randint(0, len(ACTION_MAP) - 1)
                action_name = controller.execute(action_idx)
                stats["actions_count"][ACTION_MAP[action_idx][0]] += 1

                # 3. Délai de sync
                time.sleep(STEP_DELAY)

                # 4. Métriques
                step_time_ms = (time.perf_counter() - t_step_start) * 1000
                stats["latencies_ms"].append(capture.last_latency_ms)
                stats["step_times_ms"].append(step_time_ms)
                stats["total_steps"] += 1

                # 5. Overlay
                debug_win.render(
                    frame_bgr, frame_obs,
                    action_name,
                    episode, step,
                    capture.last_latency_ms,
                    step_time_ms,
                )

                # 6. Log console léger
                print(
                    f"  step {step+1:02d} | "
                    f"action={action_name:<10} | "
                    f"capture={capture.last_latency_ms:5.1f}ms | "
                    f"step={step_time_ms:6.1f}ms"
                )

                # Quitter proprement avec 'q' dans la fenêtre OpenCV
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("[INFO] Arrêt demandé")
                    raise KeyboardInterrupt

            print(f"  → Episode {episode + 1} terminé\n")
            time.sleep(0.5)  # pause entre épisodes

    except KeyboardInterrupt:
        print("\n[INFO] Interrompu proprement")

    finally:
        debug_win.close()

    # ── Rapport final ─────────────────────────────────────────────────────────
    lats = stats["latencies_ms"]
    stps = stats["step_times_ms"]
    print("\n" + "="*50)
    print("RAPPORT DE TEST")
    print("="*50)
    print(f"Steps totaux       : {stats['total_steps']}")
    print(f"Latence capture    : moy={sum(lats)/len(lats):.1f}ms  "
          f"max={max(lats):.1f}ms  min={min(lats):.1f}ms")
    print(f"Durée step totale  : moy={sum(stps)/len(stps):.1f}ms  "
          f"max={max(stps):.1f}ms  min={min(stps):.1f}ms")
    print(f"FPS effectif       : {1000/(sum(stps)/len(stps)):.1f}")
    print(f"\nDistribution actions :")
    for name, count in stats["actions_count"].items():
        bar = "█" * (count * 20 // max(stats["actions_count"].values(), default=1))
        print(f"  {name:<12} {count:3d}  {bar}")
    print("="*50)

if __name__ == "__main__":
    run_test()