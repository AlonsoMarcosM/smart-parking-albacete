# 00. Resumen ejecutivo

## 0.1 Identificación del proyecto

| Campo | Valor |
|-------|-------|
| Titulación | Máster Universitario en Big Data y Computación en la Nube (UCLM) |
| Asignatura | Internet de las Cosas y sus Aplicaciones (cód. 311482, 6 ECTS) |
| Entregable | Proyecto final TR1 + prototipo |
| Curso | 2025-2026 |
| Autor | alonso.marcos@alu.uclm.es |
| Cliente ficticio | TECO S.L. |
| Cliente real (licitador) | Ayuntamiento de Albacete |
| Zona piloto | Entorno universitario de Albacete (BBOX `38.976059, -1.858728 → 38.983215, -1.846111`) |

## 0.2 Visión del proyecto

El Ayuntamiento de Albacete saca a licitación una solución de **smart parking** que permita monitorizar en tiempo real las plazas de aparcamiento del entorno universitario, exponer su disponibilidad a sistemas externos (aplicaciones de movilidad, vehículos autónomos vía C-V2X, paneles informativos) y servir como base para un escalado posterior a toda la ciudad.

TECO S.L. responde con una solución end-to-end basada en cuatro capas:

1. **Telemetría**: sensores magnéticos AMR en cada plaza (independencia visual, bajo consumo) y cámaras ANPR puntuales en los accesos.
2. **Conectividad**: NB-IoT como red principal por su cobertura municipal y autonomía multianual; LoRaWAN como alternativa donde haya infraestructura privada disponible; fibra/5G para el backhaul de los gateways y cámaras.
3. **Plataforma cloud**: AWS IoT Core como puerta de entrada MQTT/TLS, IoT Rules + Lambda como capa de procesamiento, DynamoDB como almacén operacional, API Gateway como fachada pública.
4. **Aplicaciones**: API REST documentada con OpenAPI 3.0 (incluido formato GeoJSON para clientes cartográficos) y dashboard Streamlit para el operador, junto con la integración futura con FIWARE Orion (NGSI-v2) para interoperabilidad con otras smart cities.

## 0.3 Alcance del prototipo entregado

El prototipo cubre el **flujo extremo a extremo** desde sensor hasta dashboard:

- 40 plazas simuladas, distribuidas en 4 sub-zonas operativas reales sobre coordenadas exactas dentro de la BBOX (Campus UCLM, Estadio Carlos Belmonte, Hospital Universitario y entorno residencial sur).
- Despliegue real en **AWS Academy Learner Lab** con scripts boto3 idempotentes.
- Verificación funcional: `GET /spots`, `GET /spots/{id}`, `GET /zones`, `GET /zones/{id}/kpis`, formato GeoJSON, dashboard con mapa, KPIs por sub-zona y serie temporal de ocupación.

## 0.4 Decisiones técnicas más relevantes

| Decisión | Justificación |
|----------|---------------|
| Sensor magnético AMR (no cámara por plaza) | Mejor balance precisión/consumo/coste/privacidad; >5 años de autonomía. |
| NB-IoT como red principal | Cobertura LTE municipal existente, sin desplegar infraestructura propia, coste OPEX bajo (<1 €/SIM/mes). |
| AWS IoT Core + IoT Rule + Lambda | Modelo serverless; coste por evento; sin servidores que mantener. |
| DynamoDB on-demand | Sin capacidad provisionada; absorbe picos de eventos sin throttling. |
| Lambda agregador (no Flink en piloto) | Volumen del piloto manejable en una función simple; Flink se reserva para escenario ciudad. |
| Streamlit como dashboard | Velocidad de desarrollo y suficiente para una demo de defensa. |
| FIWARE solo a nivel de diseño | El enunciado exige AWS; FIWARE se documenta como capa de interoperabilidad NGSI-v2. |

## 0.5 Resultados clave

- Latencia medida end-to-end (sensor → DynamoDB → API): **< 2 segundos** en condiciones del piloto.
- Throughput verificado: 40 sensores publicando ~4 eventos/min sostenidos sin throttling.
- KPIs por sub-zona generados cada vez que cambia el estado de una plaza, con persistencia como serie temporal.
- Coste estimado del piloto en AWS: **< 5 USD/mes** para el volumen actual; escalable linealmente.
- Coste estimado escenario ciudad (10 000 plazas): aproximadamente 600-900 USD/mes en AWS más el CAPEX de sensores (~75 €/plaza).

## 0.6 Mapeo a los resultados de aprendizaje

| Resultado | Cobertura en este proyecto |
|-----------|----------------------------|
| **CN02** (arquitecturas de tratamiento masivo) | Capítulos 5, 7, 9 (cloud, modelo de datos, escalabilidad). |
| **HA03** (orquestación ETL, data lakes) | Capítulo 7 (S3 raw como data lake bronze; DynamoDB como zona silver; pipeline en Lambda). |
| **CP02** (IoT, edge, streams) | Capítulos 3, 4, 5 (telemetría, conectividad, edge) y 6 (Apache Flink en diseño). |

## 0.7 Estructura del documento

```
00 Resumen ejecutivo (este documento)
01 Descripción del problema
02 Requisitos funcionales y no funcionales
03 Capa de telemetría
04 Conectividad
05 Arquitectura cloud en AWS
06 Integración con FIWARE y Apache Flink (diseño)
07 Modelo maestro de datos y APIs
08 Seguridad
09 Escalabilidad (piloto y ciudad)
10 Análisis de costes
11 Prototipo: ejecución, verificación y capturas
12 Limitaciones y trabajo futuro
13 Preparación de la defensa
```
