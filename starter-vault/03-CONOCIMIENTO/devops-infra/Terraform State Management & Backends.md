---
tags: [herramienta, devops, iac, terraform, cloud]
nombre: Terraform State Management
categoria: devops-infra
---

# 🌍 [[Terraform]] State Management & Locking

## ¿Por qué es Crítico el State?
El archivo `terraform.tfstate` mapea los recursos declarados en el código con la infraestructura real aprovisionada en la nube (AWS, GCP, Azure, DigitalOcean).

## Remote Backends & State Locking
En entornos de equipo y pipelines de [[CI-CD Pipelines]], el state **NUNCA** debe guardarse en el repositorio Git local:
- **Almacenamiento Remoto**: S3 bucket, Google Cloud Storage o [[Terraform]] Cloud con cifrado en reposo.
- **State Locking**: Mecanismo (ej. tabla DynamoDB en AWS o bloqueos nativos de GCS) que impide que dos ingenieros o pipelines ejecuten `terraform apply` simultáneamente, evitando corrupción catastrófica de infraestructura.

## Reglas de Oro
- Nunca almacenar contraseñas ni secretos hardcodeados en variables de [[Terraform]]; inyectar desde Vault o Secret Managers.
