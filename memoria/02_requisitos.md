# 02. Requisitos funcionales y no funcionales

La elicitación de requisitos parte del enunciado del campus virtual, se completa con la guía operativa interna del proyecto y con la guía docente de la asignatura, y se formaliza en este capítulo distinguiendo entre **requisitos funcionales** (RF), **no funcionales** (RNF) y **restricciones** (RST). Cada requisito incluye criterios de aceptación verificables.

## 2.1 Requisitos funcionales

| ID | Requisito | Criterio de aceptación |
|----|-----------|------------------------|
| RF-01 | El sistema debe detectar y reportar el estado (libre / ocupada) de cada plaza monitorizada. | Cada cambio de estado se refleja en el almacén operacional en ≤ 5 s. |
| RF-02 | Cada evento debe quedar asociado a la plaza concreta y a la sub-zona. | Cada evento incluye `spotId` y `zoneId`. |
| RF-03 | El sistema debe transmitir eventos desde los sensores o desde un simulador. | Prototipo: el simulador publica MQTT/TLS contra AWS IoT Core. |
| RF-04 | El sistema debe mantener el estado actual de ocupación de cada plaza. | Tabla DynamoDB `parking-state` con PK `spotId`. |
| RF-05 | El sistema debe ofrecer un dashboard con la disponibilidad en tiempo real. | Streamlit con KPIs, mapa y serie temporal; refresco ≤ 10 s. |
| RF-06 | El sistema debe exponer una API REST a sistemas externos. | API Gateway + OpenAPI 3.0; endpoints `/spots`, `/zones`, `/zones/{id}/kpis`. |
| RF-07 | La API debe permitir análisis por sub-zona y por plaza. | Parámetro `?zone=` y endpoint `/zones`. |
| RF-08 | La salida debe poder consumirse por mapas de terceros sin transformación. | `?format=geojson` devuelve FeatureCollection RFC 7946. |
| RF-09 | El sistema debe calcular agregados por sub-zona (libres, ocupadas, % ocupación). | Lambda agregador actualiza `zone-kpis` por cambio de estado. |
| RF-10 | El sistema debe registrar histórico operacional. | Serie temporal en `zone-kpis` indexada por `(zoneId, windowEnd)`. |
| RF-11 | El sistema debe ser capaz de detectar sensores caídos. | Heartbeat configurable + auditoría de `lastUpdated` (trabajo futuro: alerta automática). |

## 2.2 Requisitos no funcionales

### Rendimiento y latencia

| ID | Requisito | Criterio de aceptación |
|----|-----------|------------------------|
| RNF-01 | Latencia E2E (sensor → consulta en API) ≤ 5 s en condiciones normales. | Medición real en el prototipo: ≤ 2 s. |
| RNF-02 | La API debe responder en p95 ≤ 1 s. | Verificado con curl/Streamlit. |
| RNF-03 | El sistema debe soportar 10 eventos/s sin throttling en el piloto. | DynamoDB on-demand absorbe el pico. |

### Escalabilidad

| ID | Requisito | Criterio de aceptación |
|----|-----------|------------------------|
| RNF-04 | La arquitectura debe escalar de 500 plazas a ≥ 10 000 sin rediseño. | Plan documentado en el capítulo 9 (sharding por zona, GSI por estado, Timestream/Kinesis). |
| RNF-05 | Los servicios cloud usados deben ser serverless o gestionados. | IoT Core, Lambda, DynamoDB, API Gateway son todos gestionados. |

### Fiabilidad y disponibilidad

| ID | Requisito | Criterio de aceptación |
|----|-----------|------------------------|
| RNF-06 | Disponibilidad ≥ 99,5 % en piloto. | SLA AWS IoT Core 99,9 %; SLA Lambda 99,95 %. |
| RNF-07 | El sistema debe tolerar pérdida temporal de conectividad del sensor. | Reintento con backoff en el cliente MQTT; buffer local. |
| RNF-08 | Cualquier componente debe poder reiniciarse sin perder estado. | Estado en DynamoDB; Lambdas sin estado en memoria. |

