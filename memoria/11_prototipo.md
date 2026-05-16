# 11. Prototipo funcional: ejecución, verificación y capturas

Este capítulo describe paso a paso cómo se ha construido, desplegado y verificado el prototipo entregable. Incluye la cronología de comandos efectivamente ejecutados, los resultados observados y la lista de capturas de pantalla que acompañan el documento.

## 11.1 Resumen del prototipo

El prototipo demuestra el flujo extremo a extremo:

```
Simulador Python (40 sensores MQTT/TLS)
  -> AWS IoT Core (Things, certificados, policy, Topic Rule)
    -> Lambda ingest -> DynamoDB parking-state
      -> Lambda aggregator -> DynamoDB zone-kpis
    -> API Gateway REST (+ formato GeoJSON)
      -> Streamlit dashboard (mapa, KPIs, serie temporal)
      -> Cualquier tercero por HTTPS
```

Todo está implementado y desplegado realmente en una cuenta AWS Academy Learner Lab (`Account 583916379944`, `us-east-1`).

## 11.2 Estructura del prototipo en disco

```
prototipo/
├── README.md
├── requirements.txt
├── .env.example
├── infra/
│   ├── common.py
│   ├── 01_setup_iot_core.py
│   ├── 02_setup_dynamodb.py
│   ├── 03_setup_lambda.py
│   ├── 04_setup_api_gateway.py
│   ├── 99_teardown.py
│   ├── parking_zone_seed.json
│   └── infra_state.json            (generado en runtime; no en git)
├── simulator/
│   ├── parking_sensor.py
│   ├── fleet_runner.py
│   └── certs/                      (generado al desplegar IoT Core)
├── lambdas/
│   ├── ingest/handler.py
│   ├── aggregator/handler.py
│   └── api/handler.py
├── api/openapi.yaml
└── dashboard/streamlit_app.py
```

## 11.3 Requisitos previos

- Python 3.11 o superior (probado en 3.13.9).
- AWS Academy Learner Lab activo con credenciales en `%USERPROFILE%\.aws\credentials`.
- Conexión a Internet.
- Sistema operativo Windows / Linux / macOS (probado en Windows 11).

## 11.4 Cómo lanzar el prototipo paso a paso

### 11.4.1 Instalación de dependencias

```powershell
cd "D:\DISCO DURO PORTABLE\...\proyectofinal\prototipo"
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### 11.4.2 Validación rápida de credenciales

```powershell
python -c "import boto3; print(boto3.client('sts', region_name='us-east-1').get_caller_identity())"
```

Debe devolver un objeto con `Account`, `Arn` (terminado en `:assumed-role/voclabs/...`).

### 11.4.3 Despliegue de la infraestructura AWS

Ejecutar en orden:

```powershell
python infra\01_setup_iot_core.py
python infra\02_setup_dynamodb.py
python infra\03_setup_lambda.py
python infra\04_setup_api_gateway.py
```

Tras `01_*` se generan los ficheros `simulator/certs/{device.cert.pem, device.private.key, AmazonRootCA1.pem}`.
Tras `04_*` el archivo `infra/infra_state.json` contiene la URL pública de la API (`apiBaseUrl`).

### 11.4.4 Lanzamiento del simulador de telemetría

```powershell
python simulator\fleet_runner.py --num-spots 40 --duration 180 --heartbeat 20 --tick 2
```

Parámetros:

- `--num-spots`: número de plazas a simular (máx. 40 según el seed).
- `--duration`: segundos a ejecutar (0 = indefinido).
- `--heartbeat`: segundos entre heartbeats sin cambio de estado.
- `--tick`: período del bucle interno del simulador.

### 11.4.5 Lanzamiento del dashboard

En otra consola:

```powershell
python -m streamlit run dashboard\streamlit_app.py
```

Se abre el navegador en `http://localhost:8501`. La aplicación toma la URL de la API de `infra/infra_state.json`. El refresco automático está configurable en la barra lateral.

### 11.4.6 Teardown obligatorio

Para no dejar recursos colgando (y proteger las horas de lab restantes):

```powershell
python infra\99_teardown.py
```

## 11.5 Cómo utilizar el sistema

