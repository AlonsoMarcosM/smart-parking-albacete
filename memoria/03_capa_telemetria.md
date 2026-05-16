# 03. Capa de telemetría

La capa de telemetría es la base del sistema: si el sensor no detecta correctamente la ocupación o no es operable a coste razonable, toda la capa de datos posterior pierde valor. Este capítulo justifica la combinación de sensores elegida tras una comparación explícita de alternativas, atendiendo a precisión, coste, consumo energético, robustez al entorno, dificultad de instalación, mantenimiento y privacidad.

## 3.1 Catálogo de tecnologías evaluadas

| Tecnología | Principio físico | Producto comercial de referencia |
|------------|------------------|-----------------------------------|
| Magnético AMR pasivo | Distorsión del campo magnético terrestre por la masa metálica del vehículo | Nedap SENSIT (1-2), Smart Parking PS101, Bosch INA213 |
| Ultrasonido | Tiempo de vuelo de un eco entre el sensor cenital y el suelo/coche | Libelium Smart Parking Ultrasonic, Worldsensing Fastprk-U |
| Radar mmWave | Detección de presencia / movimiento por reflexión electromagnética | TI IWR6843, Vayyar (multi-plaza) |
| LIDAR 2D/3D | Telemetría láser; ideal para cubrir varias plazas a la vez | Velodyne Puck (estático), Quanergy M8 |
| Cámara visión artificial (ANPR + ocupación) | Procesamiento de imagen sobre stream de vídeo | Cámaras IP + algoritmo YOLO/EfficientDet en edge o cloud |
| Sensores ambientales (CO₂, ruido, temperatura) | Complemento de la calidad del entorno | Libelium Smart Cities, Adeunis Comfort |

## 3.2 Análisis comparativo

| Criterio | Magnético | Ultrasónico | Radar | LIDAR | Cámara ANPR |
|----------|-----------|-------------|-------|-------|-------------|
| Precisión detección ocupación | Alta (>95 %) si bien calibrado | Alta en interior; baja en exterior por lluvia/viento | Muy alta; tolera meteorología | Muy alta | Muy alta + matrícula |
| Identificación de vehículo | No | No | No | No (forma) | Sí (matrícula) |
| Coste unitario | 60-120 € | 80-150 € | 200-500 € | 1500-5000 € | 500-1200 € por cámara (multi-plaza) |
| Consumo energético | 5-10 µA medio (>5 años con pila D) | 0,5-1 mA medio (1-2 años con batería) | 5-50 mA (necesita red eléctrica) | Decenas de W (red) | Red eléctrica obligatoria |
| Robustez frente a clima | Excelente (sellado IP68 bajo asfalto) | Media (lluvia distorsiona) | Excelente | Buena (suciedad cristal) | Media (lluvia, niebla, deslumbramiento) |
| Privacidad | Muy alta (sin imagen, sin matrícula) | Muy alta | Alta | Alta (no identifica personas) | **Baja** (procesa matrículas) |
| Despliegue | Bajo asfalto (corte nocturno) | Soporte en farola/pared | Mástil/pared | Mástil elevado | Mástil/edificio + iluminación |
| Mantenimiento | Bajo (cambio batería >5 años) | Medio (limpieza, recalibración) | Bajo | Alto (mecánico) | Medio (limpieza óptica) |
| Adecuado para parking en cordón | **Sí** | Limitado (necesita techo) | Sí | Sí (multi-plaza) | Sí, agregado |
| Adecuado para escenario ciudad | Sí | Limitado | Sí (mayor coste) | No (coste/mantenimiento) | Solo en accesos |

## 3.3 Decisión razonada

Se opta por una **arquitectura híbrida** con dos categorías de sensores:

### 3.3.1 Sensor principal: magnético AMR bajo asfalto

- **Una unidad por plaza**, sellada IP68, anclada en el centro de la plaza bajo el pavimento (instalación nocturna en una sola operación).
- Calibración inicial in situ (toma del campo magnético terrestre de referencia sin coche).
- Detección de paso desde estado libre→ocupado y viceversa con umbral configurable; debounce típico 2-3 s para evitar falsos positivos por motos en plazas contiguas.
- Reporta el evento por LPWAN (capítulo 4) y mantiene un heartbeat configurable (5 min por defecto en producción; 30 s en demo).
- Vida útil 5-7 años con pila D (justifica el TCO frente al ultrasonido o al radar).
- Modelo de coste asumido: **75 € por unidad** (precio medio en compras municipales de 2024-2025).

