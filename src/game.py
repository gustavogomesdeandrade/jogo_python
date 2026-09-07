"""Loop principal, telas e regras centrais do Nebula Sentinel."""

import random
import pygame

from .audio import SoundManager
from .config import BACKGROUND, CYAN, FPS, GREEN, HEIGHT, MUTED, ORANGE, RED, TITLE, WHITE, WIDTH, YELLOW
from .entities import Player
from .systems import SaveData, WaveDirector, explosion
from .ui import bar, panel, text


class Game:
    """Orquestra entrada, atualização e desenho em um ciclo de 60 FPS."""
    def __init__(self):
        # pre_init precisa ocorrer antes de pygame.init para definir o formato
        # usado pelo áudio procedural: 44,1 kHz, 16 bits, estéreo.
        pygame.mixer.pre_init(44_100, -16, 2, 512)
        pygame.init(); pygame.display.set_caption(TITLE)
        self.screen, self.clock = pygame.display.set_mode((WIDTH, HEIGHT)), pygame.time.Clock()
        self.fonts = {"small": pygame.font.SysFont("consolas", 16), "body": pygame.font.SysFont("consolas", 22), "title": pygame.font.SysFont("consolas", 52, bold=True)}
        self.running, self.high_score, self.state = True, SaveData.load_high_score(), "menu"
        self.stars = [(random.randrange(WIDTH), random.randrange(HEIGHT), random.choice((1, 1, 1, 2, 2, 3))) for _ in range(115)]
        self.sound = SoundManager()
        self.sound.start_ambient()
        self.reset()

    def reset(self):
        """Cria uma partida, preservando somente o recorde histórico."""
        self.player = Player(); self.enemies, self.bullets, self.particles = [], [], []
        self.director, self.score, self.combo, self.combo_timer = WaveDirector(), 0, 0, 0.0
        self.message, self.message_timer = "", 0.0

    def run(self):
        while self.running:
            # dt em segundos deixa o jogo consistente em computadores diferentes.
            dt = min(self.clock.tick(FPS) / 1000, .05)
            self.handle_events()
            if self.state == "playing": self.update(dt)
            self.draw()
        self.sound.stop()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing": self.state = "paused"
                    elif self.state == "paused": self.state = "playing"
                    else: self.running = False
                elif event.key in (pygame.K_RETURN, pygame.K_r) and self.state in ("menu", "game_over"):
                    self.reset(); self.state = "playing"; self.sound.play("start")
                elif event.key == pygame.K_p and self.state in ("playing", "paused"):
                    self.state = "paused" if self.state == "playing" else "playing"
                elif event.key == pygame.K_SPACE and self.state == "playing":
                    shots = self.player.shoot()
                    self.bullets.extend(shots)
                    if shots: self.sound.play("player_shot")

    def update(self, dt):
        keys = pygame.key.get_pressed(); self.player.update(dt, keys, self.particles)
        # Segurar espaço é confortável num arcade; shoot impõe a cadência.
        if keys[pygame.K_SPACE]:
            shots = self.player.shoot()
            self.bullets.extend(shots)
            if shots: self.sound.play("player_shot")
        if self.director.update(dt, self.enemies):
            self.message, self.message_timer = f"ONDA {self.director.wave}", 1.5
            self.sound.play("wave")
        self.message_timer -= dt; self.combo_timer -= dt
        if self.combo_timer <= 0: self.combo = 0
        for enemy in self.enemies[:]:
            shot = enemy.update(dt, self.player.pos)
            if shot:
                self.bullets.append(shot)
                self.sound.play("enemy_shot")
            if enemy.pos.y > HEIGHT + enemy.radius:
                self.enemies.remove(enemy)
                if self.player.hit(enemy.damage):
                    explosion(self.particles, self.player.pos, RED, 12); self.sound.play("hit")
        for bullet in self.bullets[:]:
            if not bullet.update(dt): self.bullets.remove(bullet)
        # Cópias ([:]) permitem remover itens durante a iteração com segurança.
        for bullet in self.bullets[:]:
            if bullet.friendly:
                for enemy in self.enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        if bullet in self.bullets: self.bullets.remove(bullet)
                        enemy.health -= bullet.damage; explosion(self.particles, bullet.pos, CYAN, 4)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy); self.combo += 1; self.combo_timer = 2.2
                            self.score += enemy.score + self.combo * 2; explosion(self.particles, enemy.pos, enemy.color, 22); self.sound.play("explosion")
                        break
            elif bullet.rect.colliderect(self.player.rect):
                self.bullets.remove(bullet)
                if self.player.hit(bullet.damage):
                    explosion(self.particles, self.player.pos, RED, 13); self.sound.play("hit")
        for enemy in self.enemies[:]:
            if enemy.rect.colliderect(self.player.rect):
                self.enemies.remove(enemy)
                if self.player.hit(enemy.damage * 2):
                    explosion(self.particles, enemy.pos, ORANGE, 24); self.sound.play("hit")
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.life <= 0: self.particles.remove(particle)
        if self.player.health <= 0:
            if self.score > self.high_score: self.high_score = self.score; SaveData.save_high_score(self.high_score)
            self.sound.play("game_over")
            self.state = "game_over"

    def draw_background(self):
        self.screen.fill(BACKGROUND)
        for x, y, size in self.stars:
            pygame.draw.circle(self.screen, (80 + size * 35, 100 + size * 30, 155 + size * 25), (x, y), size)
        pygame.draw.line(self.screen, (22, 37, 71), (0, HEIGHT * .43), (WIDTH, HEIGHT * .43), 1)

    def draw_hud(self):
        bar(self.screen, pygame.Rect(25, 25, 250, 27), self.player.health, self.player.max_health, GREEN, "CASCO", self.fonts["small"])
        bar(self.screen, pygame.Rect(25, 60, 250, 22), self.player.energy, 100, CYAN, "ENERGIA", self.fonts["small"])
        text(self.screen, self.fonts["body"], f"PONTOS  {self.score:06d}", (WIDTH - 28, 30), CYAN, "topright")
        text(self.screen, self.fonts["small"], f"RECORDE  {self.high_score:06d}", (WIDTH - 28, 60), MUTED, "topright")
        text(self.screen, self.fonts["body"], f"ONDA {self.director.wave}", (WIDTH / 2, 27), WHITE)
        if self.combo > 2: text(self.screen, self.fonts["body"], f"COMBO x{self.combo}", (WIDTH / 2, 58), YELLOW)

    def draw_overlay(self, title, lines, accent=CYAN):
        rect = pygame.Rect(WIDTH // 2 - 285, HEIGHT // 2 - 175, 570, 350); panel(self.screen, rect)
        text(self.screen, self.fonts["title"], title, (rect.centerx, rect.y + 74), accent)
        for index, (line, color) in enumerate(lines): text(self.screen, self.fonts["body"], line, (rect.centerx, rect.y + 145 + index * 34), color)

    def draw(self):
        self.draw_background()
        if self.state != "menu":
            for particle in self.particles: particle.draw(self.screen)
            for bullet in self.bullets: bullet.draw(self.screen)
            for enemy in self.enemies: enemy.draw(self.screen)
            self.player.draw(self.screen); self.draw_hud()
            if self.message_timer > 0: text(self.screen, self.fonts["title"], self.message, (WIDTH / 2, HEIGHT * .36), CYAN)
        if self.state == "menu": self.draw_overlay("NEBULA SENTINEL", [("DEFENDA A FRONTEIRA ESTELAR", MUTED), ("WASD / SETAS  ·  mover", WHITE), ("ESPAÇO  ·  disparar", WHITE), ("ENTER  ·  iniciar missão", GREEN), (f"RECORDE ATUAL  {self.high_score:06d}", YELLOW)])
        elif self.state == "paused": self.draw_overlay("PAUSADO", [("P ou ESC  ·  continuar", WHITE), ("A galáxia espera por você.", MUTED)], YELLOW)
        elif self.state == "game_over": self.draw_overlay("MISSÃO ENCERRADA", [(f"PONTUAÇÃO FINAL  {self.score:06d}", WHITE), (f"ONDA ALCANÇADA  {self.director.wave}", MUTED), ("ENTER ou R  ·  nova missão", GREEN)], RED)
        pygame.display.flip()
