# 01. Descripción del problema

## 1.1 Contexto y motivación

El proyecto se inscribe en el marco de las iniciativas de **smart city** que numerosos ayuntamientos españoles están impulsando como respuesta al crecimiento del parque automovilístico, a los compromisos de descarbonización derivados del Pacto Verde Europeo y a la inminente llegada de la movilidad autónoma. La búsqueda manual de aparcamiento es una de las patologías típicas del tráfico urbano: estudios clásicos (Shoup, 2005) cifran entre el 15% y el 30% del tráfico de un centro urbano el porcentaje atribuible a vehículos que circulan buscando plaza. La consecuencia es triple: aumento del tiempo de viaje, incremento de las emisiones y degradación del confort ciudadano.

El Ayuntamiento de Albacete, ciudad de unos 175 000 habitantes con un Campus Universitario consolidado y un complejo sanitario-deportivo de alta afluencia, plantea como zona piloto el entorno comprendido entre el **Campus UCLM**, el **Estadio Municipal Carlos Belmonte**, el **Hospital Universitario** y la zona residencial al sur de la **AB-20**. El objetivo es disponer en tiempo real de la ocupación de plazas y exponer esa información tanto a sistemas externos (apps, paneles de mensajería variable, vehículos autónomos conectados vía C-V2X) como a la propia plataforma municipal de gestión de movilidad.

## 1.2 Cliente, actores y objetivos de negocio

| Actor | Rol |
|-------|-----|
| Ayuntamiento de Albacete | Cliente final; promotor de la licitación. |
| TECO S.L. | Adjudicatario (rol del autor); diseña, despliega y opera la solución. |
| Conductores y ciudadanos | Usuarios indirectos vía app/panel. |
| Vehículos autónomos conectados | Consumidores futuros de la API mediante C-V2X. |
| Concejalía de Movilidad | Cliente interno; explota KPIs para planificación. |
| Servicios de emergencia (Hospital) | Caso de uso prioritario: acceso rápido a plazas de servicio. |
| Operador externo de cámaras ANPR | Proporciona vídeo en los accesos. |

Objetivos de negocio:

1. Reducir tiempo medio de búsqueda de aparcamiento en la zona piloto.
2. Mejorar el acceso al Hospital y a la Facultad de Medicina en horario crítico.
3. Generar evidencia (KPIs) para planificar zonas reguladas (verde/azul) y políticas de movilidad.
4. Disponer de una plataforma con capacidad de escalado al resto de la ciudad sin rediseño.
5. Cumplir requisitos de interoperabilidad (NGSI-v2 / FIWARE) que el ecosistema de smart cities europeas demanda cada vez con más frecuencia en los pliegos.

## 1.3 Caracterización de la zona piloto

La zona piloto se ha delimitado mediante una **bounding box** real definida por el responsable del proyecto:

| Esquina | Latitud | Longitud |
|---------|---------|----------|
| Suroeste | 38.976059 | -1.858728 |
| Noreste | 38.983215 | -1.846111 |

Esta BBOX cubre una superficie aproximada de **0,55 km² (≈ 800 × 800 m)** y engloba los siguientes polos generadores de demanda de aparcamiento:

- **Z1-CAMPUS** (Universidad e investigación): Escuela Superior de Ingeniería Informática UCLM, Pabellón Universitario, edificios del campus a lo largo de Calle Imperial y Calle de la Navaja. Patrón de uso: pico fuerte de llegadas entre 7:30 y 10:00, segundo pico menor entre 16:00 y 18:00, vacío en fin de semana excepto eventos.
- **Z2-DEPORTIVO** (eventos y ocio): Estadio Municipal Carlos Belmonte (capacidad ~17 500), Campos de Fútbol "Alba Redondo" y "José Copete", restaurante Le Première. Patrón fuertemente correlacionado con el calendario deportivo; picos extremos en partidos (saturación), demanda baja entre semana.
- **Z3-SANITARIO** (Hospital y facultades): Hospital Universitario de Albacete, Facultad de Medicina, Facultad de Farmacia. Patrón continuo 24/7 con turnos del personal sanitario y rotación de visitas; demanda crítica en urgencias.
- **Z4-RESIDENCIAL** (zona sur de la AB-20): viviendas y servicios de la Avenida de la Mancha y Avenida Olimpia. Patrón residencial clásico: alta ocupación nocturna, liberación diurna parcial.