Justificación frente a las alternativas:
- Frente a **ultrasonido**, gana en exterior por robustez climática y vida útil.
- Frente a **radar mmWave**, gana en consumo y coste; el radar es muy buena opción para zonas de alta facturación o donde haya alimentación eléctrica disponible (p. ej. plazas de carga eléctrica).
- Frente a **LIDAR**, el coste y el mantenimiento descartan su uso por plaza; LIDAR podría plantearse para cubrir varias plazas desde un solo poste en versiones futuras.
- Frente a **cámara**, ganan privacidad, coste y simplicidad operativa; las cámaras se reservan para los accesos.

### 3.3.2 Sensor complementario: cámaras ANPR en accesos a zonas

- **6-8 cámaras ANPR estratégicas** en los accesos a la BBOX (entradas/salidas de la N-430, C. San Juan, C. Imperial, Av. de la Mancha) para conteo agregado de flujo y, opcionalmente, control de acceso a futuras zonas de bajas emisiones.
- No se usan para detectar la ocupación de plazas individuales: se elimina así el principal riesgo RGPD.
- Se procesan en gateway edge con un modelo ligero (YOLOv8-tiny o similar), enviando solo metadatos (timestamp, dirección, recuento) a la cloud.
- Resultado: conteo agregado por puerta de acceso que el operador puede correlacionar con la ocupación detectada por los sensores.

### 3.3.3 Sensores ambientales puntuales

- 1 nodo ambiental cada ~150 plazas (NO₂, PM2.5, CO₂, ruido, temperatura, humedad) para correlacionar ocupación con calidad del aire y aportar valor añadido al expediente municipal de movilidad.
- Estos nodos no influyen en la decisión "libre/ocupada"; aportan analítica complementaria.

## 3.4 Modelo del nodo IoT (sensor magnético)

Cada sensor se modela como un **objeto IoT (Thing)** en AWS IoT Core con los siguientes atributos persistentes:

```json
{
  "spotId": "ALB-Z1-001",
  "zoneId": "Z1-CAMPUS",
  "street": "C. Imperial",
  "lat": 38.97765,
  "lon": -1.85745
}
```

El payload de cada evento publicado por el sensor (topic `parking/{zoneId}/spot/{spotId}/status`):

```json
{
  "spotId": "ALB-Z1-001",
  "zoneId": "Z1-CAMPUS",
  "street": "C. Imperial",
  "lat": 38.97765,
  "lon": -1.85745,
  "status": "occupied",
  "batteryLevel": 92.2,
  "confidence": 0.94,
  "sensorType": "magnetic",
  "timestamp": 1778929200072
}
```

## 3.5 Política de envío

| Evento | Condición | Frecuencia |
|--------|-----------|-----------|
| Cambio de estado | `status` actual ≠ `status` anterior, tras debounce | inmediato |
| Heartbeat | Sin cambio en `T` minutos | cada 5 min (configurable) |
| Auto-test diario | Una vez al día | 1/día |
| Alarma de manipulación | Acelerómetro detecta movimiento del sensor | inmediato |
| Aviso de batería baja | `batteryLevel < 20 %` | una vez al día hasta sustitución |

Este patrón minimiza el tráfico LPWAN (factor dominante del coste OPEX) sin perder observabilidad.

## 3.6 Calibración, instalación y mantenimiento

- **Calibración inicial** en taller (linealización del magnetómetro) y final in situ (medida del campo terrestre sin vehículo). Tiempo medio por unidad: 5-10 min.
- **Instalación** nocturna por cuadrillas de 2 operarios; rendimiento típico 30-40 plazas por noche con maquinaria menor.
- **Mantenimiento**: revisión por muestreo cada 6 meses; sustitución de pila prevista a los 5 años; firmware actualizable OTA vía LPWAN o mediante visita técnica si la pila lo permite.

## 3.7 Tabla resumen de la elección

| Parámetro | Valor adoptado | Comentario |
|-----------|----------------|------------|
| Tecnología principal | Magnético AMR bajo asfalto | Mejor coste/consumo/privacidad |
| Tecnología complementaria | Cámaras ANPR puntuales (accesos) | Solo conteo agregado, sin matrículas en cloud |
| Tecnología auxiliar | Nodos ambientales 1/150 plazas | Valor añadido (no crítico) |
| Densidad | 1 sensor / plaza | Modelo más fiable |
| Cadencia | 1 evento/cambio + heartbeat 5 min | Mínimo tráfico, máxima observabilidad |
| Vida útil sensor | 5-7 años | Habitual del segmento |
| Coste medio sensor | 75 € | Precio de mercado actual |
