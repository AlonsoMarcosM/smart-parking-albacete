# Guía docente - Internet de las Cosas y sus Aplicaciones

## Contexto para agente IA

Este documento resume la guía docente de la asignatura en formato operativo para agentes. Su objetivo es proporcionar restricciones académicas, resultados de aprendizaje, criterios de evaluación y contexto curricular útil para orientar el proyecto final.

## Datos generales

- Asignatura: Internet de las Cosas y sus Aplicaciones.
- Código: 311482.
- Titulación: Máster Universitario en Big Data y Computación en la Nube.
- Universidad: Universidad de Castilla-La Mancha.
- Curso académico: 2025-26.
- Curso: 1.º.
- Créditos ECTS: 6.
- Tipología: obligatoria.
- Lengua principal: español.
- Centros: Escuela Superior de Ingeniería Informática / Escuela Superior de Informática.

## Profesorado

- Félix Jesús Villanueva Molina.
  - Departamento: Tecnologías y Sistemas de Información.
  - Correo: Felix.Villanueva@uclm.es.
- María Blanca Caminero Herráez.
  - Departamento: Sistemas Informáticos.
  - Correo: MariaBlanca.Caminero@uclm.es.
  - Web: http://blog.uclm.es/mariablancacaminero
- Francisco Manuel Delicado Martínez.
  - Departamento: Sistemas Informáticos.
  - Correo: Francisco.Delicado@uclm.es.

## Requisitos previos

El estudiante debería estar familiarizado con:

- Redes de computadores.
- Sistemas distribuidos.

El agente debe asumir que el proyecto puede apoyarse en conceptos de:

- Comunicación entre dispositivos.
- Arquitecturas distribuidas.
- Procesamiento de datos.
- Despliegue de servicios.
- APIs.
- Seguridad básica.

## Justificación de la asignatura

IoT permite captar, recolectar y almacenar datos del mundo físico a coste viable. Esta capacidad es clave para aplicaciones de inteligencia artificial, automatización, analítica avanzada y transformación digital.

La asignatura se centra en arquitecturas, tecnologías y estándares IoT, desde la interacción con sensores hasta comunicaciones, diseño de aplicaciones y procesamiento de flujos de datos.

Ámbitos de aplicación:

- Ciudades inteligentes.
- Industria 4.0.
- Salud conectada.
- Agricultura.
- Transporte.
- Sistemas de datos sensoriales.

## Resultados de aprendizaje relevantes

### CN02

Conocer arquitecturas para tratamiento masivo de datos y técnicas de almacenamiento, orquestación de procesos y pipelines necesarias para construir soluciones avanzadas.

### HA03

Orquestar procesos ETL para adquirir y procesar datos masivos estructurados, semiestructurados y no estructurados desde distintas fuentes, incluidos Data Lakes, y diseñar una arquitectura de almacenamiento eficiente y escalable.

### CP02

Desarrollar estrategias para integrar, gestionar y analizar datos masivos generados por dispositivos IoT, usando edge computing y procesamiento de streams.

## Temario oficial

- Tema 1: Fundamentos de IoT.
- Tema 2: Interacción con el mundo físico.
- Tema 3: Recolección, comunicación y procesamiento de flujos de datos.
- Tema 4: Arquitectura de aplicaciones IoT.
- Tema 5: Aplicaciones.

Nota: el temario puede adaptarse a la evolución tecnológica.

## Metodología

La asignatura combina:

- Enseñanza virtual asíncrona.
- Enseñanza virtual síncrona.
- Prácticas de laboratorio virtual.
- Aprendizaje basado en proyectos y problemas.
- Aprendizaje colaborativo.
- Foros virtuales.
- Gamificación.
- Estudio autónomo.
- Elaboración de memorias e informes.
- Presentación y defensa de trabajos.
- Tutorías.
- Pruebas de evaluación.

## Implicaciones para el proyecto

El proyecto final debe demostrar:

- Aplicación práctica de conceptos IoT.
- Diseño de arquitectura completa.
- Integración de sensores, conectividad, edge, cloud y aplicaciones.
- Procesamiento de datos en tiempo real o near-real-time.
- Documentación técnica.
- Capacidad de defensa oral.
- Justificación de decisiones.

## Evaluación continua

La evaluación se distribuye así:

| Sistema | Peso | Descripción |
|---|---:|---|
| EX | 25 % | Examen final de preguntas cortas sobre conceptos de la asignatura. |
| ENTR1 / TR1 | 25 % | Informe técnico del problema, código desarrollado y resultados. |
| ENTR2 / TR2 | 20 % | Presentación y defensa de proyectos. |
| PR1 | 20 % | Prácticas, talleres o seminarios evaluados con entrevistas. |
| PR2 | 5 % | Entrevistas de seguimiento de trabajos y autoría. |
| APR | 5 % | Participación y cuestionarios semanales. |

Fórmula:

```text
Nota Final = EX*0,25 + TR1*0,25 + TR2*0,2 + PR1*0,2 + APR*0,05 + PR2*0,05
```

Condiciones:

- `EX >= 4`.
- `TR1 >= 4`.
- `TR2 >= 4`.
- Para superar la asignatura, la nota final debe ser igual o superior a 5.
- Si no se cumplen mínimos, la nota final será inferior a 4 aunque la media ponderada sea superior.

## Evaluación no continua

Los criterios son los mismos que en evaluación continua. El estudiante debe entregar las actividades pendientes antes de la fecha del examen ordinario, junto con la defensa y pruebas teóricas.

## Bibliografía y fuentes relevantes

- AWS IoT Core Documentation. https://docs.aws.amazon.com/iot/
- FIWARE Tutorials - Getting Started. https://github.com/FIWARE/tutorials.Getting-Started
- Apache Flink Hands-On Training. https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/learn-flink/overview/
- Giacomo Veneri y Antonio Capasso. "Hands-On Industrial Internet of Things". Packt Publishing, 2024.
- Arshdeep Bahga y Vijay Madisetti. "Internet of Things: A Hands-On Approach", 2014.

## Criterios para orientar al agente

Cuando un agente genere documentación o código para esta asignatura debe priorizar:

- Arquitecturas técnicamente justificadas.
- Integración explícita entre capas.
- Uso de tecnologías vistas en la asignatura.
- Escalabilidad.
- Edge computing.
- Procesamiento de streams.
- Claridad en supuestos.
- Costes aproximados.
- Resultados demostrables en prototipo.
- Preparación para defensa oral.

## Checklist académico para el proyecto

- [ ] El documento técnico explica el problema y sus supuestos.
- [ ] La arquitectura cubre sensorización, red, edge, cloud, datos, API y dashboard.
- [ ] Las decisiones técnicas están justificadas.
- [ ] Hay relación clara con IoT, streams y edge computing.
- [ ] El prototipo demuestra un flujo completo.
- [ ] La solución discute escalabilidad y seguridad.
- [ ] Hay análisis de costes.
- [ ] La memoria prepara la defensa de autoría y decisiones.
- [ ] El trabajo evita generalidades no fundamentadas.

## Preguntas de control para un agente

Antes de cerrar una propuesta, verificar:

- ¿Qué resultado de aprendizaje cubre cada parte del proyecto?
- ¿Dónde se ve el procesamiento de streams?
- ¿Dónde se ve edge computing?
- ¿Qué componentes se implementan realmente?
- ¿Qué componentes se diseñan pero no se implementan?
- ¿Qué evidencias aporta el prototipo?
- ¿Cómo se defendería la autoría y comprensión técnica en entrevista?