### 11.5.1 Como operador municipal (dashboard)

1. Abrir `http://localhost:8501`.
2. La cabecera muestra los KPIs globales (total / libres / ocupadas / sin datos / % ocupación).
3. El mapa central muestra cada plaza con color (verde = libre, rojo = ocupada, gris = sin datos).
4. La sección "KPIs por sub-zona" muestra una tabla y un gráfico de barras por sub-zona.
5. En "Evolución temporal" se selecciona una sub-zona y se ve la serie temporal del % de ocupación.
6. La tabla "Detalle de plazas" permite filtrar e inspeccionar.

### 11.5.2 Como sistema externo (vehículo autónomo, app)

```bash
# Estado global
curl https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/spots

# Plazas libres en una sub-zona
curl 'https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/spots?zone=Z2-DEPORTIVO'

# GeoJSON para un mapa cliente
curl 'https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/spots?format=geojson'

# Detalle de una plaza
curl https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/spots/ALB-Z1-001

# Serie temporal KPIs
curl https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/zones/Z1-CAMPUS/kpis?limit=20
```

## 11.6 Cómo visualizar los resultados

| Vista | Dónde | Cómo |
|-------|-------|------|
| Estado por plaza | Dashboard Streamlit + `GET /spots` | Tabla y mapa |
| KPIs por zona en vivo | Dashboard + `GET /zones` | Tabla + gráfico de barras |
| Evolución temporal | Dashboard + `GET /zones/{id}/kpis` | Plotly line |
| Mensajes MQTT crudos | AWS Console > IoT > Test > MQTT test client, suscribiéndose a `parking/#` | Útil para defensa |
| Items en DynamoDB | AWS Console > DynamoDB > Tables > `smart-parking-albacete-state` > Explore | Ver datos como se persisten |
| Logs de Lambda | AWS Console > CloudWatch > Log groups > `/aws/lambda/smart-parking-albacete-ingest` | Diagnóstico |

## 11.7 Cómo explicar el prototipo en la defensa

Discurso recomendado (≈ 5 minutos):

1. **Contexto** (30 s): smart parking en zona universitaria de Albacete; cliente ficticio TECO S.L.; problema real de tráfico ineficiente buscando aparcamiento.
2. **Decisiones clave** (1 min): sensor magnético + NB-IoT + AWS serverless. Por qué cada elección (referencias al capítulo 3 y 4 de la memoria).
3. **Arquitectura** (1 min): diagrama mermaid del capítulo 5; remarcar que es serverless gestionada y multi-AZ.
4. **Demostración en vivo** (2 min):
   - Mostrar el dashboard ya cargado con el mapa.
   - Lanzar el simulador en una consola y mostrar cómo, al cabo de unos segundos, las plazas cambian de estado en el dashboard y la serie temporal sube.
   - Mostrar la API con un `curl` al GeoJSON (la respuesta puede pintarse en `geojson.io` si hay conexión).
   - Mostrar en la consola AWS > IoT > MQTT test client suscrito a `parking/#` que recibe los mensajes en tiempo real.
5. **Escalado y coste** (30 s): de 500 a 10 000 plazas con los cambios del capítulo 9; coste cloud despreciable (~6 céntimos/plaza/mes).
6. **Pregunta esperada — "¿Por qué no FIWARE?"** (15 s): se ha diseñado la integración híbrida; en piloto sobra; en ciudad se introduce sin tocar el resto.

## 11.8 Verificación end-to-end (resultado real obtenido)

