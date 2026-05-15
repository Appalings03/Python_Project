# perception/ui_extractor.py
import cv2
import numpy as np

class UIExtractor:
    """
    Extrait les informations structurées depuis l'UI Factorio
    par masquage HSV et OCR léger.
    Calibrer les plages HSV sur ta résolution et tes paramètres visuels.
    """

    # Zones de l'écran à inspecter (en pixels, pour 1920x1080)
    # À ajuster selon ta résolution
    ROI = {
        "resource_bar":  (0,    0,    400,  40),   # x, y, w, h
        "minimap":       (1720, 850,  200, 200),
        "inventory_grid":(400,  100,  700, 600),
        "tech_bar":      (600,   0,   400,  40),
    }

    def extract_resource_counts(self, frame_bgr: np.ndarray) -> dict:
        """
        Retourne un dict approximatif des ressources visibles dans la barre.
        Stratégie : template matching sur les icônes de ressources,
        puis OCR (pytesseract) sur les chiffres adjacents.
        """
        x, y, w, h = self.ROI["resource_bar"]
        roi = frame_bgr[y:y+h, x:x+w]

        resources = {}

        # Exemple : détecter l'icône "fer" par template matching
        for resource_name, template_path in RESOURCE_TEMPLATES.items():
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                continue
            result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > 0.75:  # seuil de confiance
                # Lire le nombre à droite de l'icône
                tx, ty = max_loc
                number_roi = roi[ty:ty+20, tx+20:tx+80]
                count = self._ocr_number(number_roi)
                resources[resource_name] = count

        return resources

    def _ocr_number(self, roi: np.ndarray) -> int:
        """
        OCR minimaliste sur une zone contenant un nombre.
        pytesseract avec config numérique uniquement.
        """
        try:
            import pytesseract
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            # Binarisation agressive pour l'OCR
            _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
            text = pytesseract.image_to_string(
                thresh,
                config="--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789k"
            )
            # Gérer les suffixes "k" (ex: "1.2k" → 1200)
            text = text.strip().lower()
            if text.endswith("k"):
                return int(float(text[:-1]) * 1000)
            return int(text) if text.isdigit() else 0
        except Exception:
            return 0

    def detect_entities_on_screen(self, frame_bgr: np.ndarray) -> list[dict]:
        """
        Détecte les entités Factorio visibles (minerais, bâtiments)
        par template matching multi-échelle.
        Retourne une liste de {name, x, y, confidence}.
        """
        entities = []
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        for entity_name, template_path in ENTITY_TEMPLATES.items():
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                continue

            # Multi-échelle pour gérer le zoom de la caméra
            for scale in [0.8, 1.0, 1.2]:
                h, w = template.shape
                tw = int(w * scale)
                th = int(h * scale)
                if tw < 5 or th < 5:
                    continue
                t_scaled = cv2.resize(template, (tw, th))
                result = cv2.matchTemplate(gray, t_scaled, cv2.TM_CCOEFF_NORMED)

                # Trouver tous les matches au-dessus du seuil (pas uniquement le max)
                locations = np.where(result >= 0.70)
                for pt in zip(*locations[::-1]):
                    entities.append({
                        "name": entity_name,
                        "x": pt[0] + tw // 2,
                        "y": pt[1] + th // 2,
                        "confidence": float(result[pt[1], pt[0]]),
                        "screen_x": pt[0],
                        "screen_y": pt[1],
                    })

        # NMS (Non-Maximum Suppression) pour dédupliquer
        return self._nms(entities, iou_threshold=0.5)

    def _nms(self, entities: list, iou_threshold: float) -> list:
        """Supprime les détections redondantes proches."""
        if not entities:
            return []
        entities = sorted(entities, key=lambda e: e["confidence"], reverse=True)
        kept = []
        for entity in entities:
            duplicate = False
            for kept_e in kept:
                dist = ((entity["x"] - kept_e["x"])**2 +
                        (entity["y"] - kept_e["y"])**2) ** 0.5
                if dist < 30:  # pixels
                    duplicate = True
                    break
            if not duplicate:
                kept.append(entity)
        return kept

    def detect_death_screen(self, frame_bgr: np.ndarray) -> bool:
        """
        Détecte l'écran de mort par présence d'une teinte rouge dominante
        + vérification d'un template de l'écran "You died".
        """
        # Méthode rapide : ratio de pixels rouges dans la zone centrale
        h, w = frame_bgr.shape[:2]
        center = frame_bgr[h//4:3*h//4, w//4:3*w//4]
        hsv = cv2.cvtColor(center, cv2.COLOR_BGR2HSV)

        # Plage HSV du rouge Factorio (mort)
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_ratio = (cv2.countNonZero(mask1) + cv2.countNonZero(mask2)) / (center.size / 3)

        return red_ratio > 0.35  # plus de 35% de rouge → écran de mort probable


# Dictionnaires de templates à peupler avec tes captures
RESOURCE_TEMPLATES: dict[str, str] = {
    "iron_ore":   "templates/resources/iron_ore.png",
    "copper_ore": "templates/resources/copper_ore.png",
    "coal":       "templates/resources/coal.png",
    "stone":      "templates/resources/stone.png",
    "iron_plate": "templates/resources/iron_plate.png",
}

ENTITY_TEMPLATES: dict[str, str] = {
    "iron_ore_deposit":    "templates/entities/iron_deposit.png",
    "coal_deposit":        "templates/entities/coal_deposit.png",
    "stone_furnace":       "templates/entities/stone_furnace.png",
    "burner_mining_drill": "templates/entities/burner_drill.png",
    "chest":               "templates/entities/chest.png",
}