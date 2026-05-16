# 10. Análisis de costes

Este capítulo presenta una estimación realista del coste del proyecto en dos escenarios (piloto y ciudad) descompuesto en **CAPEX** (inversión inicial en hardware y obra civil) y **OPEX** (operación recurrente, principalmente cloud y conectividad). Los precios son aproximados y se sitúan en el orden de magnitud habitual del sector en España a fecha 2026; en una propuesta real se cerrarían con los proveedores específicos.

## 10.1 Hipótesis y unidades

| Concepto | Valor adoptado |
|----------|-----------------|
| Tipo de cambio EUR/USD | 1 EUR = 1,08 USD |
| Vida útil del sensor | 6 años |
| Tasa de descuento (NPV simple) | 5 % |
| Horas-hombre instalación | 0,3 h/sensor (cuadrilla de 2 personas, ~35 sensores/noche) |
| Coste hora-cuadrilla | 60 €/h |
| Coste medio SIM NB-IoT M2M (>10 000 unidades) | 0,60 €/mes |
| Coste medio gateway edge | 700 € unidad + 100 € instalación |
| Coste cámara ANPR con compute edge | 900 € |

## 10.2 CAPEX – piloto (500 plazas)

| Concepto | Unidades | Coste unitario (€) | Total (€) |
|----------|----------|---------------------|-----------|
| Sensores magnéticos AMR | 500 | 75 | 37 500 |
| Instalación sensores (incluye corte de tráfico, asfaltado) | 500 | 40 | 20 000 |
| Gateways edge (3 zonas + redundancia) | 4 | 800 | 3 200 |
| Cámaras ANPR puntuales | 8 | 900 | 7 200 |
| Mástiles / soportes municipales | 8 | 250 | 2 000 |
| Nodos ambientales (1 cada ~150 plazas) | 4 | 350 | 1 400 |
| Sistema central de respaldo | 1 | 1 500 | 1 500 |
| Subtotal hardware | | | 72 800 |
| Ingeniería, integración, gestión proyecto (20 %) | | | 14 560 |
| **CAPEX piloto** | | | **87 360 €** |

## 10.3 OPEX mensual – piloto

| Concepto | Cantidad | Unitario | Mensual (€) |
|----------|----------|----------|--------------|
| SIM NB-IoT por sensor | 500 | 0,60 €/mes | 300 |
| Backhaul gateway/cámara (fibra municipal) | 4 + 8 | incluido en convenio | 0 |
| AWS IoT Core mensajes (publicación y reglas) | 4,5 M msg/mes | 1 USD / 1 M | 4,2 € |
| AWS Lambda (≈ 5 M invocaciones, 256 MB, 200 ms) | 5 M inv | ~0,30 USD/M req + ~0,20 USD GB-s | 0,7 € |
| Amazon DynamoDB (on-demand, ~5 M write + 1 M read) | | 1,25 USD/M WRU + 0,25 USD/M RRU | 7,5 € |
| Amazon API Gateway (REST) | 1 M req/mes | 3,5 USD/M req | 3,3 € |
| Amazon S3 (raw events, 3 GB/mes acumulando) | 3 GB | 0,023 USD/GB | 0,07 € |
| Amazon CloudWatch (logs ~5 GB/mes) | 5 GB | 0,50 USD/GB | 2,3 € |
| Operación y mantenimiento (10 h/mes × 35 €/h) | 10 h | 35 €/h | 350 |
| **OPEX piloto mensual** | | | **≈ 670 €** |

Coste cloud puro (sin OPEX humano ni conectividad): **≈ 18 €/mes**, ampliamente por debajo de RNF-17.

## 10.4 CAPEX – ciudad (10 000 plazas)

