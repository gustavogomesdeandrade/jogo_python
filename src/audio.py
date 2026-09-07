"""Áudio procedural do jogo, criado matematicamente em vez de usar arquivos WAV.

Essa abordagem mantém o repositório pequeno e mostra que um som digital é,
essencialmente, uma sequência rápida de números que descrevem uma onda.
"""

from __future__ import annotations

from array import array
import math
import random

import pygame


class SoundManager:
    """Cria e reproduz efeitos; falha silenciosamente se não houver dispositivo.

    É comum executar jogos em ambientes sem placa de áudio (servidores, testes
    automatizados). Por isso o jogo continua funcionando mesmo se o mixer não
    puder ser inicializado.
    """

    SAMPLE_RATE = 44_100

    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.effects = {}
        self.music_channel = None
        if not self.enabled:
            return

        self.effects = {
            "player_shot": self._tone(.075, 820, 310, .22, "square"),
            "enemy_shot": self._tone(.10, 230, 125, .15, "sine"),
            "hit": self._tone(.13, 150, 55, .25, "noise"),
            "explosion": self._tone(.28, 110, 24, .30, "noise"),
            "wave": self._tone(.38, 330, 880, .20, "sine"),
            "start": self._tone(.25, 440, 660, .20, "sine"),
            "game_over": self._tone(.50, 300, 65, .25, "sine"),
        }
        self.ambient = self._ambient_loop()

    def _tone(self, duration, start_frequency, end_frequency, volume, wave_type):
        """Converte uma onda matemática em um objeto ``pygame.mixer.Sound``.

        A frequência muda ao longo do tempo para criar um "sweep", muito útil
        em sons de ficção científica. A envoltória reduz o volume no início e
        no fim, evitando estalos digitais.
        """
        samples = array("h")
        count = int(duration * self.SAMPLE_RATE)
        phase = 0.0
        for index in range(count):
            progress = index / count
            frequency = start_frequency + (end_frequency - start_frequency) * progress
            phase += math.tau * frequency / self.SAMPLE_RATE
            envelope = min(1, index / max(1, int(self.SAMPLE_RATE * .008))) * (1 - progress) ** 1.7
            if wave_type == "square":
                value = 1.0 if math.sin(phase) >= 0 else -1.0
            elif wave_type == "noise":
                # Ruído filtrado por uma senoide produz uma explosão menos áspera.
                value = random.uniform(-1, 1) * (0.45 + .55 * math.sin(phase))
            else:
                value = math.sin(phase)
            sample = int(32_767 * volume * envelope * value)
            samples.extend((sample, sample))  # mixer configurado em estéreo
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _ambient_loop(self):
        """Gera uma ambiência discreta de espaço profundo para tocar em loop."""
        samples = array("h")
        duration = 5.0
        count = int(duration * self.SAMPLE_RATE)
        for index in range(count):
            time = index / self.SAMPLE_RATE
            # Três osciladores lentos dão textura sem competir com os efeitos.
            value = (math.sin(math.tau * 55 * time) * .38 + math.sin(math.tau * 82.4 * time) * .22 + math.sin(math.tau * 0.17 * time) * .12)
            # Fade suave nas bordas reduz a transição perceptível do loop.
            edge = min(1, index / (self.SAMPLE_RATE * .35), (count - index) / (self.SAMPLE_RATE * .35))
            sample = int(32_767 * .11 * value * edge)
            samples.extend((sample, sample))
        sound = pygame.mixer.Sound(buffer=samples.tobytes())
        sound.set_volume(.45)
        return sound

    def play(self, name):
        """Toca um efeito se o mixer estiver disponível."""
        if self.enabled and name in self.effects:
            self.effects[name].play()

    def start_ambient(self):
        """Inicia a ambiência uma única vez, em um canal separado dos efeitos."""
        if self.enabled and self.music_channel is None:
            self.music_channel = self.ambient.play(loops=-1)

    def stop(self):
        """Libera os canais quando a aplicação é encerrada."""
        if self.enabled:
            pygame.mixer.stop()
