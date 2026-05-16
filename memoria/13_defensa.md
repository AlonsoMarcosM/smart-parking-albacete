# 13. Preparación de la defensa

La guía docente otorga **20 % de la nota (TR2)** a la defensa oral y **5 % (PR2)** a la entrevista de autoría. Este capítulo recopila las preguntas previsibles, las respuestas razonadas y los puntos de control que el alumno debe dominar antes de la defensa.

## 13.1 Guion sugerido (10 minutos)

| Minuto | Contenido | Apoyo visual |
|--------|-----------|--------------|
| 0:00 - 1:00 | Presentación: nombre, asignatura, cliente ficticio, problema | Slide portada con BBOX y foto satélite zona |
| 1:00 - 2:30 | Requisitos funcionales y no funcionales más relevantes | Slide con tabla resumen capítulo 2 |
| 2:30 - 4:00 | Decisión telemetría + conectividad | Slides con comparativa de los capítulos 3 y 4 |
| 4:00 - 6:00 | Arquitectura cloud AWS, flujo extremo a extremo | Diagrama mermaid del capítulo 5 |
| 6:00 - 8:00 | **Demostración en vivo del prototipo** | Dashboard + consola AWS IoT + curl |
| 8:00 - 9:00 | Escalabilidad y coste | Tablas capítulos 9 y 10 |
| 9:00 - 10:00 | Limitaciones, trabajo futuro y conclusiones | Capítulo 12 |

## 13.2 Preguntas previsibles y respuestas

### 13.2.1 ¿Por qué elegiste sensores magnéticos en lugar de cámaras?

- Privacidad (no captura matrículas).
- Consumo (vida útil 5-7 años con pila D).
- Coste (~75 € frente a 500-1200 € de una cámara que cubre 5-10 plazas).
- Robustez climática (IP68 bajo asfalto).
- Las cámaras se reservan para los accesos como conteo agregado y posible control de zonas de bajas emisiones.

### 13.2.2 ¿Qué pasa si falla un sensor o un gateway?

- Pérdida de señal del sensor: el agregador no recibe heartbeat. Mecanismo previsto (trabajo futuro): EventBridge cron + Lambda que audita `lastUpdated` y emite alerta a SNS.
- Pérdida del gateway edge: en NB-IoT directo no hay gateway propio. Para sensores LoRaWAN se mitiga con redundancia (un gateway adicional por zona).
- Pérdida de conectividad temporal: el sensor mantiene caché local y reenvía al recuperar (en el simulador no se ha implementado, sí se documenta).

### 13.2.3 ¿Cómo evitas reportar falsos libres/ocupados?

- Debounce en edge: el cambio sólo se considera tras 2-3 s estables.
- Umbral de `confidence` en el sensor (campo en el payload).
- Calibración inicial in situ del magnetómetro.
- Filtrado adicional en Lambda ingest (descartar payloads malformados).

### 13.2.4 ¿Cómo escalas la arquitectura de 500 a 10 000 plazas?

Resumen del capítulo 9:

- Sensores: certificado por dispositivo via Fleet Provisioning Templates.
- Procesamiento: Kinesis Data Streams + Managed Apache Flink en lugar de Lambda agregador.
- Estado: añadir GSI `zoneId-status-index` en DynamoDB.
- Histórico: migrar `zone-kpis` a Amazon Timestream.
- API: WAF + CloudFront caché + cuotas.
- Coste cloud: ~625 €/mes (6 céntimos por plaza/mes).

### 13.2.5 ¿Qué latencia se espera y de dónde sale?

- NB-IoT: 1-3 s típicos (CP/IDLE -> conexión radio + envío IP).
- IoT Core → IoT Rule → Lambda → DynamoDB: 50-300 ms.
- DynamoDB → API Gateway → cliente: 100-500 ms.
- **Total**: < 5 s extremo a extremo. Medido en el prototipo: **2-3 s** entre publicación del simulador y refresco en el dashboard.

### 13.2.6 ¿Qué datos guardas como estado y cuáles como histórico?

