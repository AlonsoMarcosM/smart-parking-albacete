# AGENTS.md

## Objetivo

Mantener el caso Smart Parking reproducible en dos modos: infraestructura AWS real y publicación gratuita simulada.

## Reglas

- No introducir credenciales, certificados ni `infra_state.json` en Git.
- `SMART_PARKING_MODE=auto` es el valor por defecto: usa la API si existe y, en caso contrario, la simulación local.
- La simulación debe identificarse como tal y conservar las 40 ubicaciones de `parking_zone_seed.json`.
- No desplegar recursos AWS permanentes para el portfolio.
- Actualizar `docs/portfolio_deployment.md` y `portfolio.json` cuando cambie el despliegue público.

## Verificación mínima

```powershell
python -m unittest discover -s .\prototipo\tests
$env:SMART_PARKING_MODE = "demo"
python -m streamlit run .\prototipo\dashboard\streamlit_app.py --server.headless true
```