| Paso | Comando | Resultado observado |
|------|---------|----------------------|
| Validar credenciales | `python -c "import boto3; ..."` | `Account=583916379944, Arn=...voclabs/...` |
| Crear IoT Core | `python infra/01_setup_iot_core.py` | 40 Things, certificado, policy, attach OK |
| Crear DynamoDB | `python infra/02_setup_dynamodb.py` | Dos tablas en estado ACTIVE |
| Crear Lambdas | `python infra/03_setup_lambda.py` | 3 Lambdas creadas, IoT Rule activa |
| Crear API Gateway | `python infra/04_setup_api_gateway.py` | URL: `https://85fbp0svzc.execute-api.us-east-1.amazonaws.com/prod` |
| Ejecutar simulador (60 s) | `python simulator/fleet_runner.py --duration 60 ...` | 40 sensores conectados, eventos publicados |
| `GET /spots` | `curl .../prod/spots` | 200 OK, 39 items (la 40ª es sensor en fallo intencional) |
| `GET /zones` | `curl .../prod/zones` | 4 sub-zonas con KPIs (Z1 40 %, Z2 60 %, Z3 40 %, Z4 22 %) |
| `GET /spots?format=geojson` | `curl ...&format=geojson` | FeatureCollection con 10 features para Z1 |
| `GET /zones/Z1-CAMPUS/kpis` | `curl .../zones/Z1-CAMPUS/kpis?limit=5` | 5 entradas con `windowEnd` y serie temporal |

## 11.9 Capturas de pantalla a incluir en la memoria (a generar por el autor)

> **Importante**: el agente no puede tomar capturas de pantalla del sistema operativo del autor. Los siguientes assets deben generarse manualmente antes de la entrega final y guardarse en `memoria/diagramas/`. Se sugiere nomenclatura para que el documento las localice automáticamente:

1. **`captura_aws_iot_things.png`** – Consola AWS > IoT Core > Manage > Things, mostrando los 40 Things `ALB-Z1-001` … `ALB-Z4-010` listados.
2. **`captura_aws_iot_mqtt_test.png`** – Consola AWS > IoT Core > Test > MQTT test client, suscrito a `parking/#`, mostrando mensajes recientes con el JSON publicado por el simulador.
3. **`captura_aws_iot_rule.png`** – Consola AWS > IoT Core > Message routing > Rules > `smart_parking_albacete_ingest_rule`, mostrando el SQL y la acción Lambda asociada.
4. **`captura_aws_dynamodb_state.png`** – Consola AWS > DynamoDB > Tables > `smart-parking-albacete-state` > Explore, mostrando una decena de items con sus `spotId`, `status`, `lat`, `lon`.
5. **`captura_aws_dynamodb_kpis.png`** – Ídem para `smart-parking-albacete-zone-kpis`, mostrando varias entradas con `windowEnd` distintos.
6. **`captura_aws_lambda_ingest.png`** – Consola AWS > Lambda > `smart-parking-albacete-ingest`, mostrando la configuración (runtime Python 3.12, rol LabRole) y un test de invocación.
7. **`captura_aws_cloudwatch_ingest.png`** – Consola AWS > CloudWatch > Log groups > `/aws/lambda/smart-parking-albacete-ingest`, mostrando un log stream con varias invocaciones.
8. **`captura_aws_apigateway.png`** – Consola AWS > API Gateway > APIs > `smart-parking-albacete-api`, mostrando los recursos y el stage `prod` desplegado.
9. **`captura_dashboard_principal.png`** – Streamlit con KPIs cabecera, mapa de plazas y leyenda.
10. **`captura_dashboard_kpis_zona.png`** – Sección "KPIs por sub-zona" con tabla y gráfico de barras.
11. **`captura_dashboard_serie_temporal.png`** – Sección de evolución temporal mostrando una serie con varios puntos.
12. **`captura_curl_geojson.png`** – Consola PowerShell con la respuesta GeoJSON formateada.
13. **`captura_curl_zones.png`** – Consola PowerShell con la respuesta de `GET /zones`.

Los diagramas Mermaid de los capítulos 5, 6 y 9 se renderizan automáticamente al exportar a PDF a través de pandoc (siempre que la cadena de plantillas tenga soporte). Si no, basta con renderizarlos en `mermaid.live` y guardar el PNG con el mismo nombre que el bloque.

## 11.10 Mapa "tal cual" del sistema en operación

Para que el lector se haga una idea inmediata del aspecto del prototipo:

- 40 puntos coloreados sobre el plano de la zona universitaria de Albacete.
- 4 grupos por sub-zona.
- Barra lateral con configuración y enlace a la API.
- Refresco visible cada 5-10 segundos.
- Latencia entre cambio de estado (en el simulador) y refresco en pantalla: **2-3 segundos** en operación normal.
