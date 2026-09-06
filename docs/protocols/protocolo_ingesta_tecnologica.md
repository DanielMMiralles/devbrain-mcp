# 📥 Protocolo de Ingesta y Asimilación Tecnológica (DevBrain Ingestion Protocol - DIP)

Este protocolo define el flujo estándar y riguroso cuando el usuario o el agente proponen una **nueva herramienta, repositorio de GitHub, biblioteca o enfoque arquitectónico** para alimentar DevBrain.

---

## 1. Pipeline de 4 Fases

```
[GitHub Repo / Enfoque]
          │
          ▼
   1. TRIAGE & SCAN (Inspección de README, stack, licencia, madurez)
          │
          ▼
   2. FILTRO RED TEAM & PONYTAIL (¿Aporta valor real o es hype/deuda técnica?)
          ├── RECHAZADO ──> Registro breve en 00-INBOX/radar como "Observación"
          └── APROBADO  ──┐
                          ▼
   3. DESTILACIÓN ATÓMICA (Crear nota técnica curada en 03-CONOCIMIENTO o SKILL.md)
                          │
                          ▼
   4. ACTIVACIÓN PRAGMÁTICA (¿Aplica hoy a Chambita, Narval, AliaLog? -> OpenSpec / ADR)
```

---

## Fase 1: Triage e Inspección Rápida
Cuando el usuario diga: *"Mira esta herramienta/repo: [URL o nombre]"*, el agente recopila:
1. **Propósito Central**: ¿Qué problema resuelve en una sola frase?
2. **Naturaleza del Artefacto**:
   - 📦 **Librería / Tooling de Código**: Se integra al stack de desarrollo.
   - 🧠 **Capacidad de Agente (Skill / MCP)**: Extiende a DevBrain o Antigravity.
   - 📐 **Patrón Arquitectónico**: Enfoque de diseño conceptual (ej: Local-First, CRDT).
3. **Métricas de Salud**: Actividad en GitHub, licencias (MIT/Apache preferidas), peso de dependencias.

---

## Fase 2: Filtro Implacable Red Team & Ponytail
Antes de asimilar nada en el Vault, la herramienta pasa por las 4 preguntas de corte:
1. **La Prueba del Reemplazo**: ¿Esto reemplaza algo existente con una mejora de al menos 5x, o es solo una alternativa con sintaxis diferente?
2. **El Costo del Mantenimiento**: ¿Requiere demonios extra, servicios en segundo plano o configuración frágil?
3. **La Escalera Ponytail**: ¿Podemos hacer lo mismo con la biblioteca estándar o una función de 20 líneas sin meter este paquete?
4. **Veredicto**:
   - **DESCARTAR**: Demasiado inflado o inmaduro.
   - **MONITOREAR**: Interesante pero no listo para producción. Se guarda en Inbox.
   - **ASIMILAR**: Resuelve un dolor real con arquitectura sobria.

---

## Fase 3: Destilación en el Grafo de Conocimiento
Si el veredicto es **ASIMILAR**, se genera el contenido con estructura formal de DevBrain:

### Si es Conocimiento / Arquitectura:
Se crea una nota en `03-CONOCIMIENTO/[categoría]/[Nombre].md`:
- **Descripción Especializada**: Mecánica de ejecución.
- **Producción Gotchas & Anti-Patterns**: Cuándo falla y qué evitar.
- **Canonical Blueprint**: Snippet mínimo y funcional de integración.
- **Wikilinks cruzados**: Enlaces a notas relacionadas en el Vault.

### Si es una Habilidad Operativa del Agente:
Se crea un skill formal en `06-SISTEMA/agentes/skills/[nombre-skill]/SKILL.md`:
- Metadatos YAML (`name`, `description`).
- Runbook de ejecución paso a paso para el agente.

---

## Fase 4: Activación Pragmática (Impacto Real)
Una herramienta asimilada no debe quedarse como "conocimiento muerto":
1. **¿Aplica a un proyecto insignia hoy?**:
   - Si resuelve una necesidad de *Chambita-Ecosystem*, *Narval-SGN*, *AliaLog-System*, etc., se lanza una especificación OpenSpec (`propose_spec`) o se registra una decisión arquitectónica (`remember_decision`).
2. **Si no aplica hoy**: Queda indexada en el grafo lista para cuando `search_knowledge` la convoque en futuros diseños.
