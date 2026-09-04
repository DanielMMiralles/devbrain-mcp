---
tags: [devops, kubernetes, ebpf, networking, cilium]
categoria: devops-infra
---
# Cilium eBPF XDP Architecture

## ¿Qué es?
Arquitectura de red de alto rendimiento para [[Kubernetes]] que ejecuta programas [[eBPF (Extended Berkeley Packet Filter)]] directamente en el controlador de red del kernel mediante XDP (eXpress Data Path), procesando paquetes antes de que alcancen la pila de red del sistema operativo.

## Ventajas Clave
- **Reemplazo de Kube-Proxy**: Elimina las tablas masivas de `iptables` de Linux, reduciendo la latencia de routing O(N) a O(1) mediante tablas hash BPF.
- **Cifrado Transparente**: Soporte nativo para WireGuard e IPsec nodo a nodo sin modificar aplicaciones en [[FastAPI]] o [[NestJS]].
- **Visibilidad L7 con Hubble**: Inspección de flujos HTTP, gRPC y DNS sin necesidad de inyectar sidecars en los Pods.
