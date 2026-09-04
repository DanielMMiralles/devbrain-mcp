---
tags: [skill, devops, docker, security, containers]
nombre: Docker Security & Multi-Stage Hardening
categoria: devops-infra
---

# 🛡️ [[Docker]] Security & Multi-Stage Hardening

## ¿Por qué Multi-Stage Builds?
Permite compilar el código en una etapa pesada (con compilers, SDKs de TypeScript o Python, cabeceras C) y copiar **únicamente los binarios o artefactos finales** a una imagen limpia y mínima de ejecución (Distroless o Alpine).

## Checklist de Seguridad para Producción
1. **Ejecutar como Usuario No-Root**:
   - `USER appuser` (nunca correr contenedores como `root`).
2. **Imágenes Base Mínimas**:
   - Usar `python:3.12-slim`, `node:20-alpine` o imágenes Google Distroless.
3. **Escaneo de Vulnerabilidades**:
   - Integrar herramientas como Trivy o [[Docker]] Scout en los pipelines de [[CI-CD Pipelines]].
4. **Eliminar el Gestor de Paquetes en Runtime**:
   - En la imagen final no deben residir herramientas innecesarias como `curl`, `wget`, `gcc` o `apk`.
