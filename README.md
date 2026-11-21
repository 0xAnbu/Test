# pingwatch

Monitor mínimo de URLs. Python ≥ 3.12, solo biblioteca estándar.

Hace `GET` a cada URL de `targets.txt` (timeout 5 s) y envía una alerta `POST` a `NOTIFY_URL` cuando el status es 0 (error de red) o ≥ 500.

## Configuración

```sh
cp .env.example .env               # y rellena NOTIFY_URL / NOTIFY_API_KEY
cp targets.example.txt targets.txt  # y pon tus URLs
```

Las variables de entorno del proceso tienen prioridad sobre `.env`:

| Variable | Obligatoria | Por defecto | Uso |
|---|---|---|---|
| `NOTIFY_URL` | sí | — | Endpoint de alertas |
| `NOTIFY_API_KEY` | sí | — | Se envía como `Authorization: Bearer …` |
| `TARGETS_FILE` | no | `targets.txt` | Una URL por línea; `#` comenta |
| `TIMEOUT` | no | `5` | Segundos por petición |

## Uso

```sh
python -m pingwatch --once          # una ronda; sale con 1 si alguna alerta no se entrega
python -m pingwatch --interval 60   # bucle cada 60 s (Ctrl+C para salir)
```

Las alertas se reintentan 3 veces con backoff (1, 2, 4 s). Cuerpo JSON, p. ej.: `{"url": "https://example.com", "status": 503, "latency_ms": 12.5}`.

## Tests

```sh
python -m unittest
```

`tests/test_integration_service.py` usa el servicio local `http://127.0.0.1:9099/v1/alerts`; el caso con clave válida solo corre si `NOTIFY_API_KEY` está en el entorno.
