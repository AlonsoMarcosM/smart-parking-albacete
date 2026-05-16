# README - Guia del proyecto Smart Parking Albacete

> **Autor**: alonso.marcos@alu.uclm.es
> **Asignatura**: Internet de las Cosas y sus Aplicaciones (cod. 311482) - MUBDyCN UCLM
> **Curso**: 2025-2026

Este documento es la guia operativa del proyecto final. Esta escrito con dos objetivos:

1. Que el autor del proyecto (yo mismo) pueda **reproducir, defender y explicar** cada decision y cada comando ejecutado, incluso semanas despues de la entrega.
2. Que cualquier evaluador externo pueda **lanzar, usar, visualizar y entender** el sistema en menos de 15 minutos a partir de cero.

Esta organizado por bloques cronologicos en el mismo orden en que se realizaron las acciones. Cada bloque indica el **por que** (razon de la decision) ademas del **como** (comando).

---

## Tabla de contenidos

1. [Vision rapida en una pantalla](#1-vision-rapida-en-una-pantalla)
2. [Que entrega el proyecto](#2-que-entrega-el-proyecto)
3. [Como esta estructurada la carpeta](#3-como-esta-estructurada-la-carpeta)
4. [Stack tecnologico elegido y por que](#4-stack-tecnologico-elegido-y-por-que)
5. [Preparacion del entorno (una vez por equipo)](#5-preparacion-del-entorno-una-vez-por-equipo)
6. [Lanzamiento del prototipo de cero (cada sesion)](#6-lanzamiento-del-prototipo-de-cero-cada-sesion)
7. [Como usar el sistema desplegado](#7-como-usar-el-sistema-desplegado)
8. [Como visualizar los resultados](#8-como-visualizar-los-resultados)
9. [Como explicar el proyecto en defensa](#9-como-explicar-el-proyecto-en-defensa)
10. [Compilacion de la memoria a PDF](#10-compilacion-de-la-memoria-a-pdf)
11. [Capturas de pantalla que debe hacer el autor](#11-capturas-de-pantalla-que-debe-hacer-el-autor)
12. [Diario cronologico de lo que hizo el agente](#12-diario-cronologico-de-lo-que-hizo-el-agente)
13. [Mapeo entregables - guia docente y enunciado](#13-mapeo-entregables--guia-docente-y-enunciado)
14. [Glosario tecnico para repaso de defensa](#14-glosario-tecnico-para-repaso-de-defensa)
15. [Apagado y limpieza (obligatorio al cerrar el lab)](#15-apagado-y-limpieza-obligatorio-al-cerrar-el-lab)
16. [FAQ y resolucion de problemas](#16-faq-y-resolucion-de-problemas)

---

## 1. Vision rapida en una pantalla

```
                                  +---------------------+
   +--------------+    MQTT/TLS   |  AWS IoT Core       |   IoT Rule SQL
   | Simulador    | ============> |  - Things (40)      | ----------------+
   | Python paho  |               |  - Cert X.509       |                 |
   +--------------+               |  - Policy           |                 v
                                  +---------------------+        +-----------------+
                                                                  | Lambda ingest   |
                                                                  +-----------------+
                                                                  | UPSERT          |
                                                                  v                 |
                                                       +-----------------+          |
                                                       | DynamoDB        |          |
                                                       | parking-state   |          |
                                                       +-----------------+          |
                                                                ^                   |
                                                                | invoke async      |
                                                                |                   v
                                                       +-----------------+   +-----------------+
                                                       | Lambda          |<--| Lambda          |
                                                       | aggregator      |   | (event change)  |
                                                       +-----------------+   +-----------------+
                                                                |
                                                                v
                                                       +-----------------+
                                                       | DynamoDB        |
                                                       | zone-kpis       |
                                                       +-----------------+
                                                                ^
                                                                |
                                  +-----------------+ <---------+
                                  | API Gateway     |    +-----------------+
                                  | + Lambda api    |--->| Streamlit       |
                                  +-----------------+    | Dashboard       |
                                          ^               +-----------------+
                                          |
                                  +-----------------+
                                  | Tercero (curl,  |
                                  | vehiculo, app)  |
                                  +-----------------+
```

Todo lo que se ve a la derecha de AWS IoT Core es **infraestructura serverless real** desplegada por scripts boto3. El simulador a la izquierda **representa la flota fisica** de sensores magneticos.

---

## 2. Que entrega el proyecto

| Entregable | Donde esta | Tamano aprox. |
|-----------|------------|-----------------|
| **Memoria tecnica completa (Markdown unificado)** | `memoria/MEMORIA_TECNICA.md` | ~100 KB / ~14000 palabras |
| **Memoria en LaTeX** | `memoria/MEMORIA_TECNICA.tex` | ~180 KB |
| **Memoria en PDF compilado** | `memoria/MEMORIA_TECNICA.pdf` | ~280 KB / 66 paginas |
| **Memoria troceada por secciones** | `memoria/00_*.md` ... `13_*.md` | 14 ficheros |
| **Diagramas** | `memoria/diagramas/` | (vacio; el autor anade capturas) |
| **Prototipo funcional (codigo)** | `prototipo/` | ~30 KB |
| **README de prototipo** | `prototipo/README.md` | - |
| **Especificacion OpenAPI 3.0** | `prototipo/api/openapi.yaml` | - |
| **Este README guia** | `README_GUIA.md` (raiz) | - |

Para subir al campus virtual conviene zipear `memoria/` + `prototipo/` + `README_GUIA.md` + `guia_proyecto.md` (de referencia).

---

## 3. Como esta estructurada la carpeta

```
proyectofinal/
|-- README_GUIA.md                   (este documento)
|-- guia_proyecto.md                  (enunciado normalizado, no se modifica)
|-- Guia_Docente_*.md                 (guia docente normalizada, no se modifica)
|-- temario/                          (materiales facilitados por el profesor)
|-- memoria/
|   |-- MEMORIA_TECNICA.md            (memoria unica concatenada)
|   |-- MEMORIA_TECNICA.tex           (version LaTeX generada por pandoc)
|   |-- MEMORIA_TECNICA.pdf           (PDF final compilado con xelatex)
|   |-- 00..13_*.md                   (secciones por separado)
|   |-- diagramas/                    (PNG/JPG: capturas e ilustraciones)
|-- prototipo/
    |-- README.md
    |-- requirements.txt
    |-- .env.example
    |-- infra/
    |   |-- common.py                 (constantes y helpers boto3)
    |   |-- 01_setup_iot_core.py      (Things, certificado, policy)
    |   |-- 02_setup_dynamodb.py      (2 tablas)
    |   |-- 03_setup_lambda.py        (3 funciones + IoT Topic Rule)
    |   |-- 04_setup_api_gateway.py   (REST API + stage prod)
    |   |-- 99_teardown.py            (borra TODO al terminar)
    |   |-- parking_zone_seed.json    (40 plazas reales con lat/lon)
    |-- simulator/
    |   |-- parking_sensor.py         (cliente MQTT/TLS por plaza)
    |   |-- fleet_runner.py           (orquesta N sensores)
    |   |-- certs/                    (generado tras 01_setup_iot_core)
    |-- lambdas/
    |   |-- ingest/handler.py
    |   |-- aggregator/handler.py
    |   |-- api/handler.py
    |-- api/openapi.yaml
    |-- dashboard/streamlit_app.py
```

---

## 4. Stack tecnologico elegido y por que

Las decisiones se justifican en detalle en la memoria tecnica. Aqui un resumen accionable para defensa:

| Capa | Eleccion | Por que (defensa de un minuto) |
|------|----------|---------------------------------|
| Sensor | Magnetico AMR bajo asfalto | Mejor coste/consumo/privacidad. >5 anos de pila. Maduro en el sector. |
| Conectividad sensor | NB-IoT | Cobertura LTE municipal sin desplegar nada propio. ~0.60 EUR/SIM/mes. Bajo consumo. |
| Backhaul gateway/camara | Fibra municipal / 5G | Capacidad y alimentacion electrica disponibles. |
| Cloud | AWS IoT Core + Lambda + DynamoDB + API Gateway | Serverless puro, multi-AZ, paga por uso, sin servidores que mantener. |
| Procesamiento | Lambda (piloto) / Apache Flink (ciudad) | Lambda alcanza para el piloto; Flink se introduce al escalar para CEP y ventanas. |
| Persistencia estado | DynamoDB on-demand | Latencia ms, absorbe picos, modelo clave-valor simple. |
| Persistencia historico | DynamoDB tabla aparte (piloto) / Timestream (ciudad) | Timestream es nativo para series temporales pero no esta en Academy. |
| Exposicion | API Gateway REST + OpenAPI + GeoJSON | Estandar; sustituible facilmente por NGSI-v2 (FIWARE) en ciudad. |
| Dashboard | Streamlit | Velocidad de desarrollo; suficiente para defensa; consume la API real. |
| Lenguaje | Python 3.13 | Mismo en cliente, infra y Lambdas. Familiar para data engineering. |

Decisiones explicitamente **descartadas** y por que:

- Camara ANPR por plaza: privacidad, coste, complejidad. Se reservan a accesos.
- Sigfox: incertidumbre comercial tras la quiebra de 2022.
- FIWARE / Flink ya en piloto: no aporta valor academico extra y consume tiempo del lab.
- Cognito / WAF / Certificado por dispositivo: necesarios en produccion, no en piloto academico (LabRole no permite crear roles propios).

---

## 5. Preparacion del entorno (una vez por equipo)

### 5.1 Software requerido

- Python 3.11+ (probado en 3.13.9). Descargable de `python.org`.
- AWS Academy Learner Lab con credenciales en `C:\Users\<user>\.aws\credentials`.
- Opcionalmente AWS CLI v2 para validacion manual.
- MiKTeX + pandoc si se quiere recompilar el PDF.

### 5.2 Instalacion de dependencias Python

```powershell
cd "D:\DISCO DURO PORTABLE\INGENIERIA\MASTER\14\INTERNET DE LAS COSAS Y SUS APLICACIONES\proyectofinal\prototipo"
python -m pip install -r requirements.txt
```

### 5.3 Validacion rapida de credenciales AWS

```powershell
python -c "import boto3; print(boto3.client('sts', region_name='us-east-1').get_caller_identity())"
```

Debe devolver `Account`, `Arn` con el rol `voclabs/<usuario>`. Si falla, refrescar las credenciales en el portal de AWS Academy.

---

## 6. Lanzamiento del prototipo de cero (cada sesion)

Tiempo total: **~3 minutos**. Hacerlo siempre con la cuenta del Lab recien activada (3h por ventana).

### 6.1 Desplegar la infraestructura AWS

```powershell
cd "D:\...\proyectofinal\prototipo\infra"
python 01_setup_iot_core.py
python 02_setup_dynamodb.py
python 03_setup_lambda.py
python 04_setup_api_gateway.py
```

Que hace cada script (resumen mental para defensa):

- **01_setup_iot_core.py**: crea Thing Type + Thing Group + 40 Things (uno por plaza, con `zoneId`, `street`, `lat`, `lon` como atributos buscables) + genera un certificado X.509 compartido + descarga `AmazonRootCA1.pem` + crea la policy MQTT restringida al patron de topic + adjunta todo entre si.
- **02_setup_dynamodb.py**: crea `smart-parking-albacete-state` (PK `spotId`) y `smart-parking-albacete-zone-kpis` (PK `zoneId`, SK `windowEnd`), ambas on-demand.
- **03_setup_lambda.py**: empaqueta cada `lambdas/{ingest,aggregator,api}/handler.py` en un zip, las publica con runtime Python 3.12 y rol `LabRole`, conecta la Lambda `ingest` a la IoT Topic Rule `smart_parking_albacete_ingest_rule`.
- **04_setup_api_gateway.py**: importa el OpenAPI generado al vuelo (4 endpoints) y despliega el stage `prod`. La URL queda guardada en `infra/infra_state.json`.

### 6.2 Generar trafico con el simulador

```powershell
cd "D:\...\proyectofinal\prototipo\simulator"
python fleet_runner.py --num-spots 40 --duration 180 --heartbeat 20 --tick 2
```

Lo que ves: una linea de log por sensor conectando, luego una "publicacion inicial" que siembra el estado en DynamoDB, y a partir de ahi cambios de estado segun los patrones de la zona.

### 6.3 Lanzar el dashboard

En **otra consola** (no cierres el simulador):

```powershell
cd "D:\...\proyectofinal\prototipo\dashboard"
python -m streamlit run streamlit_app.py
```

Se abre el navegador en `http://localhost:8501`. El dashboard se autoconfigura leyendo `infra/infra_state.json`.

### 6.4 Verificacion manual de la API

```powershell
$base = (Get-Content "..\infra\infra_state.json" | ConvertFrom-Json).apiBaseUrl
curl "$base/spots"
curl "$base/zones"
curl "$base/spots?zone=Z2-DEPORTIVO&format=geojson"
curl "$base/zones/Z1-CAMPUS/kpis?limit=10"
```

---

## 7. Como usar el sistema desplegado

### 7.1 Como operador municipal (dashboard)

1. KPIs cabecera: visi[on instantanea de plazas libres / ocupadas / sin datos.
2. Mapa: pinta cada plaza dentro de la BBOX UCLM. Hover muestra detalles.
3. Selector de sub-zona: filtra el detalle.
4. Grafico de barras: distribucion por sub-zona.
5. Serie temporal: evolucion del % de ocupacion (escoger la sub-zona).
6. Tabla de detalle de plazas: filtrable, exportable.

### 7.2 Como sistema externo (vehiculo autonomo, app movil)

Endpoints clave:

| Verbo | Ruta | Uso |
|-------|------|-----|
| GET | `/spots` | Lista de plazas |
| GET | `/spots?zone=Z1-CAMPUS` | Filtrado |
| GET | `/spots?format=geojson` | GeoJSON RFC 7946 para mapas |
| GET | `/spots/ALB-Z1-001` | Detalle de una plaza |
| GET | `/zones` | KPIs vivos por sub-zona |
| GET | `/zones/Z1-CAMPUS/kpis?limit=50` | Serie temporal |

Ejemplos con `curl`: ver seccion 6.4.

Para integrar con un mapa real (Leaflet, MapLibre, Google Maps), basta con consumir el GeoJSON y pintarlo como capa: el campo `properties.color` ya viene con el color sugerido.

---

## 8. Como visualizar los resultados

| Vista | Donde | Pasos |
|-------|-------|-------|
| Dashboard live | Streamlit local | `streamlit run dashboard/streamlit_app.py` |
| Estado raw en DynamoDB | Consola AWS | DynamoDB > Tables > `smart-parking-albacete-state` > Explore items |
| Eventos MQTT al vuelo | Consola AWS | IoT > Test > MQTT test client > Subscribe `parking/#` |
| Logs Lambda | CloudWatch | Log groups > `/aws/lambda/smart-parking-albacete-ingest` |
| Trafico API Gateway | Consola AWS | API Gateway > APIs > `smart-parking-albacete-api` > Monitor |
| GeoJSON en un visor publico | `geojson.io` | Pegar el output de `?format=geojson` |

---

## 9. Como explicar el proyecto en defensa

Guion sugerido (~10 minutos):

1. **Contexto** (1 min): Smart parking en zona universitaria de Albacete; cliente ficticio TECO S.L. Mostrar mapa con la BBOX.
2. **Requisitos** (1 min): RF principales (estado plaza, API, dashboard) y RNF (latencia <5 s, escalable, RGPD).
3. **Telemetria + conectividad** (2 min): por que sensor magnetico + NB-IoT; descartes de camaras y Sigfox.
4. **Arquitectura cloud** (2 min): diagrama del capitulo 5 de la memoria. Insistir en serverless + multi-AZ.
5. **Demo en vivo** (3 min): dashboard ya cargado, lanzar simulador en una consola, ver KPIs cambiar, mostrar curl al GeoJSON, mostrar consola AWS con los Things.
6. **Escalado y coste** (1 min): tablas del capitulo 9-10. Coste cloud ~6 cts/plaza/mes.
7. **Limitaciones y futuro** (30 s): capitulo 12.

Preguntas frecuentes (con respuestas listas en el capitulo 13 de la memoria):

- Por que sensor magnetico y no camara.
- Que pasa si falla un sensor o gateway.
- Como evitas falsos libres/ocupados.
- Como escala de 500 a 10 000 plazas.
- Que latencia se espera y de donde sale.
- Que es estado y que es historico.
- Como proteges las APIs.
- Que es real y que esta simulado.
- Por que no FIWARE / Flink en el piloto.
- Que limitaciones tiene.

---

## 10. Compilacion de la memoria a PDF

La memoria esta troceada en 14 ficheros (`memoria/00_*.md` a `13_*.md`), concatenada en `memoria/MEMORIA_TECNICA.md` y convertida a `MEMORIA_TECNICA.tex` y `MEMORIA_TECNICA.pdf`.

### 10.1 Recompilacion (solo si modificas la memoria)

```powershell
cd "D:\...\proyectofinal\memoria"

# Recompone el .md unificado a partir de las secciones
# (script PowerShell incluido en el README de prototipo)

# Genera .tex y .pdf con pandoc + xelatex
pandoc MEMORIA_TECNICA.md --pdf-engine=xelatex -o MEMORIA_TECNICA.tex
pandoc MEMORIA_TECNICA.md --pdf-engine=xelatex -o MEMORIA_TECNICA.pdf

# O bien, directamente xelatex sobre el .tex (mas rapido en sucesivas iteraciones)
xelatex -interaction=nonstopmode MEMORIA_TECNICA.tex
xelatex -interaction=nonstopmode MEMORIA_TECNICA.tex   # 2a pasada para indice y referencias
```

Configuracion aplicada (frontmatter YAML embebido):

- Idioma: `es-ES`.
- Clase: `report`.
- Margenes: 2.5 cm en los cuatro lados.
- Fuente: Calibri 11 pt; codigo en Consolas.
- Indice automatico (toc) hasta profundidad 3.
- Numeracion de secciones automatica.
- Enlaces internos azules y clicables.

### 10.2 Que comprobar visualmente

- [x] Portada con titulo, subtitulo, autor y fecha.
- [x] Indice general clickable con paginas.
- [x] Numeracion de capitulos y subsecciones consistente.
- [x] Tablas dentro de los margenes (longtable se ocupa de partir paginas).
- [x] Codigo `monospace` legible.
- [x] Caracteres con tildes y "n" correctamente renderizados.

---

## 11. Capturas de pantalla que debe hacer el autor

> **Importante**: estas capturas se incluyen en la memoria pero el agente no puede generarlas (son del sistema operativo y de la consola AWS). Hazlas mientras el lab esta activo y el simulador corriendo, y guardalas en `memoria/diagramas/` con el nombre indicado.

**Capturas de la consola AWS** (mientras el lab esta activo):

1. `captura_aws_iot_things.png` -- AWS IoT > Manage > All devices > Things, lista con los 40 Things `ALB-Z1-001` a `ALB-Z4-010`.
2. `captura_aws_iot_mqtt_test.png` -- AWS IoT > Test > MQTT test client suscrito a `parking/#` con varios mensajes JSON visibles.
3. `captura_aws_iot_rule.png` -- AWS IoT > Message Routing > Rules > `smart_parking_albacete_ingest_rule` con el SQL y la accion Lambda visibles.
4. `captura_aws_dynamodb_state.png` -- DynamoDB > Tables > `smart-parking-albacete-state` > Explore items.
5. `captura_aws_dynamodb_kpis.png` -- DynamoDB > Tables > `smart-parking-albacete-zone-kpis` > Explore items con varios `windowEnd`.
6. `captura_aws_lambda_ingest.png` -- Lambda > `smart-parking-albacete-ingest` > Configuration general.
7. `captura_aws_cloudwatch_ingest.png` -- CloudWatch > Log groups > `/aws/lambda/smart-parking-albacete-ingest` con eventos recientes.
8. `captura_aws_apigateway.png` -- API Gateway > `smart-parking-albacete-api` > Resources con los 4 paths.

**Capturas del dashboard local** (Streamlit corriendo):

9. `captura_dashboard_principal.png` -- vista completa con KPIs y mapa.
10. `captura_dashboard_kpis_zona.png` -- seccion de KPIs por sub-zona con grafico de barras.
11. `captura_dashboard_serie_temporal.png` -- seccion de evolucion temporal con linea curva.

**Capturas de consola** (PowerShell):

12. `captura_curl_geojson.png` -- consola con la respuesta GeoJSON formateada.
13. `captura_curl_zones.png` -- consola con la respuesta de `/zones`.

**Diagramas de la zona piloto** (opcional, mejora la portada del capitulo 1):

14. `mapa_bbox_albacete.png` -- captura del mapa de Google Maps con la BBOX dibujada (la imagen que enviaste).

Una vez generadas, pueden insertarse en la memoria editando el .md (Markdown estandar: `![texto](diagramas/nombre.png)`) y recompilando.

---

## 12. Diario cronologico de lo que hizo el agente

Esta seccion documenta literalmente la secuencia de acciones que el agente ejecuto, para que el autor pueda rehacerlas y para acreditar autoria/trazabilidad en la entrevista PR2.

### Sesion 16 de mayo de 2026

1. Exploracion de la carpeta `proyectofinal/` y lectura de:
   - `guia_proyecto.md`
   - `Guia_Docente_INTERNET_DE_LAS_COSAS_Y_SUS_APLICACIONES.md`
   - `temario/tema4.md` (FIWARE) y `temario/tema5.md` (Flink)
   - PDFs del temario (AWS IoT Core, ecosistema AWS).
2. Verificacion del entorno: Python 3.13.9, Node 20, ausencia de AWS CLI y boto3.
3. Validacion de credenciales del lab: cuenta `583916379944`, region `us-east-1`, rol `voclabs`. Confirmacion de existencia del `LabRole`.
4. Decisiones de alcance acordadas con el usuario:
   - Despliegue real completo en AWS Academy.
   - FIWARE/Flink solo a nivel de diseno.
   - Dashboard en Streamlit minimalista.
   - Estructura `memoria/` + `prototipo/` + `README_GUIA.md`.
   - BBOX real: SW (38.976059, -1.858728) - NE (38.983215, -1.846111) y 4 sub-zonas Z1..Z4.
5. Creacion del esqueleto de carpetas y `prototipo/parking_zone_seed.json` con 40 plazas en coordenadas reales sobre los ejes viarios identificados.
6. Instalacion de dependencias Python (boto3, awsiotsdk, paho-mqtt, streamlit, plotly, pydeck, etc.).
7. Implementacion de los scripts `infra/01..04` y `99_teardown.py`, mas el modulo `common.py`. Sanitizacion de atributos de Things para cumplir el regex de AWS IoT.
8. Implementacion de las tres Lambdas (`ingest`, `aggregator`, `api`) y de la spec `openapi.yaml`.
9. Implementacion del simulador (`parking_sensor.py` + `fleet_runner.py`) con perfiles de zona realistas.
10. Implementacion del dashboard Streamlit con mapa pydeck.
11. Despliegue real en AWS:
    - `01_setup_iot_core.py`: 40 Things, certificado X.509 compartido, policy, ThingGroup.
    - `02_setup_dynamodb.py`: 2 tablas en modo on-demand.
    - Ajuste de `03_setup_lambda.py` para usar `list_topic_rules` (LabRole no autoriza `get_topic_rule`) y para esperar a que las Lambdas esten en estado `Active` antes de cada `update`.
    - `03_setup_lambda.py`: 3 Lambdas creadas, IoT Topic Rule activa.
    - `04_setup_api_gateway.py`: API REST con stage `prod` y URL publica `https://85fbp0svzc.execute-api.us-east-1.amazonaws.com/prod`.
12. Verificacion end-to-end con el simulador (60 s, 40 sensores). Validacion de `GET /spots`, `/zones`, `/spots?format=geojson`, `/zones/{id}/kpis`. Todas correctas.
13. Generacion de trafico continuo durante 3 min para alimentar la serie temporal de KPIs.
14. Redaccion de las 14 secciones de la memoria tecnica (`00_*.md` a `13_*.md`) en castellano, registrando datos reales del despliegue.
15. Concatenacion en `MEMORIA_TECNICA.md` con frontmatter YAML para pandoc.
16. Instalacion de pandoc 3.9 via winget. Generacion de `MEMORIA_TECNICA.tex` y compilacion de `MEMORIA_TECNICA.pdf` con xelatex (66 paginas).
17. Redaccion de este `README_GUIA.md`.
18. Teardown final con `99_teardown.py`.

---

## 13. Mapeo entregables - guia docente y enunciado

### 13.1 Cumplimiento del enunciado del campus virtual

| Punto del enunciado | Donde se cubre |
|---------------------|----------------|
| Descripcion del problema | `memoria/01_descripcion_problema.md` |
| Arquitectura propuesta detallada (con diagramas) | `memoria/05_arquitectura_cloud_aws.md` y diagramas mermaid |
| Analisis de costes aproximado | `memoria/10_analisis_costes.md` |
| Discusion sobre escalabilidad | `memoria/09_escalabilidad_piloto_ciudad.md` |
| Prototipo funcional minimo | `prototipo/` (todo el codigo + despliegue real) |
| Simulacion de la capa de sensorizacion | `prototipo/simulator/` |
| Dashboard / panel de control | `prototipo/dashboard/streamlit_app.py` |
| Defensa del proyecto | `memoria/13_defensa.md` |

### 13.2 Cumplimiento de los resultados de aprendizaje (guia docente)

| RA | Donde se cubre en la memoria |
|----|------------------------------|
| **CN02** (arquitecturas masivas) | Capitulos 5, 7, 9 |
| **HA03** (ETL / data lakes) | Capitulo 7 (modelo) + diseno S3 raw bronze en capitulo 9 |
| **CP02** (IoT, edge, streams) | Capitulos 3, 4, 5, 6 |

---

## 14. Glosario tecnico para repaso de defensa

| Termino | Que es y por que importa |
|---------|---------------------------|
| **MQTT** | Protocolo pub/sub ligero estandar IoT, sobre TCP. Cabecera minima (~2 bytes). |
| **mTLS** | TLS con autenticacion mutua (cliente y servidor presentan cert). Lo usa AWS IoT por defecto. |
| **Thing** | Representacion virtual de un dispositivo fisico en AWS IoT. Tiene atributos buscables. |
| **Device Shadow** | Documento JSON persistente que refleja el estado deseado y reportado de un Thing. No usado en este piloto. |
| **IoT Rule** | Regla SQL que filtra mensajes MQTT y los redirige a otros servicios AWS (Lambda, S3, Kinesis...). |
| **Lambda (AWS)** | Funcion serverless invocable por eventos. Sin servidor que gestionar. |
| **DynamoDB** | BBDD NoSQL de AWS, key-value y document, latencia ms, escalado automatico. |
| **On-demand** | Modo de facturacion de DynamoDB sin capacidad provisionada: paga por peticion. |
| **API Gateway** | Servicio AWS para crear y publicar APIs REST/HTTP/WebSocket gestionadas. |
| **GeoJSON** | Formato JSON estandar (RFC 7946) para datos geograficos. |
| **NGSI-v2** | API REST de FIWARE para gestion de contexto en smart cities. |
| **NB-IoT** | Variante LPWAN de LTE para IoT de baja energia y bajo coste, cobertura del operador. |
| **LoRaWAN** | LPWAN open spectrum (868 MHz EU). Requiere gateways propios. Sin coste por mensaje. |
| **C-V2X** | Cellular V2X. Comunicacion vehiculo-infraestructura sobre LTE/5G. |
| **CAPEX / OPEX** | Inversion inicial (capital) vs gasto operativo recurrente. |
| **LabRole** | Rol IAM predefinido en AWS Academy Learner Lab; el unico utilizable por las Lambdas. |
| **Idempotente** | Una operacion que produce el mismo resultado al ejecutarse N veces. Critico para scripts de infra. |

---

## 15. Apagado y limpieza (obligatorio al cerrar el lab)

Antes de cerrar la sesion de AWS Academy (o cuando se acaben las 3 h):

```powershell
cd "D:\...\proyectofinal\prototipo\infra"
python 99_teardown.py
```

Esto borra (en orden seguro):

1. API Gateway REST.
2. Las 3 Lambdas (`ingest`, `aggregator`, `api`).
3. La IoT Topic Rule.
4. Los 40 Things, desvinculandolos del certificado.
5. La policy y el certificado X.509.
6. El Thing Group y deprecate del Thing Type.
7. Las 2 tablas DynamoDB.

Al terminar, `infra_state.json` queda vacio. Es seguro relanzar todo en la proxima sesion.

> **Nota**: el lab academico se reinicia entre sesiones; si por algun motivo el teardown falla, no hay coste asociado (el lab tiene cuota acotada).

---

## 16. FAQ y resolucion de problemas

### Error: "Thing attribute failed regex" al ejecutar `01_setup_iot_core.py`

Los atributos de un Thing en AWS IoT no admiten espacios ni caracteres exoticos. El script ya sanitiza (`C. Imperial` -> `C._Imperial`), pero si has anadido plazas nuevas al seed, asegurate de que `street` no contenga caracteres fuera del regex `[a-zA-Z0-9_.,@/:#=\[\]-]`.

### Error: "Access to GetTopicRule was denied"

`LabRole` no autoriza `iot:GetTopicRule`. El script utiliza `list_topic_rules` para detectar si la regla existe. Ya esta resuelto en `03_setup_lambda.py`.

### Error: "An update is in progress for resource: ...Lambda..."

Las Lambdas no aceptan dos `update_function_*` consecutivos sin esperar a que la anterior termine. La funcion `_wait_function_ready` en `03_setup_lambda.py` espera al estado `Active` con `LastUpdateStatus = Successful`.

### El dashboard no carga datos

- Comprueba que `infra/infra_state.json` contiene `apiBaseUrl`.
- Lanza una peticion manual: `curl <apiBaseUrl>/spots` desde otra consola.
- Revisa la consola del navegador (F12) por errores CORS: el Lambda de la API anade `Access-Control-Allow-Origin: *`.

### Quiero anadir mas plazas

Edita `prototipo/infra/parking_zone_seed.json` siguiendo el mismo formato y vuelve a ejecutar `01_setup_iot_core.py`. Es idempotente: solo creara Things que no existan.

### El simulador termina sin generar trafico

El bucle se rompe si `--duration` es 0 o muy bajo. Para ejecucion indefinida usa `--duration 0`. Para pruebas cortas, al menos `--duration 60 --tick 2`.

### Recompilar el PDF tras editar la memoria

```powershell
cd "D:\...\proyectofinal\memoria"
xelatex -interaction=nonstopmode MEMORIA_TECNICA.tex
xelatex -interaction=nonstopmode MEMORIA_TECNICA.tex
```

(La 2a pasada actualiza indice y referencias cruzadas.)

### El PDF no respeta los margenes de mi institucion

Edita el frontmatter al inicio de `MEMORIA_TECNICA.md`:

```yaml
geometry:
  - margin=3cm
  - top=3cm
  - bottom=3cm
```

y vuelve a compilar.

---

**Fin del README guia.** Cualquier duda no cubierta aqui esta detallada en la memoria tecnica (`memoria/MEMORIA_TECNICA.pdf`) o en los comentarios del codigo del prototipo (`prototipo/`).
