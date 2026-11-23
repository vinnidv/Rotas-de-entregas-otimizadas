"""Funções geográficas auxiliares."""
from math import radians, sin, cos, asin, sqrt

RAIO_TERRA_KM = 6371.0088


def haversine(lat1, lon1, lat2, lon2):
    """Distância em km, em linha reta, entre dois pontos (graus decimais)."""
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * RAIO_TERRA_KM * asin(sqrt(a))
