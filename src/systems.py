"""Sistemas que coordenam entidades: ondas, explosões e persistência."""

import json
import random
import pygame

from .config import DATA_DIR, SAVE_FILE, WIDTH
from .entities import Enemy, Particle


class SaveData:
    """Salvamento defensivo de um único dado: o maior recorde."""
    @staticmethod
    def load_high_score():
        try:
            return int(json.loads(SAVE_FILE.read_text(encoding="utf-8")).get("high_score", 0))
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return 0

    @staticmethod
    def save_high_score(score):
        DATA_DIR.mkdir(exist_ok=True)
        SAVE_FILE.write_text(json.dumps({"high_score": score}, indent=2), encoding="utf-8")


class WaveDirector:
    """Controla a cadência das ondas, sem conhecer detalhes de desenho."""
    def __init__(self):
        self.wave, self.remaining = 0, 0
        self.spawn_timer, self.break_timer, self.waiting = 1.2, 1.5, True

    def update(self, dt, enemies):
        """Devolve True exatamente quando uma nova onda começa."""
        started = False
        if self.waiting:
            self.break_timer -= dt
            if self.break_timer <= 0:
                self.wave += 1; self.remaining = 5 + self.wave * 2
                self.spawn_timer, self.waiting, started = 0, False, True
        elif self.remaining > 0:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                enemies.append(Enemy(self.choose_kind(), random.randint(45, WIDTH - 45), self.wave))
                self.remaining -= 1; self.spawn_timer = max(.22, .72 - self.wave * .025)
        elif not enemies:
            self.waiting, self.break_timer = True, 2.2
        return started

    def choose_kind(self):
        roll = random.random()
        if self.wave >= 4 and roll < .18: return "tank"
        if self.wave >= 2 and roll < .48: return "hunter"
        return "scout"


def explosion(particles, position, color, amount=18):
    """Adiciona partículas radiais; a física delas é atualizada em Game."""
    for _ in range(amount):
        particles.append(Particle(pygame.Vector2(position), pygame.Vector2(random.uniform(-190, 190), random.uniform(-190, 190)), color, random.uniform(.35, .8), random.uniform(2, 6)))
