---
tags: [devops, sre, reliability, monitoring]
categoria: devops-infra
---
# SLI, SLO & Error Budget Engineering

## Definiciones Clave de SRE
- **SLI (Service Level Indicator)**: Métrica cuantitativa del servicio en tiempo real (ej. % de peticiones HTTP exitosas de [[FastAPI]] en <200ms).
- **SLO (Service Level Objective)**: Meta acordada de fiabilidad interna (ej. 99.9% de peticiones exitosas durante 30 días móviles).
- **Error Budget (Presupuesto de Error)**: El margen de fallo permitido `(100% - SLO) = 0.1%`.

## Políticas de Gobernanza
- Si el presupuesto de error se agota, los despliegues de nuevas características en [[CI-CD Pipelines]] se congelan y todo el esfuerzo de ingeniería se reorienta a estabilidad y tests.
