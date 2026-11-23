"""Grafo não direcionado ponderado (lista de adjacência) e algoritmo de Dijkstra."""
import heapq
from math import inf


class Grafo:
    """Grafo não direcionado com pesos em km. Os vértices são inteiros."""

    def __init__(self):
        self.adj = {}      # vértice -> lista de (vizinho, peso)
        self.coord = {}    # vértice -> (latitude, longitude)

    def adicionar_vertice(self, v, lat=None, lon=None):
        self.adj.setdefault(v, [])
        if lat is not None:
            self.coord[v] = (lat, lon)

    def adicionar_aresta(self, u, v, peso):
        if peso < 0:
            raise ValueError("Dijkstra exige pesos não negativos")
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)
        self.adj[u].append((v, peso))
        self.adj[v].append((u, peso))

    def vertices(self):
        return list(self.adj)

    def num_arestas(self):
        return sum(len(l) for l in self.adj.values()) // 2

    def componente(self, inicio):
        """Conjunto de vértices alcançáveis a partir de 'inicio' (busca em largura)."""
        visto = {inicio}
        fila = [inicio]
        while fila:
            u = fila.pop(0)
            for v, _ in self.adj[u]:
                if v not in visto:
                    visto.add(v)
                    fila.append(v)
        return visto

    def conexo(self):
        if not self.adj:
            return True
        return len(self.componente(next(iter(self.adj)))) == len(self.adj)


def dijkstra(grafo, origem):
    """Caminhos mínimos a partir de 'origem'.

    Usa fila de prioridade (heap binário). Complexidade O((V + E) log V).
    Retorna (dist, anterior): dicionários de distância e de predecessor.
    """
    dist = {v: inf for v in grafo.adj}
    anterior = {v: None for v in grafo.adj}
    dist[origem] = 0.0
    fila = [(0.0, origem)]
    while fila:
        d, u = heapq.heappop(fila)
        if d > dist[u]:
            continue  # entrada obsoleta da fila
        for v, peso in grafo.adj[u]:
            nd = d + peso
            if nd < dist[v]:
                dist[v] = nd
                anterior[v] = u
                heapq.heappush(fila, (nd, v))
    return dist, anterior


def reconstruir_caminho(anterior, origem, destino):
    """Lista de vértices do caminho mínimo origem -> destino."""
    caminho = []
    v = destino
    while v is not None:
        caminho.append(v)
        if v == origem:
            break
        v = anterior[v]
    caminho.reverse()
    if not caminho or caminho[0] != origem:
        raise ValueError("destino inalcançável")
    return caminho


def matriz_distancias(grafo, pontos):
    """Matriz simétrica de distâncias mínimas entre os 'pontos' (lista de vértices).

    Executa um Dijkstra por ponto. Retorna também os predecessores de cada
    execução, usados depois para desenhar o percurso real nas ruas.
    """
    n = len(pontos)
    matriz = [[0.0] * n for _ in range(n)]
    antes = []
    for i, p in enumerate(pontos):
        dist, ant = dijkstra(grafo, p)
        antes.append(ant)
        for j, q in enumerate(pontos):
            matriz[i][j] = dist[q]
    return matriz, antes
