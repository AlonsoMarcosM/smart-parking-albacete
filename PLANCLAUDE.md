# Plan: Proyecto Final IoT - Smart Parking Albacete (TECO S.L.)

## Contexto

Se trata del proyecto final de la asignatura **Internet de las Cosas y sus Aplicaciones** (cod. 311482, 6 ECTS) del Máster en Big Data y Computación en la Nube de la UCLM. El enunciado pide diseñar e implementar parcialmente una arquitectura IoT completa para monitorizar plazas de aparcamiento en la zona universitaria de Albacete, con escenarios de piloto (centenares de plazas) y ciudad (miles), cubriendo desde la sensorización hasta la exposición de APIs a vehículos autónomos.

Ya existen en la carpeta del proyecto:
- `Guia_Docente_INTERNET_DE_LAS_COSAS_Y_SUS_APLICACIONES.md` — restricciones académicas, pesos de evaluación (TR1 25%, TR2 20%, PR1 20%) y mínimos.
- `guia_proyecto.md` — guía operativa del enunciado con checklist obligatorio.
- `temario/` con material de FIWARE (tema4.md), Apache Flink (tema5.md), AWS IoT Core (Tema 6.1/6.2 + LAB 6.1), matrices de selección, Lean Startup y simulación IoT-REST.

**Decisiones cerradas con el usuario:**
1. Despliegue REAL en AWS Academy Learner Lab (credenciales 3 h en `C:\Users\Alonso\.aws\credentials`).
2. FIWARE Orion y Apache Flink se documentan en el diseño pero NO se implementan (las agregaciones por zona se hacen en Lambda).
3. Dashboard en **Streamlit** minimalista (rápido y suficiente para la defensa).
4. Estructura `memoria/` + `prototipo/` + `README_GUIA.md` en raíz.
5. **Zona piloto definida por el usuario con mapa real**:
   - Bounding box: `SW (38.976059, -1.858728)` → `NE (38.983215, -1.846111)` (≈ 0,8 km × 0,8 km, ~0,55 km²).
   - Límites aproximados: al norte la N-430 (Avenida de España), al sur la AB-20 / Av. de la Mancha, al oeste el Campus UCLM (C. Imperial / C. de la Navaja), al este la C. San Juan / Av. de la Mancha.
   - Puntos de interés y polos de demanda dentro de la BBOX: Campus Universitario UCLM Albacete (Facultad de Informática, Pabellón Universitario), Estadio Municipal Carlos Belmonte, Campos de Fútbol Alba Redondo y "José Copete", Facultad de Farmacia / Facultad de Medicina, Hospital Universitario de Albacete (esquina NE), restaurante Le Première, Parque Infantil y Parque de calistenia "Vía verde de la Pulgosa".
   - Ejes viarios con plazas en línea para sensorizar: C. San Juan, Av. del Arte, Av. de la Mancha, C. Duque de Rivas, C. la Historia, C. la Química, Calle Imperial.
   - Estas coordenadas reales se usarán para sembrar las plazas del simulador y para los mapas de la memoria (el dashboard Streamlit las usa al pintar los KPIs).

**Objetivo del agente:** realizar el proyecto completo "one shot" y redactar `README_GUIA.md` explicando cada decisión y comando ejecutado, en español de España con UTF-8 y cuidado con tildes y "ñ", redactando como alumno de máster.

---

## Arquitectura propuesta

### Capas (lo que se documenta + lo que se implementa)

| Capa | Diseño documentado | Implementado en prototipo |
|------|--------------------|---------------------------|
| Telemetría | Sensores magnéticos AMR por plaza + cámaras ANPR en accesos + sensores ambientales auxiliares | Simulador Python multi-sensor que publica MQTT/TLS |
| Conectividad | NB-IoT/LoRaWAN para sensores, fibra/5G para backhaul de gateways, C-V2X para diálogo con vehículo | Simulador habla MQTT directo a AWS IoT Core (representa flujo tras gateway) |
| Edge | Gateway con AWS IoT Greengrass por zona: filtrado, debounce, caché offline | Lógica de debounce dentro del propio simulador (sustituye al gateway) |
| Cloud | AWS IoT Core + Rules + Lambda + DynamoDB + API Gateway + S3 + CloudWatch | **TODO real en AWS Academy** |
| Contexto / Analítica | FIWARE Orion (NGSI-v2) + Apache Flink para agregaciones por zona y detección de sensores caídos | Lambda hace agregaciones simples por zona y persiste en DynamoDB |
| Exposición | API REST pública (terceros) + API interna (operador) + dashboard | API Gateway REST + Streamlit consumiendo la API |

### Diagrama de flujo (a incluir como Mermaid en la memoria)

