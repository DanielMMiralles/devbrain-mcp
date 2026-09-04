---
tags: [seguridad, criptografia, encryption, algorithms]
categoria: ciberseguridad
---
# Modern Cryptography Standards (AES-GCM, Ed25519, Argon2id)

## Criptografía Simétrica (Cifrado de Datos en Reposo)
- **AES-256-GCM**: Cifrado autenticado por bloques (AEAD) que garantiza confidencialidad e integridad simultáneamente.
- **ChaCha20-Poly1305**: Alternativa de alto rendimiento para CPUs sin aceleración de hardware AES.

## Criptografía Asimétrica (Firmas e Intercambio de Llaves)
- **Ed25519 / Curve25519**: Curvas elípticas modernas, ultrarrápidas y resistentes a ataques de canal lateral para firmas digitales y SSH.

## Hashing Seguro de Contraseñas
- **Argon2id**: Ganador de la Password Hashing Competition. Resistente a ataques por fuerza bruta basados en GPU y ASICs gracias a su costo de memoria configurable.
- **bcrypt**: Estándar consolidado para aplicaciones web tradicionales.