- **Estado actual** en `parking-state`: el último valor de cada plaza, sobrescrito por cada evento.
- **Histórico operacional** en `zone-kpis`: una fila por cada cálculo del agregador, indexada por `(zoneId, windowEnd)`. Permite reconstruir cómo cambió la ocupación en el tiempo.
- **Raw events** (diseño, no implementado): cada mensaje crudo a S3 (data lake bronze) para analítica futura con Athena.

### 13.2.7 ¿Cómo proteges las APIs?

- HTTPS obligatorio (TLS 1.2+).
- CORS controlado en Lambda.
- API Gateway permite throttling y API keys (no activados en piloto, diseñados para producción).
- WAF y Cognito como ampliaciones en producción.
- IAM principle of least privilege: en piloto se usa `LabRole`, en producción un rol por Lambda.

### 13.2.8 ¿Qué parte del prototipo es real y qué parte está simulada?

Real (corriendo en AWS):

- AWS IoT Core con 40 Things, certificado, policy, Topic Rule.
- 3 Lambdas (`ingest`, `aggregator`, `api`).
- 2 tablas DynamoDB (`parking-state`, `zone-kpis`).
- API Gateway REST con stage `prod`.
- Dashboard Streamlit consumiendo la API real.

Simulado:

- Los sensores físicos (sustituidos por un cliente paho-mqtt que habla MQTT/TLS contra IoT Core, exactamente igual que un sensor real haría).
- Las cámaras ANPR (solo se documentan).
- El gateway edge (su lógica de debounce está dentro del simulador).

### 13.2.9 ¿Por qué decidiste no implementar FIWARE / Flink?

- AWS Academy Lab dura 3 h: gastarlas en levantar Orion + Flink no aporta valor académico, ya que el flujo conceptual queda demostrado con la implementación AWS.
- En el piloto, el coste/beneficio de Flink es negativo (Lambda alcanza sobradamente).
- Se ha dejado el diseño detallado de la integración para el escenario ciudad, donde sí aporta valor (capítulo 6 y 9).

### 13.2.10 ¿Qué limitaciones tiene la solución?

Resumen del capítulo 12:

- Certificado X.509 compartido (cambiable a por-dispositivo).
- Sin alertas automáticas de sensores caídos (Lambda cron + SNS futuro).
- Sin autenticación de la API pública (API Keys + WAF futuro).
- Sin predicción ML (SageMaker futuro).
- Sin app ciudadana (PWA futura).

## 13.3 Resultados de aprendizaje y dónde se cubren

| RA | Cobertura |
|----|-----------|
| **CN02** (arquitecturas de tratamiento masivo) | Capítulos 5, 7, 9. |
| **HA03** (orquestación ETL / data lakes) | Capítulo 7 (modelo de datos) + diseño S3 raw bronze (capítulo 9). |
| **CP02** (IoT, edge, streams) | Capítulos 3 (telemetría), 4 (conectividad), 5 (cloud) y 6 (Flink). |

## 13.4 Checklist final antes de la entrega

- [ ] La memoria (`MEMORIA_TECNICA.md` + `.tex` + `.pdf`) está en `memoria/`.
- [ ] El prototipo es ejecutable de cero siguiendo `README_GUIA.md` y `prototipo/README.md`.
- [ ] Las capturas de pantalla del capítulo 11 están en `memoria/diagramas/`.
- [ ] El `99_teardown.py` se ha ejecutado tras la demo (no quedan recursos en AWS).
- [ ] El ZIP final no contiene credenciales (`.aws/`, `infra/infra_state.json`, `simulator/certs/`).
- [ ] El nombre del autor consta como `alonso.marcos@alu.uclm.es`.

## 13.5 Recordatorio operativo de defensa

- Llegar 15 min antes con la sesión de AWS Academy ya iniciada y el despliegue corriendo.
- Tener navegador con tres pestañas listas: Streamlit, AWS IoT MQTT test client, AWS DynamoDB Explore.
- Tener una pestaña con la memoria en PDF para señalar tablas/diagramas si surge la duda.
- Practicar la demo en seco al menos dos veces para que el simulador y el dashboard estén sincronizados.
- Estar preparado para responder en castellano y, si el tribunal lo pide, mostrar dónde en el código se implementa cada decisión.
