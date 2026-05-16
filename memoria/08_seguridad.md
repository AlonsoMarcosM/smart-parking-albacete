# 08. Seguridad y privacidad

La seguridad en IoT no es una capa que se añada al final: hay que diseñarla en todas las fases del ciclo (provisión, comunicación, persistencia, exposición y operación). Este capítulo describe las decisiones de seguridad adoptadas en el prototipo y las ampliaciones planificadas para producción, distinguiendo siempre lo que ya está **implementado** de lo que está **diseñado pero no desplegado**.

## 8.1 Modelo de amenazas (resumen)

| Activo | Amenaza | Vector | Mitigación |
|--------|---------|--------|------------|
| Sensor en calzada | Manipulación física, robo | Acceso físico | Caja blindada, anclaje, alarma de movimiento. |
| Identidad del sensor | Suplantación | Robo de certificado | Certificado por dispositivo, rotación, revocación. |
| Canal sensor↔cloud | Eavesdropping, MITM | Red pública | mTLS (TLS 1.2 con certificado mutuo). |
| Cloud (datos) | Acceso no autorizado | Credenciales filtradas | IAM con principio de mínimo privilegio; auditoría. |
| API pública | Abuso, scraping, DoS | Internet | Throttling, cuotas, API keys, WAF. |
| Datos personales | Inferencia de hábitos | Trazas de matrículas | El sistema no almacena matrículas ni datos del conductor. |
| Datos operacionales | Modificación maliciosa | Atacante con credenciales | Auditoría inmutable, logs en bucket separado. |
| Firmware del sensor | Backdoor en actualizaciones | Despliegue OTA | Firma criptográfica del firmware, validación en el dispositivo. |

## 8.2 Capa de dispositivo (provisión e identidad)

**Implementado en el prototipo:**

