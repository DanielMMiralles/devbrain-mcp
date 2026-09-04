---
tags: [cloud, storage, s3, gcs, cost-optimization]
categoria: devops-infra
---
# Cloud Storage Tiering & Lifecycle Management

## Clases de Almacenamiento
- **Hot / Standard**: Acceso frecuente de baja latencia (archivos activos en [[AliaLog-System]]).
- **Cool / Infrequent Access (IA)**: Acceso mensual, menor costo de almacenamiento pero cargo por recuperación.
- **Archive / Glacier**: Respaldo a largo plazo (archivos históricos y logs de auditoría en [[Narval-SGN]]).
- **Deep Archive**: Retención por compliance (3 a 7 años), costo por GB ultra-bajo con tiempos de recuperación de 12 horas.

## Políticas de Ciclo de Vida Automáticas
- Transicionar archivos de documentos en [[Mayan-EDMS]] a Glacier tras 90 días de inactividad para reducir la factura de almacenamiento en un 80%.
