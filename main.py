"""Ponto de entrada do jogo.

Execute este arquivo com ``python main.py`` depois de instalar as dependências.
Manter o ponto de entrada pequeno é uma convenção útil: o código do jogo fica
organizado dentro do pacote ``src`` e este arquivo só inicia a aplicação.
"""

from src.game import Game


if __name__ == "__main__":
    Game().run()
