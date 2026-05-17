# actions/action_space_v2.py
"""
Action space hiérarchique Phase 3+.
Niveau 1 (macro) : choisir le TYPE d'action
Niveau 2 (paramètre) : choisir la CIBLE parmi les entités détectées

Implémenté comme Discrete(N_macros) dans un premier temps,
avec le paramètre résolu automatiquement par heuristique
(ex: "aller au minerai le plus proche").
"""
from enum import IntEnum
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController

class MacroAction(IntEnum):
    # Navigation
    MOVE_UP        = 0
    MOVE_DOWN      = 1
    MOVE_LEFT      = 2
    MOVE_RIGHT     = 3

    # Collecte
    MINE_NEAREST   = 4   # se déplace et mine l'entité la plus proche
    PICK_UP_GROUND = 5

    # Construction
    PLACE_DRILL    = 6   # pose un burner mining drill sur le minerai ciblé
    PLACE_FURNACE  = 7   # pose une stone furnace
    PLACE_CHEST    = 8

    # Gestion
    OPEN_INVENTORY = 9
    OPEN_TECH_TREE = 10
    RESEARCH_NEXT  = 11  # clique sur la prochaine tech disponible

    # Maintenance
    REFUEL_NEAREST = 12  # ravitaille en charbon la structure la plus proche
    WAIT           = 13

N_ACTIONS_V2 = len(MacroAction)


class MacroActionExecutor:
    """
    Exécute les macro-actions en combinant vision + contrôle.
    Chaque macro encapsule la séquence complète de clics/touches nécessaires.
    """

    def __init__(self, mouse, keyboard, ui_extractor):
        self.mouse = mouse
        self.keyboard = keyboard
        self.ui = ui_extractor
        self._last_entities = []  # cache des entités détectées

    def execute(self, action: int, frame_bgr, screen_center: tuple):
        cx, cy = screen_center  # centre de l'écran = position joueur

        if action == MacroAction.MINE_NEAREST:
            self._mine_nearest(frame_bgr, cx, cy)

        elif action == MacroAction.PLACE_DRILL:
            self._place_building("burner_mining_drill", frame_bgr, cx, cy)

        elif action == MacroAction.PLACE_FURNACE:
            self._place_building("stone_furnace", frame_bgr, cx, cy)

        elif action == MacroAction.RESEARCH_NEXT:
            self._click_research()

        # ... autres actions

    def _mine_nearest(self, frame_bgr, cx, cy):
        """Déplace la souris vers le dépôt le plus proche et maintient clic gauche."""
        import time
        entities = self.ui.detect_entities_on_screen(frame_bgr)
        deposits = [e for e in entities if "deposit" in e["name"]]
        if not deposits:
            return  # rien à miner, action nulle

        # Trouver le plus proche du centre écran (= position joueur)
        nearest = min(deposits, key=lambda e: (e["x"]-cx)**2 + (e["y"]-cy)**2)
        self.mouse.position = (nearest["screen_x"], nearest["screen_y"])
        self.mouse.press(Button.left)
        time.sleep(0.5)
        self.mouse.release(Button.left)

    def _place_building(self, building_name: str, frame_bgr, cx, cy):
        """
        Séquence : ouvrir inventaire → sélectionner bâtiment → placer sur cible.
        Nécessite que le bâtiment soit dans l'inventaire.
        """
        # TODO : implémenter la séquence complète
        # 1. Keyboard shortcut ou clic inventaire
        # 2. Trouver l'icône du bâtiment dans l'inventaire (template matching)
        # 3. Clic sur l'icône → bâtiment attaché à la souris
        # 4. Clic sur la position cible
        pass

    def _click_research(self):
        """Ouvre le tech tree et clique sur la prochaine recherche disponible."""
        import time
        self.keyboard.press("t")
        time.sleep(0.3)
        self.keyboard.release("t")
        # TODO : template matching sur le bouton "Rechercher" de la première tech
        time.sleep(0.5)