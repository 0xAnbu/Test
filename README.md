# Ajedrez

Juego de ajedrez de terminal. Requiere Python 3.10 o posterior.

Para jugar dos personas en el mismo equipo:

```sh
python3 ajedrez.py
```

Para jugar contra la máquina, elige el color de la máquina. Si solo escribes
`--cpu`, la máquina juega con negras.

```sh
python3 ajedrez.py --cpu
python3 ajedrez.py --cpu blancas
```

Introduce el origen y destino, por ejemplo `e2e4`. Para enrocar, mueve el rey dos casillas.
Para coronar, añade `q`, `r`, `b` o `n` (dama, torre, alfil o caballo).
Sin sufijo se corona a dama. Escribe `salir` para terminar.

El juego detecta el jaque mate y el ahogado. Las demás reglas de tablas
quedan a cargo de los jugadores.

Pruebas:

```sh
python3 -m unittest
```
