"""Entidades móveis do jogo."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from .config import BLUE, CYAN, ORANGE, PINK, PURPLE, RED, WHITE, WIDTH, HEIGHT


def clamp(value, minimum, maximum):
    """Limita um número a um intervalo."""
    return max(minimum, min(value, maximum))


@dataclass
class Particle:
    """Fragmento visual de curta duração usado em explosões e propulsão."""
    pos: pygame.Vector2
    velocity: pygame.Vector2
    color: tuple
    life: float
    size: float

    def update(self, dt):
        self.pos += self.velocity * dt
        self.velocity *= 0.95
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, self.pos, max(1, int(self.size * self.life)))


class Bullet:
    """Projétil simples. ``friendly`` define qual grupo pode ser atingido."""
    def __init__(self, position, velocity, friendly=True, color=CYAN, damage=1):
        self.pos, self.velocity = pygame.Vector2(position), pygame.Vector2(velocity)
        self.friendly, self.color, self.damage = friendly, color, damage
        self.radius = 5 if friendly else 6
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.rect.center = self.pos

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        return -30 < self.pos.y < HEIGHT + 30

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.pos, self.radius + 3)
        pygame.draw.circle(surface, WHITE, self.pos, max(2, self.radius - 2))


class Player:
    """Nave controlada pelo jogador, incluindo vida, tiro e energia."""
    def __init__(self):
        self.pos = pygame.Vector2(WIDTH / 2, HEIGHT - 95)
        self.speed, self.max_health, self.health = 430, 100, 100
        self.energy, self.shoot_cooldown, self.invincible = 100.0, 0.0, 0.0
        self.rect = pygame.Rect(0, 0, 48, 52)
        self.rect.center = self.pos

    def update(self, dt, keys, particles):
        direction = pygame.Vector2(keys[pygame.K_d] - keys[pygame.K_a] + keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_s] - keys[pygame.K_w] + keys[pygame.K_DOWN] - keys[pygame.K_UP])
        # Normalizar impede que o movimento diagonal seja mais veloz.
        if direction.length_squared() > 0:
            self.pos += direction.normalize() * self.speed * dt
        self.pos.x, self.pos.y = clamp(self.pos.x, 32, WIDTH - 32), clamp(self.pos.y, HEIGHT * .48, HEIGHT - 38)
        self.rect.center = self.pos
        self.shoot_cooldown, self.invincible = max(0, self.shoot_cooldown - dt), max(0, self.invincible - dt)
        self.energy = min(100, self.energy + 14 * dt)
        if random.random() < .55:
            particles.append(Particle(self.pos + (random.randint(-8, 8), 27), pygame.Vector2(random.uniform(-22, 22), random.uniform(80, 145)), ORANGE, .45, 4))

    def shoot(self):
        if self.shoot_cooldown > 0: return []
        self.shoot_cooldown = .18
        return [Bullet(self.pos + (-16, -25), (0, -720)), Bullet(self.pos + (16, -25), (0, -720))]

    def hit(self, damage):
        """A invencibilidade breve evita receber dano a cada quadro."""
        if self.invincible > 0: return False
        self.health, self.invincible = max(0, self.health - damage), .65
        return True

    def draw(self, surface):
        if self.invincible > 0 and int(self.invincible * 12) % 2 == 0: return
        x, y = self.pos
        points = [(x, y - 30), (x - 23, y + 22), (x - 10, y + 16), (x, y + 27), (x + 10, y + 16), (x + 23, y + 22)]
        pygame.draw.polygon(surface, BLUE, points); pygame.draw.polygon(surface, CYAN, points, 2)
        pygame.draw.polygon(surface, WHITE, [(x, y - 19), (x - 7, y + 8), (x + 7, y + 8)])


class Enemy:
    """Inimigo com três arquétipos; atributos variam por onda."""
    STATS = {"scout": (1, 130, 12, PURPLE, 100), "hunter": (3, 90, 20, PINK, 65), "tank": (7, 52, 35, ORANGE, 42)}

    def __init__(self, kind, x, wave):
        health, speed, score, color, fire_rate = self.STATS[kind]
        self.kind, self.color, self.pos = kind, color, pygame.Vector2(x, random.randint(-160, -50))
        self.health, self.speed = health + max(0, wave - 1) // 3, speed + wave * 4
        self.damage, self.score = (10 if kind != "tank" else 18), score
        self.radius = 17 if kind == "scout" else 23 if kind == "hunter" else 30
        self.fire_timer, self.fire_rate, self.phase = random.uniform(.4, 1.4), max(.35, fire_rate / 100), random.random() * math.tau
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2); self.rect.center = self.pos

    def update(self, dt, player_pos):
        self.phase += dt * (2.5 if self.kind == "scout" else 1.5)
        self.pos.y += self.speed * dt; self.pos.x += math.sin(self.phase) * (90 if self.kind == "scout" else 38) * dt
        self.pos.x = clamp(self.pos.x, self.radius, WIDTH - self.radius); self.rect.center = self.pos; self.fire_timer -= dt
        if self.pos.y > 15 and self.fire_timer <= 0:
            self.fire_timer = self.fire_rate + random.uniform(.1, .5); target = player_pos - self.pos
            if target.length_squared(): return Bullet(self.pos, target.normalize() * 280, False, RED, self.damage)
        return None

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.pos, self.radius); pygame.draw.circle(surface, WHITE, self.pos, self.radius, 2)
        pygame.draw.circle(surface, (20, 15, 40), self.pos, max(5, self.radius // 3)); pygame.draw.circle(surface, WHITE, self.pos + (3, -2), 2)
