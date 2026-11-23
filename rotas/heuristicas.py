"""Construção e melhoria de rotas sobre uma matriz de distâncias.

Convenção: o ponto 0 é a base (ponto de partida e de retorno). Uma rota é a
lista de índices dos pontos na ordem de visita, começando em 0 e sem repetir
o 0 no final; o retorno à base é considerado no cálculo da distância.
"""
from itertools import permutations
from math import atan2


def distancia_rota(rota, matriz, retornar_base=True):
    total = 0.0
    for a, b in zip(rota, rota[1:]):
        total += matriz[a][b]
    if retornar_base:
        total += matriz[rota[-1]][rota[0]]
    return total


def ordem_chegada(n):
    """Linha de base 1: entregas na ordem em que os pacotes foram recebidos."""
    return list(range(n))


def varredura_angular(coordenadas):
    """Linha de base 2: agrupa as paradas por direção em torno da base.

    Imita o entregador experiente que "faz um lado de cada vez". Ordena as
    paradas pelo ângulo em relação à base (índice 0).
    """
    lat0, lon0 = coordenadas[0]
    indices = list(range(1, len(coordenadas)))
    indices.sort(key=lambda i: atan2(coordenadas[i][0] - lat0, coordenadas[i][1] - lon0))
    return [0] + indices


def vizinho_mais_proximo(matriz):
    """Heurística construtiva: sempre vai à parada não visitada mais próxima."""
    n = len(matriz)
    visitado = [False] * n
    rota = [0]
    visitado[0] = True
    atual = 0
    for _ in range(n - 1):
        melhor, melhor_d = None, float("inf")
        for j in range(n):
            if not visitado[j] and matriz[atual][j] < melhor_d:
                melhor, melhor_d = j, matriz[atual][j]
        rota.append(melhor)
        visitado[melhor] = True
        atual = melhor
    return rota


def dois_opt(rota, matriz):
    """Melhoria local 2-opt: inverte trechos da rota enquanto isso reduzir a distância."""
    rota = list(rota)
    n = len(rota)
    melhorou = True
    while melhorou:
        melhorou = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a, b = rota[i - 1], rota[i]
                c = rota[j]
                d = rota[(j + 1) % n]
                antes = matriz[a][b] + matriz[c][d]
                depois = matriz[a][c] + matriz[b][d]
                if depois < antes - 1e-12:
                    rota[i:j + 1] = reversed(rota[i:j + 1])
                    melhorou = True
    return rota


def forca_bruta(matriz):
    """Solução ótima por enumeração de todas as permutações (só para n pequeno)."""
    n = len(matriz)
    if n > 10:
        raise ValueError("força bruta limitada a 9 paradas")
    melhor, melhor_d = None, float("inf")
    for perm in permutations(range(1, n)):
        rota = [0] + list(perm)
        d = distancia_rota(rota, matriz)
        if d < melhor_d:
            melhor, melhor_d = rota, d
    return melhor
