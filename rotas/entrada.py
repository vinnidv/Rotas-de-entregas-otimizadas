"""Leitura de paradas a partir de um arquivo CSV e montagem do grafo viário.

Formato do CSV (cabeçalho obrigatório):  nome,latitude,longitude
A primeira linha de dados é a BASE (ponto de partida e de retorno).
Recomenda-se usar coordenadas aproximadas (por exemplo, o centro do bairro) e
não endereços completos de clientes, em respeito à LGPD.

Como o arquivo traz apenas as paradas, as ligações entre elas são montadas por
vizinhança: cada ponto é ligado aos k pontos mais próximos, com peso igual à
distância em linha reta multiplicada por um fator de sinuosidade.
"""
import csv

from .geo import haversine
from .grafo import Grafo


def ler_csv(caminho):
    pontos = []
    with open(caminho, newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            pontos.append((linha["nome"], float(linha["latitude"]), float(linha["longitude"])))
    if len(pontos) < 3:
        raise ValueError("informe a base e pelo menos duas paradas")
    return pontos


def montar_grafo(pontos, k=4, sinuosidade=1.2):
    g = Grafo()
    for i, (_, lat, lon) in enumerate(pontos):
        g.adicionar_vertice(i, lat, lon)
    n = len(pontos)
    for i in range(n):
        dists = sorted(
            (haversine(pontos[i][1], pontos[i][2], pontos[j][1], pontos[j][2]), j)
            for j in range(n) if j != i
        )
        for d, j in dists[:k]:
            if not any(v == j for v, _ in g.adj[i]):
                g.adicionar_aresta(i, j, d * sinuosidade)
    # Garante conexão ligando componentes isolados pelo par de pontos mais próximo.
    while not g.conexo():
        comp = g.componente(0)
        melhor = min(
            ((haversine(pontos[i][1], pontos[i][2], pontos[j][1], pontos[j][2]), i, j)
             for i in comp for j in range(n) if j not in comp)
        )
        g.adicionar_aresta(melhor[1], melhor[2], melhor[0] * sinuosidade)
    return g
