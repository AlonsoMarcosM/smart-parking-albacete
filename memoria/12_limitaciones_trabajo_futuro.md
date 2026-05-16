# 12. Limitaciones y trabajo futuro

Ningún piloto es la versión final. Este capítulo enumera honestamente las limitaciones de la solución entregada y propone una hoja de ruta para los siguientes pasos. Esta sinceridad es importante de cara a la defensa: muestra capacidad crítica y demuestra que el autor distingue lo que está demostrado de lo que está pendiente.

## 12.1 Limitaciones derivadas del entorno académico

| Limitación | Impacto | Mitigación / Plan |
|------------|---------|-------------------|
| Credenciales AWS Academy caducan a las 3 h | El despliegue debe completarse y demostrarse en una sesión | Scripts idempotentes (`infra/*.py`) y `99_teardown.py`. |
| Solo `LabRole` para Lambda | No se pueden afinar permisos por servicio | Documentado; en producción se crea un rol por Lambda. |
| Servicios no disponibles en el lab | Amazon Timestream y Kinesis pueden no estar habilitados | Diseño documentado; no impacta el prototipo actual. |
| Cuenta compartida con compañeros | Posible colisión de nombres | Prefijo `smart-parking-albacete-` único. |

## 12.2 Limitaciones técnicas del prototipo

| Limitación | Impacto | Plan de futuro |
|------------|---------|----------------|
| Certificado X.509 compartido por toda la flota | Revocación granular imposible | AWS IoT Fleet Provisioning Templates por dispositivo. |
| `Scan` filtrado en DynamoDB | Coste creciente a partir de ~10 000 plazas | Crear GSI `zoneId-status-index`. |
| Agregador en Lambda síncrona | Latencia añadida en eventos correlacionados | Sustituir por Flink en escenario ciudad. |
| Sin alertas automáticas de sensor caído | Operador debe revisar manualmente | Job EventBridge cron + Lambda que audita `lastUpdated`. |
| Sin retentiva configurable en KPIs | Crece la tabla con el tiempo | Habilitar DynamoDB TTL o migrar a Timestream. |
| Sin autenticación en la API | Cualquiera puede consultar | API Keys + WAF + Cognito (diseñado, no implementado en piloto). |
| Dashboard local | No multi-usuario, sin permisos | Streamlit Cloud / ECS + Cognito o sustituir por QuickSight. |
| Una sola región (`us-east-1`) | Sin DR multi-región | Diseño con DynamoDB Global Tables; redespliegue por CDK. |
| Simulador en lugar de sensores reales | Comportamiento idealizado | Validar con sensores piloto (fase 1 del plan capítulo 4). |

## 12.3 Limitaciones funcionales

| Limitación | Por qué | Trabajo futuro |
|------------|---------|----------------|
| Sin estimación de duración de la ocupación | El agregador no calcula `dwell time` | Session windows en Flink. |
| Sin predicción a futuro | El piloto solo refleja el estado actual | Modelo ML batch en SageMaker; integrar predicciones en la API. |
| Sin gestión de plazas reservadas (PMR, carga eléctrica, residentes) | Modelo simplificado | Añadir atributo `restrictedTo` y reglas de visibilidad por consumidor. |
| Sin integración con sistema de cobro | Fuera de alcance | Integración con plataforma de tarificación municipal. |
| Sin panel del ciudadano | El dashboard es de operador | App ciudadana con tiles libres por zona y guiado por GPS. |
| Sin paneles de mensajería variable | Fuera de alcance | Integración con DMS municipales por API. |

## 12.4 Roadmap propuesto (12 meses)

| Mes | Hito |
|----|------|
| 1 | Piloto técnico con 20 sensores reales y validación del flujo end-to-end con tráfico real. |
| 2-3 | Despliegue de los 500 sensores piloto; calibración de patrones reales por zona. |
| 4 | Auditoría de seguridad (pentest) y endurecimiento (Cognito, WAF, Device Defender). |
| 5 | Integración FIWARE Orion para interoperabilidad con la plataforma municipal. |
| 6 | Migración del histórico a Timestream + cuadros de mando en QuickSight. |
| 7 | App móvil ciudadana (PWA) con localización de plazas libres más cercanas. |
| 8 | Introducción de Flink para KPIs por ventanas y detección de patrones. |
| 9 | Integración con paneles de mensajería variable municipales. |
| 10-12 | Extensión a 10 000 plazas; entrada en producción "ciudad". |

## 12.5 Investigación y mejoras prospectivas

- **Modelos de predicción de ocupación**: redes neuronales recurrentes (LSTM) o transformers entrenados con histórico anual y variables exógenas (calendario universitario, calendario deportivo, festividades, meteorología).
- **Routing dinámico para vehículos autónomos**: integración del API REST con plataformas C-V2X (RSU + MEC) para guiado plaza a plaza.
- **Carbon awareness**: correlación de ocupación con calidad del aire (nodos ambientales) para informar políticas de bajas emisiones.
- **Plazas reservables**: módulo de reserva temporal para vehículos eléctricos en carga o vehículos de emergencia.
- **Open data**: publicación del histórico anonimizado en el portal de datos abiertos del ayuntamiento.

## 12.6 Riesgos abiertos

| Riesgo | Mitigación recomendada |
|--------|------------------------|
| Cambio del operador NB-IoT con subida de precios | Cláusulas contractuales multianuales + alternativa LoRaWAN preparada. |
| Pérdida de soporte de un SDK / librería usado | Sin dependencias propietarias críticas; código modular fácil de migrar. |
| Resistencia ciudadana a las cámaras ANPR | Comunicación clara, política de retención breve, hash de matrículas. |
| Variabilidad meteorológica afecta a las baterías | Selección de sensores certificados para -20 a +60 °C; auditoría anual. |
| Vandalismo en una zona concreta | Movilizar cuadrilla de mantenimiento; reposición rápida (sensor barato). |