Los ejes viarios principales que concentran plazas de aparcamiento en línea (zona blanca y futura zona regulada) son: Calle Imperial, Calle de la Navaja, Calle Sancho Panza, Calle Duque de Rivas, Calle de la Historia, Avenida del Arte, Calle San Juan, Calle La Química, Avenida de la Mancha, Avenida Olimpia, Calle Maratón.

## 1.4 Supuestos realistas adoptados

Asunciones explícitas que el agente toma como base del diseño y del análisis (consistentes con el espíritu del enunciado: "Asuma y detalle, de forma realista, cuantos parámetros necesite"):

| Supuesto | Valor adoptado | Justificación |
|----------|----------------|---------------|
| Número de plazas piloto | ~500 | Coherente con el tamaño de la BBOX y el patrón de aparcamiento en cordón típico. |
| Distribución por sub-zona | 125 plazas medias por zona | Equilibrio entre simplicidad y representatividad. |
| Rotación media diaria | 4-8 ciclos/plaza Z3, 3-5 Z1, 1-3 Z4, picos extremos en Z2 | Datos de campo de otras ciudades españolas similares. |
| Cobertura NB-IoT | 100 % en la BBOX | Albacete dispone de cobertura LTE/NB-IoT completa de los operadores nacionales. |
| Disponibilidad mínima del sistema | 99,5 % | Razonable para piloto; objetivo 99,9 % en versión productiva. |
| Latencia end-to-end máxima | 5 segundos | Suficiente para la guía humana y compatible con consumo C-V2X periódico. |
| Tasa de envío por sensor | 1 evento/cambio + 1 heartbeat cada 5 min | Reduce tráfico sin perder observabilidad. |
| Tamaño medio de mensaje | 0,5-2 KB JSON | Holgado para datos de plaza; comprimible si fuera necesario. |
| Vida útil del sensor (batería) | 5-7 años | Específicación habitual de los sensores AMR comerciales. |

## 1.5 Restricciones y consideraciones específicas

- **Privacidad**: imposible (legalmente y socialmente) cubrir cada plaza con cámaras matriculeras. Las cámaras se restringen a accesos perimetrales y se justifican como detección agregada y para servicios complementarios (control de acceso a zonas restringidas).
- **Despliegue urbano**: la instalación de sensores en calzada requiere conformidad municipal, planificación nocturna y, en zona de uso peatonal, alternativas de instalación bajo asfalto.
- **Variabilidad meteorológica**: Albacete tiene veranos secos calurosos (hasta 40 °C) e inviernos fríos (heladas, nevadas puntuales). Los sensores deben certificarse IP67/IP68 y soportar el rango térmico.
- **Cohabitación con otros servicios IoT**: la red municipal puede dar cabida en paralelo a contenedores inteligentes, iluminación, calidad del aire, etc. La arquitectura debe asumir que las plazas son sólo un dominio más.
- **Continuidad operativa**: en una versión productiva la solución debe contemplar redundancia multi-AZ; el piloto se despliega en una sola región (us-east-1) por las limitaciones del AWS Academy Learner Lab.

## 1.6 Riesgos identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Falsos positivos del sensor magnético por motos cercanas | Media | Bajo | Algoritmo de debounce en edge y umbral de confianza. |
| Pérdida de cobertura NB-IoT puntual | Baja | Medio | Buffer local en el sensor y reintento exponencial. |
| Sensores robados/vandalizados | Baja | Bajo | Caja blindada; alarma de manipulación; bajo coste unitario. |
| Saturación de la API en eventos deportivos | Media | Medio | API Gateway con throttling configurable; caché ante terceros. |
| Fuga de datos personales | Muy baja | Alto | Política estricta: no se almacena matrícula ni dato personal. |
| Caducidad credenciales lab (3h) | Alta (académico) | Alto | Scripts idempotentes, teardown rápido, plan de relanzamiento. |
