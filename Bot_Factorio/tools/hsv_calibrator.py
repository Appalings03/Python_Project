# tools/hsv_calibrator.py
"""
Outil de calibration HSV interactif.
Permet d'identifier les plages HSV des éléments UI et des dépôts de ressources.

Utilisation :
1. Lancer Factorio en jeu
2. Lancer ce script
3. Basculer sur Factorio (3s de délai)
4. La fenêtre de calibration s'ouvre
5. Utiliser les trackbars pour isoler la couleur voulue
6. Appuyer sur 's' pour sauvegarder les valeurs dans hsv_ranges.json
7. Appuyer sur 'q' pour quitter
"""

import cv2
import numpy as np
import mss
import time
import json
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────

CAPTURE_REGION = {"top": 0, "left": 0, "width": 1280, "height": 800}
WINDOW_NAME    = "HSV Calibrator — Factorio Bot"
OUTPUT_FILE    = "hsv_ranges.json"

# Plages de départ basées sur les screenshots fournis
PRESETS = {
    "copper_ore":  {"h_min": 0,   "h_max": 15,  "s_min": 80,  "s_max": 200, "v_min": 100, "v_max": 220},
    "iron_ore":    {"h_min": 100, "h_max": 130, "s_min": 20,  "s_max": 100, "v_min": 80,  "v_max": 160},
    "coal":        {"h_min": 0,   "h_max": 180, "s_min": 0,   "s_max": 50,  "v_min": 0,   "v_max": 60},
    "stone":       {"h_min": 15,  "h_max": 35,  "s_min": 20,  "s_max": 100, "v_min": 120, "v_max": 200},
    "water":       {"h_min": 95,  "h_max": 115, "s_min": 100, "s_max": 255, "v_min": 100, "v_max": 220},
}

# ─── Calibrateur ──────────────────────────────────────────────────────────────

