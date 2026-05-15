# utils/debug_overlay.py
import cv2
import numpy as np

class DebugOverlay:
    """
    Affiche en temps réel ce que voit et décide l'agent.
    Utile pour diagnostiquer les problèmes de perception avant de lancer l'entraînement.
    """

    def render(
        self,
        frame_bgr: np.ndarray,
        entities: list[dict],
        action_name: str,
        reward: float,
        state_vec: np.ndarray,
        step: int,
    ) -> np.ndarray:
        overlay = frame_bgr.copy()

        # Dessiner les entités détectées
        for entity in entities:
            cv2.circle(overlay, (entity["screen_x"], entity["screen_y"]), 15, (0, 255, 0), 2)
            cv2.putText(
                overlay,
                f"{entity['name']} ({entity['confidence']:.2f})",
                (entity["screen_x"] + 18, entity["screen_y"]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1,
            )

        # HUD de debug (coin supérieur gauche)
        hud_lines = [
            f"Step: {step}",
            f"Action: {action_name}",
            f"Reward: {reward:+.3f}",
            f"Iron: {state_vec[0]*500:.0f}  Cu: {state_vec[1]*500:.0f}",
            f"Coal: {state_vec[2]*500:.0f}  Health: {state_vec[8]*100:.0f}%",
        ]
        for i, line in enumerate(hud_lines):
            cv2.putText(
                overlay, line,
                (10, 20 + i * 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2,
            )

        return overlay

    def show(self, overlay: np.ndarray, window_name: str = "Factorio Bot Debug"):
        """Affiche l'overlay dans une fenêtre OpenCV séparée."""
        small = cv2.resize(overlay, (960, 540))  # moitié de la résolution
        cv2.imshow(window_name, small)
        cv2.waitKey(1)  # non-bloquant