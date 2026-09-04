---
tags: [cloud, arquitectura, disaster-recovery, sdr, high-availability]
categoria: devops-infra
---
# Disaster Recovery Strategies in the Cloud

## Estrategias de Recuperación ante Desastres (RTO vs RPO)
- **RTO (Recovery Time Objective)**: Tiempo máximo tolerable de inactividad del sistema.
- **RPO (Recovery Point Objective)**: Cantidad máxima tolerable de pérdida de datos medida en tiempo.

## Modelos Arquitectónicos
1. **Backup & Restore**: Económico, RTO/RPO de horas. Copias de seguridad en S3/GCS restauradas bajo demanda.
2. **Pilot Light**: Componentes centrales (base de datos con replicación continua a otra región) encendidos; la flota de cómputo se escala rápidamente en caso de fallo.
3. **Warm Standby**: Versión reducida del sistema corriendo continuamente en una segunda región o nube alternativa.
4. **Multi-Region Active-Active**: Tráfico distribuido globalmente mediante DNS Anycast o Cloudflare. RTO/RPO cercano a cero; máxima resiliencia.