| Concepto | Unidades | Coste unitario (€) | Total (€) |
|----------|----------|---------------------|-----------|
| Sensores magnéticos AMR | 10 000 | 75 (con descuento por volumen) | 750 000 |
| Instalación sensores | 10 000 | 35 | 350 000 |
| Gateways edge (40 zonas con redundancia) | 80 | 800 | 64 000 |
| Cámaras ANPR (puntos clave + zonas reguladas) | 50 | 900 | 45 000 |
| Nodos ambientales | 70 | 350 | 24 500 |
| Centro de operaciones (servidor de respaldo, monitor) | 1 | 8 000 | 8 000 |
| Subtotal hardware | | | 1 241 500 |
| Ingeniería + gestión + formación (15 %) | | | 186 225 |
| **CAPEX ciudad** | | | **≈ 1 427 725 €** |

## 10.5 OPEX mensual – ciudad

| Concepto | Cantidad | Unitario | Mensual (€) |
|----------|----------|----------|--------------|
| SIM NB-IoT | 10 000 | 0,55 €/mes (volumen) | 5 500 |
| Mantenimiento físico (cuadrillas, repuestos) | — | — | 6 000 |
| Conectividad gateways (fibra municipal) | — | — | 0 |
| AWS IoT Core mensajes | 90 M msg/mes | 1 USD/M | 83 € |
| AWS Kinesis Data Streams (3 shards, 200 PUT/s pico) | — | ~75 USD/mes | 70 € |
| Managed Apache Flink (1 KPU) | — | ~110 USD/mes | 102 € |
| Lambda + DynamoDB + API + S3 + CloudWatch | — | — | ≈ 250 € |
| Amazon Timestream (KPIs históricos) | — | — | ≈ 90 € |
| WAF + CloudFront | — | — | ≈ 30 € |
| Personal operaciones (1 FTE) | — | — | 3 500 |
| **OPEX ciudad mensual** | | | **≈ 15 625 €** |

Coste AWS puro (sin RR. HH. ni SIMs ni operación física): **≈ 625 €/mes para 10 000 plazas**, es decir, **~6 céntimos por plaza y mes** en infraestructura cloud.

## 10.6 Coste de propiedad total (TCO) a 5 años

| Escenario | CAPEX (€) | OPEX 5 años (€) | TCO total (€) | TCO por plaza-año |
|-----------|-----------|-----------------|----------------|--------------------|
| Piloto (500 plazas) | 87 360 | 670 × 60 = 40 200 | 127 560 | **51 €/plaza/año** |
| Ciudad (10 000 plazas) | 1 427 725 | 15 625 × 60 = 937 500 | 2 365 225 | **47 €/plaza/año** |

Comparativa cualitativa:

- Una plaza regulada en zona azul típica española factura por encima de 1 €/día (~365 €/año).
- Solo con incrementar la rotación en un 5 % o capturar un 2 % adicional en sanciones evitadas, la solución se autofinancia.

## 10.7 Notas adicionales

- Las tarifas de AWS usadas son las publicadas en `aws.amazon.com/pricing` para `us-east-1`. En `eu-west-1` (región natural para Albacete) los precios son ~10 % superiores; los importes se mantienen en el mismo orden de magnitud.
- No se incluye el coste de licencias FIWARE (open source) ni de cualquier despliegue propio adicional.
- La estimación NO incluye IVA.
- La estimación de coste de operación humana (≈ 1 FTE en ciudad) puede absorberse por la propia plantilla del ayuntamiento si la operación se hace en el centro municipal de gestión de movilidad.

## 10.8 Conclusiones del análisis de coste

1. La fracción cloud del coste es **marginal frente al hardware y la operación física**.
2. El coste cloud se mantiene aproximadamente lineal con el número de plazas; el verdadero coste crece con la flota física.
3. NB-IoT como red elegida es decisiva en el OPEX: cualquier alternativa con cuota mensual >2 €/SIM duplicaría el coste operativo.
4. La arquitectura serverless evita inversión en infraestructura cloud propia (sin EC2/RDS) y permite un piloto que cabe en el presupuesto típico de un proyecto de innovación de un ayuntamiento mediano.