class HSVCalibrator:

    def __init__(self):
        self.sct = mss.MSS()
        self.current_preset = "copper_ore"
        self.saved_ranges = {}

        # Charger les ranges existants si le fichier existe
        if Path(OUTPUT_FILE).exists():
            with open(OUTPUT_FILE) as f:
                self.saved_ranges = json.load(f)
            print(f"[INFO] Ranges existants chargés depuis {OUTPUT_FILE}")

    def setup_window(self):
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, 1200, 700)
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

        p = PRESETS[self.current_preset]

        # Trackbars HSV
        cv2.createTrackbar("H min", WINDOW_NAME, p["h_min"], 179, lambda x: None)
        cv2.createTrackbar("H max", WINDOW_NAME, p["h_max"], 179, lambda x: None)
        cv2.createTrackbar("S min", WINDOW_NAME, p["s_min"], 255, lambda x: None)
        cv2.createTrackbar("S max", WINDOW_NAME, p["s_max"], 255, lambda x: None)
        cv2.createTrackbar("V min", WINDOW_NAME, p["v_min"], 255, lambda x: None)
        cv2.createTrackbar("V max", WINDOW_NAME, p["v_max"], 255, lambda x: None)

    def read_trackbars(self) -> dict:
        return {
            "h_min": cv2.getTrackbarPos("H min", WINDOW_NAME),
            "h_max": cv2.getTrackbarPos("H max", WINDOW_NAME),
            "s_min": cv2.getTrackbarPos("S min", WINDOW_NAME),
            "s_max": cv2.getTrackbarPos("S max", WINDOW_NAME),
            "v_min": cv2.getTrackbarPos("V min", WINDOW_NAME),
            "v_max": cv2.getTrackbarPos("V max", WINDOW_NAME),
        }

    def apply_mask(self, frame_bgr: np.ndarray, ranges: dict) -> tuple:
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        lower = np.array([ranges["h_min"], ranges["s_min"], ranges["v_min"]])
        upper = np.array([ranges["h_max"], ranges["s_max"], ranges["v_max"]])
        mask  = cv2.inRange(hsv, lower, upper)

        # Appliquer le masque sur l'image originale
        result = cv2.bitwise_and(frame_bgr, frame_bgr, mask=mask)

        # Stats du masque
        pixel_count = cv2.countNonZero(mask)
        total_pixels = mask.shape[0] * mask.shape[1]
        coverage_pct = pixel_count / total_pixels * 100

        return mask, result, coverage_pct

    def build_display(
        self,
        frame_bgr: np.ndarray,
        mask: np.ndarray,
        result: np.ndarray,
        ranges: dict,
        coverage_pct: float,
    ) -> np.ndarray:
        h, w = 320, 400  # taille de chaque panneau

        # Resize les 3 vues
        orig   = cv2.resize(frame_bgr, (w, h))
        mask_3 = cv2.cvtColor(cv2.resize(mask, (w, h)), cv2.COLOR_GRAY2BGR)
        res    = cv2.resize(result, (w, h))

        # Panneau d'info
        info = np.zeros((h, w, 3), dtype=np.uint8)
        lines = [
            f"Preset: {self.current_preset}",
            f"",
            f"H: [{ranges['h_min']}, {ranges['h_max']}]",
            f"S: [{ranges['s_min']}, {ranges['s_max']}]",
            f"V: [{ranges['v_min']}, {ranges['v_max']}]",
            f"",
            f"Coverage: {coverage_pct:.2f}%",
            f"",
            f"Commandes:",
            f"  's' = sauvegarder",
            f"  'n' = preset suivant",
            f"  'q' = quitter",
            f"",
            f"Sauvegardés: {list(self.saved_ranges.keys())}",
        ]
        for i, line in enumerate(lines):
            color = (0, 255, 180) if i == 0 else (200, 200, 200)
            if "Coverage" in line:
                # Colorer selon la qualité du masque
                color = (0, 255, 0) if 1 < coverage_pct < 15 else (0, 100, 255)
            cv2.putText(info, line, (10, 25 + i * 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Labels sur les panneaux
        for panel, label in [(orig, "Original"), (mask_3, "Masque"), (res, "Resultat")]:
            cv2.putText(panel, label, (8, 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3)
            cv2.putText(panel, label, (8, 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        # Assembler : ligne du haut (orig + masque), ligne du bas (result + info)
        top    = np.hstack([orig, mask_3])
        bottom = np.hstack([res, info])
        return np.vstack([top, bottom])

    def save_current(self, ranges: dict):
        self.saved_ranges[self.current_preset] = ranges
        with open(OUTPUT_FILE, "w") as f:
            json.dump(self.saved_ranges, f, indent=2)
        print(f"[SAVED] {self.current_preset} → {ranges}")
        print(f"[INFO]  Fichier mis à jour : {OUTPUT_FILE}")

    def next_preset(self):
        presets_list = list(PRESETS.keys())
        idx = presets_list.index(self.current_preset)
        self.current_preset = presets_list[(idx + 1) % len(presets_list)]

        # Charger les valeurs sauvegardées si elles existent, sinon les defaults
        p = self.saved_ranges.get(self.current_preset, PRESETS[self.current_preset])
        cv2.setTrackbarPos("H min", WINDOW_NAME, p["h_min"])
        cv2.setTrackbarPos("H max", WINDOW_NAME, p["h_max"])
        cv2.setTrackbarPos("S min", WINDOW_NAME, p["s_min"])
        cv2.setTrackbarPos("S max", WINDOW_NAME, p["s_max"])
        cv2.setTrackbarPos("V min", WINDOW_NAME, p["v_min"])
        cv2.setTrackbarPos("V max", WINDOW_NAME, p["v_max"])

        print(f"[PRESET] → {self.current_preset}")

    def run(self):
        print(f"Démarrage dans 3s — bascule sur Factorio")
        for i in range(3, 0, -1):
            print(f"  {i}...")
            time.sleep(1)

        self.setup_window()
        print(f"\nCalibration de : {self.current_preset}")
        print("Ajuste les trackbars jusqu'à isoler la couleur voulue")
        print("Coverage idéal : 1–15% (assez pour détecter, pas trop pour éviter le bruit)\n")

        while True:
            # Capture
            raw = self.sct.grab(CAPTURE_REGION)
            bgr = cv2.cvtColor(np.array(raw), cv2.COLOR_BGRA2BGR)

            # Lire les trackbars et appliquer
            ranges = self.read_trackbars()
            mask, result, coverage = self.apply_mask(bgr, ranges)

            # Afficher
            display = self.build_display(bgr, mask, result, ranges, coverage)
            cv2.imshow(WINDOW_NAME, display)

            key = cv2.waitKey(30) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("s"):
                self.save_current(ranges)
            elif key == ord("n"):
                self.next_preset()
                print(f"Calibration de : {self.current_preset}")

        cv2.destroyAllWindows()
        print(f"\nRanges finaux sauvegardés dans {OUTPUT_FILE}")


if __name__ == "__main__":
    cal = HSVCalibrator()
    cal.run()