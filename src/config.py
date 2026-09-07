"""Constantes centralizadas.

Concentrar os valores que serão ajustados com frequência evita "números
mágicos" espalhados pelo código e torna mais fácil equilibrar o jogo.
"""

from pathlib import Path

WIDTH, HEIGHT = 1100, 700
FPS = 60
TITLE = "Nebula Sentinel"
DATA_DIR = Path("data")
SAVE_FILE = DATA_DIR / "save.json"

# Paleta: tons escuros criam contraste com os lasers e interfaces luminosas.
BACKGROUND = (7, 10, 24)
PANEL = (13, 20, 43)
WHITE = (235, 244, 255)
MUTED = (139, 160, 194)
CYAN = (57, 225, 255)
BLUE = (74, 115, 255)
PURPLE = (182, 91, 255)
PINK = (255, 83, 163)
ORANGE = (255, 165, 74)
RED = (255, 82, 103)
GREEN = (88, 239, 171)
YELLOW = (255, 226, 105)
