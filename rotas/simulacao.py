"""Geração de dados simulados: malha viária sintética e paradas de entrega.

Nenhum dado real de clientes é utilizado. A malha imita um conjunto de ruas
em grade, com quarteirões de tamanhos variados, algumas ruas interrompidas e
curvas que tornam o percurso real maior que a linha reta.
"""
import random

from .geo import haversine
from .grafo import Grafo

# Referência geográfica aproximada (zona sul de São Paulo - SP), apenas para
# dar ordem de grandeza realista às distâncias.
LAT_BASE = -23.6500
LON_BASE = -46.7000
GRAUS_POR_KM_LAT = 1 / 111.0
GRAUS_POR_KM_LON = 1 / 102.0


def gerar_malha(lado=20, espacamento_km=0.30, prob_remocao=0.10, seed=0):
    """Cria um grafo em grade lado x lado.

    - Cada cruzamento recebe um deslocamento aleatório (ruas não são perfeitas).
    - O peso de cada trecho é a distância em linha reta vezes um fator de
      sinuosidade entre 1,00 e 1,30.
    - Uma fração das ruas é removida, desde que o grafo continue conexo.
    """
    rng = random.Random(seed)
    g = Grafo()
    ident = lambda r, c: r * lado + c
    for r in range(lado):
        for c in range(lado):
            dx = rng.uniform(-0.25, 0.25) * espacamento_km
            dy = rng.uniform(-0.25, 0.25) * espacamento_km
            lat = LAT_BASE + (r * espacamento_km + dy) * GRAUS_POR_KM_LAT
            lon = LON_BASE + (c * espacamento_km + dx) * GRAUS_POR_KM_LON
            g.adicionar_vertice(ident(r, c), lat, lon)

    arestas = []
    for r in range(lado):
        for c in range(lado):
            if c + 1 < lado:
                arestas.append((ident(r, c), ident(r, c + 1)))
            if r + 1 < lado:
                arestas.append((ident(r, c), ident(r + 1, c)))
    rng.shuffle(arestas)
    removidas = set(arestas[: int(len(arestas) * prob_remocao)])

    for u, v in arestas:
        if (u, v) in removidas:
            continue
        g.adicionar_aresta(u, v, _peso(g, u, v, rng))
    # Reinsere ruas removidas apenas se necessário para manter a conexão.
    for u, v in arestas:
        if (u, v) in removidas and not g.conexo():
            if v not in g.componente(u):
                g.adicionar_aresta(u, v, _peso(g, u, v, rng))
    return g


def _peso(g, u, v, rng):
    lat1, lon1 = g.coord[u]
    lat2, lon2 = g.coord[v]
    return haversine(lat1, lon1, lat2, lon2) * rng.uniform(1.00, 1.30)


def sortear_paradas(grafo, n_paradas, seed=0):
    """Escolhe a base e as paradas entre os vértices do grafo.

    Retorna a lista de vértices; a posição 0 é a base. A lista de pacotes
    já vem embaralhada, representando a ordem de chegada dos pacotes.
    """
    rng = random.Random(seed + 10_000)
    escolhidos = rng.sample(grafo.vertices(), n_paradas + 1)
    return escolhidos


def custo_combustivel(km, km_por_litro=30.0, preco_litro=6.00):
    """Custo estimado de combustível em reais (parâmetros hipotéticos)."""
    return km / km_por_litro * preco_litro