- Cada **Thing** en AWS IoT Core representa una plaza identificable de forma única (`ALB-Z1-001`, …).
- Un único **certificado X.509** compartido por toda la flota piloto, atado a una **IoT Policy** restrictiva (`smart-parking-albacete-sensor-policy`).
- La policy autoriza únicamente `Connect`, `Publish`, `Subscribe`, `Receive` y solo sobre topics que comienzan por `parking/`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": "iot:Connect", "Resource": "*"},
    {"Effect": "Allow", "Action": "iot:Publish",   "Resource": "arn:aws:iot:*:*:topic/parking/*"},
    {"Effect": "Allow", "Action": "iot:Subscribe", "Resource": "arn:aws:iot:*:*:topicfilter/parking/*"},
    {"Effect": "Allow", "Action": "iot:Receive",   "Resource": "arn:aws:iot:*:*:topic/parking/*"}
  ]
}
```

**Diseñado para producción (no en piloto):**

- **Un certificado por dispositivo** (`Just-in-Time Provisioning` o `Fleet Provisioning Templates`): permite revocaciones granulares y auditoría individual.
- **Renovación periódica** de certificados (cada 12-24 meses) mediante el endpoint `iot:UpdateCertificate`.
- **AWS IoT Device Defender** activado para auditar configuraciones (políticas demasiado permisivas, certificados a punto de expirar) y detectar comportamiento anómalo (volumen de mensajes inusual, conexión desde IP no habitual).

## 8.3 Capa de transporte

- **TLS 1.2** obligatorio en todas las conexiones MQTT (puerto 8883). Cifrado AES-128/256 según negociación.
- **mTLS** (autenticación mutua) con certificado del cliente firmado por la CA de AWS IoT Core.
- Verificación del certificado raíz **AmazonRootCA1.pem** en el dispositivo (incluido en los certificados que se descargan en `simulator/certs/`).
- API REST **siempre por HTTPS** (TLS 1.2+) con el certificado gestionado por API Gateway.

## 8.4 Capa de procesamiento (Lambdas)

- Las tres Lambdas se ejecutan bajo `LabRole`, un rol del lab de Academy con permisos sobre los servicios que el laboratorio expone. En producción se sustituiría por **un rol IAM por Lambda** con políticas a medida (principio de mínimo privilegio):
  - `lambda-ingest-role`: permisos `dynamodb:PutItem` sobre `parking-state` y `lambda:InvokeFunction` sobre el agregador.
  - `lambda-aggregator-role`: `dynamodb:Scan` (con condición sobre `zoneId`) sobre `parking-state` y `dynamodb:PutItem` sobre `zone-kpis`.
  - `lambda-api-role`: `dynamodb:GetItem` / `Query` / `Scan` sobre las dos tablas (solo lectura).
- Variables de entorno **sin credenciales en claro**; los nombres de tabla y de función auxiliar viajan como `STATE_TABLE`, `KPIS_TABLE`, `AGGREGATOR_FN`.
- Trazabilidad: cada invocación genera logs en CloudWatch con request ID, código de estado y tiempo.

## 8.5 Capa de persistencia

- DynamoDB está cifrado **en reposo por defecto** con claves gestionadas por AWS (AWS KMS).
- En producción se utilizaría **CMK propia** (Customer Master Key) para satisfacer auditorías y políticas internas.
- Backup: DynamoDB on-demand permite habilitar `Point-in-Time Recovery` (PITR) con 35 días de retención. Recomendado activarlo en producción.

## 8.6 Capa de exposición (API)

**Implementado:**

- HTTPS con TLS 1.2+ en API Gateway.
- CORS controlado a nivel de Lambda (necesario para Streamlit local).

**Diseñado para producción:**

- **API Keys + Usage Plans** en API Gateway para terceros: throttling por minuto y cuotas mensuales (p. ej. 10 000 peticiones/día por aplicación).
- **Amazon Cognito** o **JWT custom** para diferenciar API pública (sin auth o con clave) vs API interna del operador (autenticada).
- **AWS WAF** delante de API Gateway para mitigar abuso, OWASP Top 10 y rate-limiting basado en IP.
- **Custom domain** con certificado ACM para una URL estable y fácil de comunicar a integradores.

## 8.7 Capa de operación

- **CloudWatch Logs**: retiene los logs de cada Lambda y de la IoT Rule con retención configurable.
- **CloudTrail** (activo por defecto en la cuenta) audita todas las llamadas a la API de AWS (quién creó/borró/modificó qué).
- **AWS Config** (recomendado en producción) para alertar de cambios en políticas IAM o en certificados IoT.
- **Auditoría de manipulación**: los Things creados quedan registrados con timestamp; cualquier cambio futuro genera evento de CloudTrail.

## 8.8 Cumplimiento RGPD y privacidad

El diseño es **privacy by design**:

- **No se almacenan datos personales** identificables. La unidad mínima de información es la plaza, no el conductor.
- Las cámaras ANPR (capa complementaria) procesan la matrícula **localmente en el gateway** y solo envían a la cloud un **hash unidireccional** y la dirección de paso. Las imágenes originales se retienen un máximo de 72 horas localmente para reclamaciones, y después se borran (LOPDGDD y RGPD).
- Las consultas de la API son **anónimas** para el consumidor; no se trazan identidades de usuario final.
- **Política de retención** para los KPIs: 24 meses agregados; los logs operacionales rotan a S3 Glacier después de 90 días.

## 8.9 Plan de respuesta a incidentes (resumen)

1. **Detección**: alertas de CloudWatch o IoT Device Defender (intentos de conexión rechazados, picos de tráfico anómalos).
2. **Contención**: revocación inmediata del certificado afectado con `iot:UpdateCertificate(newStatus="REVOKED")`.
3. **Erradicación**: rotación de certificados afectados, sustitución física del sensor si hay sospecha de tampering.
4. **Recuperación**: restauración del estado desde DynamoDB PITR si fue manipulado.
5. **Post-mortem**: revisión de logs CloudTrail y CloudWatch; informe a la concejalía; mejora de la policy o de la lógica afectada.

## 8.10 Resumen de cumplimiento de requisitos no funcionales de seguridad

| Requisito | Estado |
|-----------|--------|
| RNF-09 (cifrado en tránsito) | OK (MQTT/TLS, HTTPS) |
| RNF-10 (identidad por dispositivo) | Parcial en piloto (cert compartido); diseñado por dispositivo en producción |
| RNF-11 (control de consumo API) | Diseñado (API Keys + WAF) |
| RNF-12 (sin PII) | OK |
| RNF-13 (auditoría y trazabilidad) | OK (CloudWatch, CloudTrail) |
| RNF-20 (RGPD) | OK (privacy by design) |
