---
tags: [devops, linux, containers, kernel]
---
# Linux Namespaces & cgroups
Primitivas fundamentales del kernel de Linux que hacen posible la existencia de [[Docker]]:
- **Namespaces**: Proveen aislamiento de procesos (PID), red (NET), montajes (MNT) e identidades (USER).
- **Control Groups (cgroups)**: Limitan y monitorean el consumo de recursos de hardware (CPU, memoria, disco, ancho de banda).