### Seguridad

| ID | Requisito | Criterio de aceptación |
|----|-----------|------------------------|
| RNF-09 | Toda comunicación dispositivo-cloud debe ir cifrada. | MQTT sobre TLS 1.2 con mTLS (cert X.509). |
| RNF-10 | Cada dispositivo debe tener identidad propia. | Cada Thing en IoT Core con su certificado y policy. |
| RNF-11 | La API pública debe poder limitar el consumo de terceros. | API Gateway permite throttling y API keys. |
| RNF-12 | No deben almacenarse datos personales identificables. | El modelo no contiene matrículas ni identificadores del conductor. |
| RNF-13 | Auditoría y trazabilidad de eventos. | S3 raw + CloudTrail + CloudWatch Logs. |

### Mantenibilidad y observabilidad

| ID | Requisito | Criterio de aceptación |
|----|-----------|------------------------|
| RNF-14 | El despliegue debe ser reproducible desde código. | Scripts boto3 idempotentes; ningún paso manual en consola. |
| RNF-15 | Debe existir un procedimiento limpio de borrado. | `99_teardown.py`. |
| RNF-16 | Métricas y logs deben centralizarse. | CloudWatch para Lambda e IoT; logs de regla MQTT. |

### Coste

| ID | Requisito | Criterio de aceptación |
|----|-----------|------------------------|
| RNF-17 | El coste cloud del piloto debe ser < 10 USD/mes. | Estimación detallada en el capítulo 10. |

### Interoperabilidad y privacidad

| ID | Requisito | Criterio de aceptación |
|----|-----------|------------------------|
| RNF-18 | La API debe ser autodescriptiva y estándar. | OpenAPI 3.0.1, GeoJSON RFC 7946. |
| RNF-19 | Diseño compatible con NGSI-v2 (FIWARE). | Modelo de entidades documentado; mapping en el capítulo 6. |
| RNF-20 | Cumplimiento RGPD. | Sin datos personales; documentado en el capítulo 8. |

## 2.3 Restricciones

| ID | Restricción | Origen |
|----|-------------|--------|
| RST-01 | La plataforma cloud debe ser Amazon AWS. | Enunciado. |
| RST-02 | Las credenciales del lab caducan a las 3 horas. | AWS Academy Learner Lab. |
| RST-03 | Solo se dispone del `LabRole` predefinido; no se pueden crear roles IAM nuevos. | AWS Academy. |
| RST-04 | El prototipo debe demostrarse en defensa oral. | Guía docente. |
| RST-05 | La documentación se entrega en castellano. | Guía docente. |
| RST-06 | El prototipo debe ejecutarse desde un equipo Windows estándar. | Entorno del autor. |

## 2.4 Matriz de trazabilidad

| Requisito | Capítulo donde se aborda | Componente del prototipo |
|-----------|--------------------------|--------------------------|
| RF-01..04 | 03, 05 | Simulador + IoT Core + Lambda ingest + DynamoDB state |
| RF-05 | 11 | `dashboard/streamlit_app.py` |
| RF-06..08 | 07 | Lambda API + API Gateway + OpenAPI |
| RF-09..10 | 05, 07 | Lambda aggregator + DynamoDB kpis |
| RF-11 | 03, 12 | Heartbeat en simulador; alerta como trabajo futuro |
| RNF-01..03 | 05, 11 | Mediciones reales del prototipo |
| RNF-04..05 | 09 | Plan de escalabilidad |
| RNF-06..08 | 08, 09 | Reintentos + AZ + estado externalizado |
| RNF-09..13 | 08 | mTLS + LabRole + S3 + CloudWatch |
| RNF-14..16 | 11 | Scripts `infra/*.py` + CloudWatch |
| RNF-17 | 10 | Estimación pricing |
| RNF-18..20 | 06, 07, 08 | OpenAPI + FIWARE NGSI-v2 + ausencia de PII |
