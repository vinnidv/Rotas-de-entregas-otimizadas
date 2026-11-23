import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rotas.grafo import Grafo, dijkstra, matriz_distancias, reconstruir_caminho
from rotas.heuristicas import (distancia_rota, dois_opt, forca_bruta,
                               vizinho_mais_proximo)
from rotas.simulacao import gerar_malha, sortear_paradas


def grafo_exemplo():
    g = Grafo()
    for u, v, w in [(0, 1, 7), (0, 2, 9), (0, 5, 14), (1, 2, 10), (1, 3, 15),
                    (2, 3, 11), (2, 5, 2), (3, 4, 6), (4, 5, 9)]:
        g.adicionar_aresta(u, v, w)
    return g


class TesteDijkstra(unittest.TestCase):
    def test_distancias_conhecidas(self):
        dist, _ = dijkstra(grafo_exemplo(), 0)
        self.assertEqual([dist[i] for i in range(6)], [0, 7, 9, 20, 20, 11])

    def test_caminho(self):
        _, ant = dijkstra(grafo_exemplo(), 0)
        self.assertEqual(reconstruir_caminho(ant, 0, 4), [0, 2, 5, 4])

    def test_peso_negativo(self):
        with self.assertRaises(ValueError):
            Grafo().adicionar_aresta(0, 1, -1)

    def test_matriz_simetrica(self):
        m, _ = matriz_distancias(grafo_exemplo(), [0, 3, 4])
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(m[i][j], m[j][i])


class TesteRotas(unittest.TestCase):
    def setUp(self):
        self.g = gerar_malha(seed=3)
        self.v = sortear_paradas(self.g, 8, seed=3)
        self.m, _ = matriz_distancias(self.g, self.v)

    def test_malha_conexa(self):
        self.assertTrue(self.g.conexo())

    def test_rotas_validas(self):
        for rota in (vizinho_mais_proximo(self.m),
                     dois_opt(vizinho_mais_proximo(self.m), self.m)):
            self.assertEqual(sorted(rota), list(range(len(self.v))))
            self.assertEqual(rota[0], 0)

    def test_2opt_nao_piora(self):
        nn = vizinho_mais_proximo(self.m)
        self.assertLessEqual(distancia_rota(dois_opt(nn, self.m), self.m),
                             distancia_rota(nn, self.m) + 1e-9)

    def test_otimo_e_limite_inferior(self):
        otimo = distancia_rota(forca_bruta(self.m), self.m)
        nn = distancia_rota(vizinho_mais_proximo(self.m), self.m)
        self.assertLessEqual(otimo, nn + 1e-9)


if __name__ == "__main__":
    unittest.main()
