# Prototipo Smart Parking Albacete

Prototipo funcional minimo del proyecto. Demuestra el flujo extremo a extremo:

```
Simulador (paho-mqtt, mTLS) -> AWS IoT Core -> IoT Rule -> Lambda ingesta
       -> DynamoDB (estado)
       -> Lambda agregador -> DynamoDB (KPIs)
       -> API Gateway REST -> Streamlit dashboard / terceros
```

## Requisitos

- Python 3.11 o superior (probado en 3.13).
- AWS Academy Learner Lab activo con credenciales en `~/.aws/credentials`.
- Region `us-east-1` (modificable via variable `AWS_REGION`).

## Instalacion

```powershell
python -m pip install -r requirements.txt
copy .env.example .env
```

## Despliegue (en orden)

```powershell
python infra/01_setup_iot_core.py
python infra/02_setup_dynamodb.py
python infra/03_setup_lambda.py
python infra/04_setup_api_gateway.py
```

Tras `01_*` se generan los certificados X.509 dentro de `simulator/certs/`.
Tras `04_*` la URL base de la API queda persistida en `infra/infra_state.json`.

## Simulador

```powershell
python simulator/fleet_runner.py --num-spots 40 --duration 300 --heartbeat 30 --tick 2
```

Cada sensor publica un evento por cambio de estado y un heartbeat cada 30 s.
El ultimo sensor de la flota se simula como caido para ilustrar deteccion de
averias en la memoria.

## Dashboard

```powershell
streamlit run dashboard/streamlit_app.py
```

Se abre en `http://localhost:8501`. Toma la URL de la API de
`infra/infra_state.json` automaticamente.

## Teardown

```powershell
python infra/99_teardown.py
```

Borra IoT Things, certificado, policy, Topic Rule, Lambdas, tablas DynamoDB y
API Gateway. Hay que ejecutarlo antes de que caduquen las credenciales del lab.
