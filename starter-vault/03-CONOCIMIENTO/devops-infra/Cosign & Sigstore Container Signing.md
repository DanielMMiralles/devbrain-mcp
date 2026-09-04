---
tags: [devops, security, containers, supply-chain]
categoria: devops-infra
---
# Cosign & Sigstore Container Signing

## ¿Qué es?
Herramienta de la fundación Linux / OpenSSF para la firma criptográfica, verificación y almacenamiento de firmas y atestaciones directamente en registros OCI de contenedores ([[Docker]]).

## Flujo en Pipelines de [[CI-CD Pipelines]]
1. GitHub Actions compila la imagen Docker del microservicio.
2. `cosign sign` firma el digest SHA256 de la imagen utilizando OIDC keyless sin llaves privadas estáticas.
3. En [[Kubernetes]], un controlador de admisión (Kyverno / Gatekeeper) bloquea el despliegue de cualquier Pod cuya imagen no esté firmada criptográficamente.