```
Sensor plaza -> Gateway edge -> AWS IoT Core (MQTT/TLS)
  -> IoT Rule -> Lambda ingesta -> DynamoDB (estado)
  -> IoT Rule -> S3 (raw, historico)
  -> Lambda agregador -> DynamoDB (KPIs por zona)
  -> API Gateway -> Streamlit dashboard / clientes terceros
```

---

## Estructura final del proyecto

```
proyectofinal/
├── README_GUIA.md                  # Diario explicativo (decisiones + comandos)
├── guia_proyecto.md                # Existente, no se toca
├── Guia_Docente_*.md               # Existente, no se toca
├── temario/                        # Existente, no se toca
├── memoria/
│   ├── 00_resumen_ejecutivo.md
│   ├── 01_descripcion_problema.md
│   ├── 02_requisitos.md
│   ├── 03_capa_telemetria.md
│   ├── 04_conectividad.md
│   ├── 05_arquitectura_cloud_aws.md
│   ├── 06_integracion_fiware_flink.md
│   ├── 07_modelo_datos_apis.md
│   ├── 08_seguridad.md
│   ├── 09_escalabilidad_piloto_ciudad.md
│   ├── 10_analisis_costes.md
│   ├── 11_prototipo.md
│   ├── 12_limitaciones_trabajo_futuro.md
│   ├── 13_defensa.md
│   └── diagramas/                  # Mermaid + descripciones
└── prototipo/
    ├── README.md                   # Cómo arrancar el prototipo
    ├── requirements.txt
    ├── .env.example
    ├── infra/
    │   ├── 01_setup_iot_core.py    # Crea Thing, certificados, política, Rule
    │   ├── 02_setup_dynamodb.py    # Crea tablas parking_state y zone_kpis
    │   ├── 03_setup_lambda.py      # Empaqueta y despliega lambdas + role del lab
    │   ├── 04_setup_api_gateway.py # API REST con endpoints publicos
    │   ├── 99_teardown.py          # Limpia todo al cerrar el lab
    │   └── parking_zone_seed.json  # 30-40 plazas piloto con coords reales dentro de la BBOX UCLM-Belmonte-Hospital (4 sub-zonas Z1..Z4)
    ├── simulator/
    │   ├── parking_sensor.py       # Cliente MQTT/TLS por plaza
    │   ├── fleet_runner.py         # Orquesta N sensores con patrones realistas
    │   └── certs/                  # Certificados descargados de AWS IoT
    ├── lambdas/
    │   ├── ingest/handler.py       # Normaliza evento, escribe estado
    │   └── aggregator/handler.py   # Recalcula KPIs por zona
    ├── api/
    │   └── openapi.yaml            # Spec de la API REST
    └── dashboard/
        ├── streamlit_app.py        # KPIs, tabla de plazas, gráfica temporal
        └── assets/
```

---

## Componentes a implementar

### 1. Memoria técnica (`memoria/*.md`)

Documento exhaustivo en castellano dividido en 13 secciones cortas. Cada decisión queda justificada con criterios (latencia, coste, consumo, cobertura, privacidad) y comparada frente a alternativas. Diagramas Mermaid embebidos.

Puntos críticos:
- **Supuestos del piloto** (sección 1-2): zona piloto delimitada por la BBOX `38.976059, -1.858728 → 38.983215, -1.846111` (≈ 0,55 km² en torno al Campus UCLM Albacete). Se divide en 4 sub-zonas operativas: `Z1-CAMPUS` (Universidad e Investigación), `Z2-DEPORTIVO` (Estadio Belmonte + Alba Redondo + José Copete), `Z3-SANITARIO` (Facultades Medicina/Farmacia + Hospital Universitario), `Z4-RESIDENCIAL` (zona sur, Av. de la Mancha). Volumen estimado: ~500 plazas piloto (≈125 por zona), latencia objetivo < 5 s end-to-end, disponibilidad 99,5 %. Patrones de demanda diferenciados (Z1 pico mañana, Z2 pico fin de semana, Z3 24/7).
- **Justificación de sensores** (sección 3): tabla comparativa magnético vs ultrasónico vs cámara ANPR vs radar, recomendación de magnético AMR (Bosch/Nedap clase) por consumo y precisión.
- **Conectividad** (sección 4): NB-IoT como red principal por cobertura municipal y consumo (>5 años con pilas D), LoRaWAN como alternativa privada, 5G/fibra para backhaul de cámaras y gateways.
- **Costes** (sección 10): tabla con CAPEX (sensor 60-120 €, gateway 400-800 €, cámara 500-1200 €) y OPEX (NB-IoT ~0,30-1 €/SIM/mes, AWS estimado por evento), proyección piloto y ciudad.
- **Escalabilidad** (sección 9): sharding por zona en DynamoDB con partition key compuesta, número de IoT Things, throughput de Rules, plan de migración a Timestream para histórico en ciudad.

