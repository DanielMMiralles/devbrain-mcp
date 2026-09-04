---
tags: [devops, security, compliance, sbom]
categoria: devops-infra
---
# SBOM Generation (Syft & Grype)

## ¿Qué es un SBOM?
*Software Bill of Materials*: Inventario formal y estandarizado (SPDX o CycloneDX) de todos los paquetes, librerías, dependencias transitivas y licencias que componen una imagen de contenedor o binario.

## Herramientas
- **Syft**: Escanea el sistema de archivos del contenedor y genera el manifiesto SBOM JSON.
- **Grype**: Compara el SBOM contra bases de datos de vulnerabilidades conocidas (CVE) para detectar fallos de seguridad antes del despliegue en producción.
