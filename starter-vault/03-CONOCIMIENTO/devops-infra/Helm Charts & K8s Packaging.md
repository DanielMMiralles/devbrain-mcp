---
tags: [herramienta, devops, kubernetes, helm, cloud-native]
nombre: Helm Charts
categoria: devops-infra
---

# ⎈ Helm Charts & [[Kubernetes]] Packaging

## ¿Qué es?
Gestor de paquetes estándar de facto para [[Kubernetes]] que permite definir, versionar, instalar y actualizar aplicaciones complejas mediante plantillas de manifiestos reutilizables (`values.yaml`).

## Componentes de un Chart
- `Chart.yaml`: Metadatos del paquete (nombre, versión, dependencias).
- `values.yaml`: Configuración por defecto personalizable por entorno (dev, staging, prod).
- `templates/`: Plantillas YAML parametrizadas (Deployments, Services, ConfigMaps, Ingress).

## Buenas Prácticas
- Mantener los secretos fuera de `values.yaml` utilizando External Secrets Operator o Sealed Secrets.
- Validar charts en pipelines de [[CI-CD Pipelines]] mediante `helm lint` y `helm template`.