### 2. Infraestructura AWS (`prototipo/infra/*.py`)

Scripts boto3 idempotentes que crean y limpian todo desde código (NO se usa la consola web salvo para validar). Usan el perfil `default` del Learner Lab, region `us-east-1` (la del lab), y `LabRole` que ya existe en el lab para Lambda.

- **01_setup_iot_core.py**: crea 1 Thing por sensor (limitado a 5 para prototipo + 30 simulados via mismo Thing), genera certificado X.509, descarga clave/cert/root-CA a `simulator/certs/`, crea política `parking-sensor-policy`, crea Topic Rule `ParkingSpotIngestRule` con SQL `SELECT * FROM 'parking/+/spot/+/status'` y dos acciones: Lambda ingest + S3 (raw).
- **02_setup_dynamodb.py**: tabla `parking_state` (PK `spotId`), tabla `zone_kpis` (PK `zoneId`, SK `windowEnd`).
- **03_setup_lambda.py**: empaqueta `lambdas/ingest` y `lambdas/aggregator` en zip, los publica, asocia rol `LabRole`, conecta el ingest como action de la IoT Rule.
- **04_setup_api_gateway.py**: REST API con recursos `/spots`, `/spots/{id}`, `/zones`, `/zones/{id}/kpis`. Integraciones AWS_PROXY con una Lambda lectora `lambdas/api`.
- **99_teardown.py**: borra todo (DynamoDB, Lambdas, API, IoT Things/Rules/Cert/Policy) para no dejar residuos en el lab.

### 3. Simulador de telemetría (`prototipo/simulator/`)

- `parking_sensor.py`: cliente MQTT5/TLS con `awscrt`/`awsiotsdk` que publica eventos JSON `{spotId, zoneId, status, batteryLevel, timestamp, confidence}` al topic `parking/{zone}/spot/{id}/status` cuando hay cambio de estado, y heartbeat cada 5 min.
- `fleet_runner.py`: ejecuta concurrentemente N sensores (asyncio) con patrones realistas por sub-zona: Z1-CAMPUS pico mañana (8-10 h) y tarde (16-18 h), Z2-DEPORTIVO picos de evento (sábado/tarde-noche), Z3-SANITARIO rotación continua, Z4-RESIDENCIAL ocupación alta y estable de noche. Inyecta también sensores con batería < 20 % y un sensor "caído" (sin heartbeat) para demostrar detección de fallos.
- Lee la configuración de plazas desde `infra/parking_zone_seed.json`. Las coordenadas (lat, lon) se generan distribuyendo las 30-40 plazas a lo largo de los ejes viarios reales identificados (C. San Juan, Av. del Arte, Av. de la Mancha, C. Duque de Rivas, C. Imperial) dentro de la BBOX `38.976059, -1.858728 → 38.983215, -1.846111`, agrupadas por sub-zona.

### 4. Lambdas (`prototipo/lambdas/`)

- `ingest/handler.py`: recibe evento desde IoT Rule, valida esquema, normaliza, hace UPSERT en `parking_state`, dispara invocación asíncrona del agregador si cambia el estado.
- `aggregator/handler.py`: lee plazas de una zona desde `parking_state`, calcula `freeSpots`, `occupiedSpots`, `occupancyRate`, escribe en `zone_kpis` con `windowEnd = now`.
- `api/handler.py`: enruta peticiones del API Gateway según `httpMethod` + `path`, consulta DynamoDB y devuelve JSON. Acepta parámetros `zone` y `format=geojson` para que terceros (mapas) consuman directo.

### 5. Dashboard Streamlit (`prototipo/dashboard/streamlit_app.py`)

- KPIs cabecera: total plazas, libres, ocupadas, % ocupación global.
- Selector de sub-zona (Z1-CAMPUS, Z2-DEPORTIVO, Z3-SANITARIO, Z4-RESIDENCIAL) y mini-tabla de plazas con código de color.
- Mapa interactivo (`st.map` o `pydeck`) centrado en `(38.9796, -1.8524)` con las plazas pintadas según estado (verde=libre, rojo=ocupada, gris=sin datos). Las coordenadas vienen del seed y caen dentro de la BBOX real del proyecto.
- Gráfica de evolución temporal (Plotly line) leyendo `zone_kpis`.
- Botón "Refrescar" + auto-refresh cada 5 s.
- Pinta los datos consumiendo la API REST desplegada (no DynamoDB directo).

### 6. README_GUIA.md (la "guía descriptiva" que pide el usuario)

Documento en raíz, dirigido al usuario como autor del proyecto. Contiene:
1. Resumen de lo que hace el agente y por qué.
2. Stack tecnológico elegido y alternativas descartadas (con justificación que el usuario pueda repetir en defensa).
3. Pasos cronológicos ejecutados, con cada comando y su explicación.
4. Cómo arrancar el prototipo desde cero (instalación, despliegue, simulador, dashboard).
5. Cómo destruir la infra al cerrar el lab.
6. Mapeo de cada entregable exigido por la guía docente y por el enunciado del campus virtual.
7. Glosario IoT/AWS para repaso rápido antes de la defensa.

