"""Programa principal: calcula e compara rotas de entrega.

Uso:
    python main.py --demo                      # simulação com 20 paradas
    python main.py --demo --paradas 30 --seed 5
    python main.py --entrada dados/exemplo_paradas.csv
"""
import argparse
import time

from rotas.entrada import ler_csv, montar_grafo
from rotas.grafo import matriz_distancias
from rotas.heuristicas import (distancia_rota, dois_opt, ordem_chegada,
                               varredura_angular, vizinho_mais_proximo)
from rotas.simulacao import custo_combustivel, gerar_malha, sortear_paradas


def calcular(grafo, vertices):
    """Executa todos os métodos e devolve um dicionário de resultados."""
    coords = [grafo.coord[v] for v in vertices]
    matriz, _ = matriz_distancias(grafo, vertices)
    resultados = {}

    def registrar(nome, funcao):
        t0 = time.perf_counter()
        rota = funcao()
        tempo = time.perf_counter() - t0
        resultados[nome] = {
            "rota": rota,
            "km": distancia_rota(rota, matriz),
            "tempo_s": tempo,
        }

    registrar("Ordem de chegada", lambda: ordem_chegada(len(vertices)))
    registrar("Varredura angular", lambda: varredura_angular(coords))
    registrar("Vizinho mais próximo", lambda: vizinho_mais_proximo(matriz))
    registrar("Vizinho mais próximo + 2-opt",
              lambda: dois_opt(vizinho_mais_proximo(matriz), matriz))
    return resultados, matriz


def imprimir(resultados, nomes=None):
    base = resultados["Ordem de chegada"]["km"]
    print(f"{'Método':<32}{'Distância (km)':>16}{'Economia':>12}{'Combustível (R$)':>20}")
    for nome, r in resultados.items():
        eco = 100 * (base - r["km"]) / base
        print(f"{nome:<32}{r['km']:>16.2f}{eco:>11.1f}%{custo_combustivel(r['km']):>20.2f}")
    melhor = min(resultados, key=lambda k: resultados[k]["km"])
    rota = resultados[melhor]["rota"]
    print(f"\nMelhor rota ({melhor}):")
    ordem = [nomes[i] if nomes else f"Parada {i}" for i in rota]
    print("  " + " -> ".join(ordem) + " -> " + ordem[0])


def main():
    p = argparse.ArgumentParser(description="Otimização de rotas de entrega")
    p.add_argument("--demo", action="store_true", help="usa dados simulados")
    p.add_argument("--entrada", help="arquivo CSV com nome,latitude,longitude")
    p.add_argument("--paradas", type=int, default=20)
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args()

    if a.entrada:
        pontos = ler_csv(a.entrada)
        grafo = montar_grafo(pontos)
        vertices = list(range(len(pontos)))
        nomes = [n for n, _, _ in pontos]
    elif a.demo:
        grafo = gerar_malha(seed=a.seed)
        vertices = sortear_paradas(grafo, a.paradas, seed=a.seed)
        nomes = ["Base"] + [f"Parada {i}" for i in range(1, len(vertices))]
    else:
        p.error("use --demo ou --entrada arquivo.csv")

    resultados, _ = calcular(grafo, vertices)
    imprimir(resultados, nomes)


if __name__ == "__main__":
    main()
