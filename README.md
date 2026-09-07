# Nebula Sentinel

Um jogo arcade espacial feito em Python e Pygame, pensado também como material
de estudo. Todo o visual e os efeitos sonoros são desenhados por código: não há
imagens ou arquivos de áudio externos para configurar.

## Como executar

1. Crie um ambiente virtual (recomendado): `python -m venv .venv`
2. Ative-o: `source .venv/bin/activate` (Linux/macOS) ou `.venv\\Scripts\\activate` (Windows)
3. Instale a biblioteca: `pip install -r requirements.txt`
4. Inicie: `python main.py`

## Controles

| Tecla | Ação |
|---|---|
| `WASD` ou setas | Mover a nave |
| `Espaço` | Atirar |
| `P` ou `Esc` | Pausar / voltar |
| `Enter` | Começar ou recomeçar |
| `R` | Recomeçar após uma derrota |

## Estrutura

```text
.
├── main.py             # ponto de entrada
├── requirements.txt    # biblioteca necessária
├── data/               # recorde salvo localmente (criado ao jogar)
└── src/
    ├── config.py       # constantes e paleta
    ├── audio.py         # efeitos e ambiência sintetizados matematicamente
    ├── entities.py     # nave, inimigos, tiros e partículas
    ├── game.py         # loop principal e estados das telas
    ├── systems.py      # ondas, colisões e pontuação
    └── ui.py           # elementos de interface reutilizáveis
```

## Ideias para expandir

- Adicionar novas formações de inimigos em `WaveDirector`.
- Criar chefes para cada cinco ondas.
- Trocar os desenhos procedurais por sprites próprios.
- Adicionar efeitos sonoros usando `pygame.mixer`.