---

## Stack tecnológico final

- **Lenguaje**: Python 3.13.
- **Librerías**: `boto3`, `awsiotsdk`, `paho-mqtt` (alternativa), `streamlit`, `plotly`, `requests`, `python-dotenv`.
- **AWS**: IoT Core, Lambda, DynamoDB, API Gateway, S3, CloudWatch Logs, IAM `LabRole`. Region `us-east-1`.
- **Local**: scripts `infra/*.py` con boto3, simulador asyncio, dashboard Streamlit.
- **NO se usa**: Greengrass (se simula), Timestream (no suele estar habilitado en Academy), Cognito (se documenta), Kinesis/MSK (no necesario en piloto), FIWARE/Flink (solo documentación).

---

## Flujo de ejecución (one shot)

1. Crear estructura de carpetas y archivos vacíos.
2. Instalar dependencias (`pip install boto3 awsiotsdk streamlit plotly python-dotenv requests`) + AWS CLI v2 (opcional para validación con `aws sts get-caller-identity`).
3. Validar credenciales del lab con boto3 (account ID, region).
4. Redactar memoria técnica (13 secciones) en `memoria/`.
5. Implementar código del prototipo (infra, simulador, lambdas, api, dashboard).
6. Ejecutar `infra/01..04_setup_*.py` para crear todo en AWS.
7. Lanzar el simulador unos minutos y comprobar mensajes en MQTT test client (vía boto3 IoT data plane) y en DynamoDB.
8. Lanzar el dashboard Streamlit y capturar pantallazos para la memoria.
9. Redactar `README_GUIA.md` con la cronología real de comandos.
10. Recordatorio explícito al usuario para ejecutar `infra/99_teardown.py` antes de que caduquen las credenciales.

---

## Archivos críticos a crear/modificar

- `proyectofinal/README_GUIA.md` (nuevo, raíz)
- `proyectofinal/memoria/*.md` (13 archivos nuevos + carpeta diagramas)
- `proyectofinal/prototipo/requirements.txt`, `.env.example`, `README.md`
- `proyectofinal/prototipo/infra/{01..04,99}_*.py` + `parking_zone_seed.json`
- `proyectofinal/prototipo/simulator/{parking_sensor.py, fleet_runner.py}`
- `proyectofinal/prototipo/lambdas/{ingest,aggregator,api}/handler.py`
- `proyectofinal/prototipo/api/openapi.yaml`
- `proyectofinal/prototipo/dashboard/streamlit_app.py`

No se modifica nada de lo existente (`guia_proyecto.md`, `Guia_Docente_*.md`, `temario/`).

---

## Verificación end-to-end

1. `python -c "import boto3; print(boto3.client('sts').get_caller_identity())"` devuelve account + role del lab.
2. Tras `01_setup_iot_core.py`: en AWS console aparece el Thing y los certificados quedan en `simulator/certs/`.
3. Tras `02..04`: la tabla `parking_state` está vacía, la API Gateway responde `[]` en `GET /spots`.
4. Lanzar `python simulator/fleet_runner.py --num-spots 30 --duration 120`. Comprobar en CloudWatch Logs que la Lambda ingest se invoca, y en DynamoDB que aparecen items.
5. `curl https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/spots` devuelve JSON con plazas y estados.
6. `streamlit run dashboard/streamlit_app.py` muestra mapa/tabla con datos en vivo del paso 5.
7. Capturar pantallazos para `memoria/11_prototipo.md`.
8. `python infra/99_teardown.py` deja la cuenta limpia.

---

## Riesgos y mitigaciones

- **Credenciales caducan (3 h)**: scripts idempotentes y agrupados; teardown rápido al final; mensaje en README sobre cómo relanzar el lab y reejecutar.
- **Región del lab restringida**: usar `us-east-1` que es la habitual de Academy; documentar fallback a `us-west-2`.
- **Permisos del `LabRole`**: limitarse a IoT, Lambda, DynamoDB, API Gateway, S3, IAM passrole, CloudWatch. NO se intenta crear roles nuevos.
- **Sensor SDK puede no compilar**: como fallback, `paho-mqtt` con TLS también funciona contra AWS IoT Core.
- **Latencia visible**: Streamlit auto-refresh cada 5 s es suficiente para defender la "baja latencia" (eventos llegan a DynamoDB en < 1 s).
- **Tiempo del agente**: 13 secciones de memoria + ~10 archivos de código es ambicioso. Estrategia: primero código mínimo que funcione, después rellenar memoria con datos reales del despliegue.
