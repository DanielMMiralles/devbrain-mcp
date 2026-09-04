---
tags: [devops, security, compliance, slsa]
categoria: devops-infra
---
# SLSA Framework (Supply-chain Levels for Software Artifacts)

## ¿Qué es?
Marco de seguridad respaldado por Google y OpenSSF que define directrices e incrementos de madurez (Niveles 1 al 4) para proteger el software contra ataques a la cadena de suministro (como inyecciones de código malicioso en dependencias o runners comprometidos).

## Requisitos Nivel 3+
- Construcciones herméticas y aisladas en runners efímeros.
- Procedencia verificable generada criptográficamente durante el build en [[CI-CD Pipelines]].
