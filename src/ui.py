"""Funções pequenas para desenhar a interface do usuário."""

import pygame

from .config import CYAN, PANEL, WHITE


def text(surface, font, message, position, color=WHITE, anchor="center"):
    """Renderiza texto e devolve o rect, útil para alinhar outros elementos."""
    image = font.render(str(message), True, color)
    rect = image.get_rect()
    setattr(rect, anchor, position)
    surface.blit(image, rect)
    return rect


def bar(surface, rect, value, maximum, fill, label, font):
    """Desenha uma barra com preenchimento proporcional e rótulo."""
    pygame.draw.rect(surface, PANEL, rect, border_radius=7)
    pygame.draw.rect(surface, (52, 68, 104), rect, 2, border_radius=7)
    ratio = max(0, min(value / maximum, 1)) if maximum else 0
    inner = rect.inflate(-6, -6)
    inner.width = int(inner.width * ratio)
    if inner.width:
        pygame.draw.rect(surface, fill, inner, border_radius=4)
    text(surface, font, label, (rect.centerx, rect.centery), WHITE)


def panel(surface, rect, alpha=225):
    """Cria um painel semitransparente em uma camada separada."""
    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(layer, (*PANEL, alpha), layer.get_rect(), border_radius=18)
    pygame.draw.rect(layer, (*CYAN, 80), layer.get_rect(), 2, border_radius=18)
    surface.blit(layer, rect)
