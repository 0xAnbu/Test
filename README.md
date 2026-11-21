# Ajedrez

Juego de ajedrez para dos personas o contra la máquina. Requiere Python 3.10 o posterior.

## Abrir el tablero gráfico

Desde la carpeta del juego, ejecuta:

```sh
python3 gui.py
```

Si Python indica que falta Tkinter, instala el paquete de tu sistema
(por ejemplo, `python3-tk` en Debian).

Elige el modo de juego y pulsa **Nueva partida**. Haz clic en una pieza y luego
en una de las casillas resaltadas. **Pista** marca una jugada posible y
**Deshacer** recupera el último turno. Usa **Coronar como** para escoger la pieza
antes de llevar un peón a la última fila.

## Jugar en la terminal

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
Sin sufijo se corona a dama. Escribe `pista` para que la máquina te sugiera una jugada,
`deshacer` para volver atrás (contra la máquina deshace también su respuesta) o `salir` para terminar.

El juego detecta el jaque mate y el ahogado. Las demás reglas de tablas
quedan a cargo de los jugadores.

Pruebas:

```sh
python3 -m unittest
```
