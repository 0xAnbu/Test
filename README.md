# Ajedrez

Juego de terminal para dos personas en el mismo equipo. Requiere Python 3.10 o posterior.

```sh
python3 ajedrez.py
```

Introduce el origen y destino, por ejemplo `e2e4`. Para enrocar, mueve el rey dos casillas.
Para coronar, añade `q`, `r`, `b` o `n` (dama, torre, alfil o caballo).
Sin sufijo se corona a dama. Escribe `salir` para terminar.

El juego detecta el jaque mate y el ahogado. Las demás reglas de tablas
quedan a cargo de los jugadores.
