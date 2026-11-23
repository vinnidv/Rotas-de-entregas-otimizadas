# Otimização de rotas de entrega com grafos

Projeto Integrador: Laboratório de Programação — Universidade Santo Amaro (UNISA).

Programa em Python que define a ordem de visita das paradas de um entregador
parceiro de plataforma de e-commerce, reduzindo a distância total percorrida.

## Como funciona

1. As paradas (e a base, ponto de partida e de retorno) são lidas de um CSV ou geradas por simulação.
2. As ruas são modeladas como um grafo ponderado (lista de adjacência).
3. O algoritmo de Dijkstra, com fila de prioridade (heap), calcula a matriz de menores distâncias entre as paradas.
4. As heurísticas do vizinho mais próximo e do 2-opt definem a ordem de visita.
5. O programa compara o resultado com duas linhas de base (ordem de chegada e varredura angular) e estima o custo de combustível (parâmetros hipotéticos e ajustáveis em `rotas/simulacao.py`).

## Requisitos

Python 3.9 ou superior. O programa principal usa apenas a biblioteca padrão.
Para gerar as figuras dos experimentos: `pip install -r requirements.txt`.

## Execução

```
python main.py --demo                       # simulação com 20 paradas
python main.py --demo --paradas 30 --seed 5 # outro tamanho e semente
python main.py --entrada dados/exemplo_paradas.csv
python experimentos.py                      # reproduz tabelas e figuras do artigo
python -m unittest discover -s testes -v    # testes automatizados
```

Formato do CSV: `nome,latitude,longitude`. A primeira linha de dados é a base.
Use coordenadas aproximadas (por exemplo, o centro do bairro) e nunca endereços
completos de clientes, em respeito à Lei Geral de Proteção de Dados (Lei nº 13.709/2018).

## Estrutura

```
main.py              programa principal (linha de comando)
experimentos.py      experimentos, tabelas (CSV) e figuras
rotas/geo.py         distância haversine
rotas/grafo.py       grafo, Dijkstra, matriz de distâncias
rotas/heuristicas.py rotas: ordem de chegada, varredura, vizinho mais próximo, 2-opt, força bruta
rotas/simulacao.py   malha viária e paradas simuladas, custo de combustível
rotas/entrada.py     leitura de CSV e montagem do grafo
testes/              testes unitários
dados/               exemplo de entrada
resultados/          saídas dos experimentos
```

## Limitações

Dados simulados; sem trânsito, ruas de mão única, janelas de horário ou capacidade do veículo.
