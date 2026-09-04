---
tags: [skill, devops, arquitectura, best-practices]
nombre: The Twelve-Factor App
categoria: arquitectura
---

# ☁️ The Twelve-Factor App para Sistemas Modernos

## Principios Clave
1. **Base de Código Única**: Un repositorio versionado con [[Git & GitHub]], múltiples despliegues.
2. **Dependencias Explícitas**: Declaradas estrictamente en manifiestos (`package.json`, `pyproject.toml`).
3. **Configuración en el Entorno**: Secretos y credenciales inyectados vía variables de entorno, nunca en código.
4. **Servicios de Respaldo como Recursos**: [[PostgreSQL]], [[Redis]] y servicios externos se tratan como URLs adjuntas.
5. **Procesos Sin Estado (Stateless)**: La persistencia reside en la base de datos, no en memoria del proceso.
6. **Contenedorización**: Cada servicio empaquetado en [[Docker]] listo para orquestación en [[Kubernetes]].
