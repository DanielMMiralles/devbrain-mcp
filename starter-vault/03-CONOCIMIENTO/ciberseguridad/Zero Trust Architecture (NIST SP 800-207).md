---
tags: [seguridad, zero-trust, nist, arquitectura]
categoria: ciberseguridad
---
# Zero Trust Architecture (NIST SP 800-207)

## Principios Fundamentales de Confianza Cero
1. **Asumir Brecha (Assume Breach)**: Operar asumiendo que el perímetro ya ha sido comprometido por atacantes.
2. **Verificación Explícita Continua**: Autenticar y autorizar dinámicamente cada intento de acceso basado en identidad, contexto, dispositivo y comportamiento.
3. **Principio de Menor Privilegio (PoLP)**: Conceder únicamente los accesos mínimos requeridos con límites de tiempo estrictos (Just-In-Time access).

## Implementación Técnica
- Eliminación de VPNs tradicionales en favor de túneles basados en identidad (**Cloudflare Zero Trust / WireGuard**).
- Microsegmentación de red en [[Kubernetes]] con [[Cilium eBPF XDP Architecture]].
