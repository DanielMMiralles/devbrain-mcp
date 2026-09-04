---
tags: [skill, devops, cicd, github-actions, security]
nombre: CI/CD Pipelines Hardening
categoria: devops-infra
---

# 🔒 CI/CD Pipelines Hardening con GitHub Actions

## Buenas Prácticas de Seguridad en Pipelines
1. **Principio de Menor Privilegio**:
   - Asignar permisos explícitos y restrictivos a nivel de job (`permissions: contents: read`).
2. **Autenticación OIDC (OpenID Connect)**:
   - Eliminar credenciales estáticas de larga duración para nubes (AWS/GCP/Azure); autenticar runners vía tokens efímeros OIDC.
3. **Fijar Acciones a SHA Commit**:
   - `uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11` en lugar de `@v4` para prevenir ataques a la cadena de suministro.
4. **Secretos Segregados por Entornos**:
   - Utilizar GitHub Environments con reglas de aprobación manual obligatoria antes de desplegar en Producción.
