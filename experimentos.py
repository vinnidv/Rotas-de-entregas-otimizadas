"""Experimentos: compara os métodos em instâncias simuladas e gera tabelas e figuras.

Saídas em resultados/: resumo_por_tamanho.csv, gap_otimo.csv, figuras PNG.
"""
import csv
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from main import calcular
from rotas.grafo import matriz_distancias, reconstruir_caminho, dijkstra
from rotas.heuristicas import distancia_rota, forca_bruta
from rotas.simulacao import custo_combustivel, gerar_malha, sortear_paradas

TAMANHOS = [10, 20, 30, 40, 50]
INSTANCIAS = 30
METODOS = ["Ordem de chegada", "Varredura angular",
           "Vizinho mais próximo", "Vizinho mais próximo + 2-opt"]
CORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]


def resumo_por_tamanho():
    linhas = []
    for n in TAMANHOS:
        km = {m: [] for m in METODOS}
        tempo = {m: [] for m in METODOS}
        for s in range(INSTANCIAS):
            g = gerar_malha(seed=1000 * n + s)
            v = sortear_paradas(g, n, seed=1000 * n + s)
            res, _ = calcular(g, v)
            for m in METODOS:
                km[m].append(res[m]["km"])
                tempo[m].append(res[m]["tempo_s"])
        base = st.mean(km["Ordem de chegada"])
        for m in METODOS:
            media = st.mean(km[m])
            linhas.append({
                "paradas": n, "metodo": m,
                "km_media": round(media, 2),
                "km_desvio": round(st.stdev(km[m]), 2),
                "economia_pct": round(100 * (base - media) / base, 1),
                "tempo_ms": round(1000 * st.mean(tempo[m]), 3),
            })
    return linhas


def gap_otimo(n=8):
    linhas = []
    for s in range(INSTANCIAS):
        g = gerar_malha(seed=7000 + s)
        v = sortear_paradas(g, n, seed=7000 + s)
        res, m = calcular(g, v)
        otimo = distancia_rota(forca_bruta(m), m)
        linha = {"instancia": s, "otimo_km": otimo}
        for met in METODOS:
            linha[met] = res[met]["km"]
        linhas.append(linha)
    return linhas


def salvar_csv(caminho, linhas):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)


def estilo(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.grid(axis="y", color="#e5e4e0", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors="#52514e", labelsize=9)


def figura_linhas(resumo):
    fig, ax = plt.subplots(figsize=(7, 4), dpi=200)
    for m, cor in zip(METODOS, CORES):
        pts = [(r["paradas"], r["km_media"]) for r in resumo if r["metodo"] == m]
        ax.plot(*zip(*pts), color=cor, linewidth=2, marker="o", markersize=5,
                markeredgecolor="white", markeredgewidth=1.2, label=m)
    ax.set_xlabel("Número de paradas", fontsize=10, color="#52514e")
    ax.set_ylabel("Distância média (km)", fontsize=10, color="#52514e")
    ax.set_xticks(TAMANHOS)
    estilo(ax)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig("resultados/fig_distancia_por_paradas.png")
    plt.close(fig)


def figura_mapa(n=20, seed=1):
    g = gerar_malha(seed=seed)
    v = sortear_paradas(g, n, seed=seed)
    res, m = calcular(g, v)
    fig, eixos = plt.subplots(1, 2, figsize=(9, 4.8), dpi=200)
    titulos = [("Ordem de chegada", CORES[0]), ("Vizinho mais próximo + 2-opt", CORES[2])]
    for ax, (nome, cor) in zip(eixos, titulos):
        for u in g.adj:
            for w, _ in g.adj[u]:
                if u < w:
                    (la1, lo1), (la2, lo2) = g.coord[u], g.coord[w]
                    ax.plot([lo1, lo2], [la1, la2], color="#dcdbd6", linewidth=0.5, zorder=1)
        rota = res[nome]["rota"]
        for a, b in zip(rota, rota[1:] + [rota[0]]):
            _, ant = dijkstra(g, v[a])
            cam = reconstruir_caminho(ant, v[a], v[b])
            xs = [g.coord[c][1] for c in cam]
            ys = [g.coord[c][0] for c in cam]
            ax.plot(xs, ys, color=cor, linewidth=1.6, alpha=0.9, zorder=2)
        for i, vert in enumerate(v):
            lat, lon = g.coord[vert]
            if i == 0:
                ax.scatter(lon, lat, s=70, color="#0b0b0b", marker="s", zorder=4)
            else:
                ax.scatter(lon, lat, s=22, color="white", edgecolor=cor, linewidth=1.5, zorder=3)
        ax.set_title(f"{nome}\n{res[nome]['km']:.1f} km", fontsize=10, color="#0b0b0b")
        ax.set_aspect("equal")
        ax.axis("off")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig("resultados/fig_mapa_rotas.png")
    plt.close(fig)
    return res


if __name__ == "__main__":
    resumo = resumo_por_tamanho()
    salvar_csv("resultados/resumo_por_tamanho.csv", resumo)
    gaps = gap_otimo()
    salvar_csv("resultados/gap_otimo.csv", gaps)
    figura_linhas(resumo)
    figura_mapa()
    print("\nResumo por tamanho (média de", INSTANCIAS, "instâncias)")
    for r in resumo:
        print(r)
    print("\nGap em relação ao ótimo (8 paradas):")
    for met in METODOS:
        g = [100 * (x[met] - x["otimo_km"]) / x["otimo_km"] for x in gaps]
        print(f"{met:<32} média {st.mean(g):6.2f}%  máx {max(g):6.2f}%  "
              f"ótimas {sum(1 for y in g if y < 1e-6)}/{len(g)}")
    n30 = [r for r in resumo if r["paradas"] == 30]
    base = next(r for r in n30 if r["metodo"] == "Ordem de chegada")["km_media"]
    best = next(r for r in n30 if r["metodo"] == "Vizinho mais próximo + 2-opt")["km_media"]
    print(f"\n30 paradas: {base:.2f} -> {best:.2f} km; combustível/dia "
          f"R$ {custo_combustivel(base):.2f} -> R$ {custo_combustivel(best):.2f}")
