# ✂️ Reglas Ponytail: El Arquetipo del Senior Dev Perezoso

Inspirado en el framework abierto **Ponytail** (Dietrich Gebert / +120k stars). El mejor código es el que no se escribe. Cada línea de código es una deuda técnica y un vector potencial de bugs.

---

## 1. La Escalera de Decisiones Obligatoria
Antes de redactar una sola línea de código, proponer un nuevo paquete o crear una abstracción, el agente DEBE subir esta escalera:

1. **¿Tiene que existir? (YAGNI - You Ain't Gonna Need It)**:
   - Si no hay un requerimiento explícito e inmediato que lo justifique hoy, la respuesta es NO.
2. **¿Ya existe en el repositorio?**:
   - Reutilizar lo existente en lugar de duplicar o crear variantes "elegantes".
3. **¿La biblioteca estándar lo resuelve?**:
   - Python: `json`, `pathlib`, `sqlite3`, `dataclasses`, `urllib`, `re`, `subprocess`.
   - Node / TS: `fs/promises`, `crypto`, `fetch`, `URL`, `path`.
   - Prohibido instalar `lodash`, `moment`, `axios` o wrappers redundantes si la plataforma nativa lo resuelve.
4. **¿Existe una característica nativa de la plataforma?**:
   - Postgres ya tiene JSONB, full-text search y pub/sub básico (`LISTEN/NOTIFY`). No metas Elasticsearch o Redis hasta que Postgres realmente colapse.
5. **¿Existe ya una dependencia instalada que lo haga?**:
   - No instales una biblioteca nueva si una ya presente tiene la función.
6. **¿Puede ser una sola función o una sola línea?**:
   - Una función pura de 10 líneas es 10 veces mejor que una clase con 3 capas de inyección de dependencias, DTO, interface y factory.

---

## 2. Los Pecados Capitales del Over-Engineering
1. **Abstracción Prematura**: Crear interfaces genéricas para cosas que sólo tienen una implementación.
2. **Microserviciosis Temprana**: Separar en microservicios antes de tener usuarios reales y cuellos de botella medidos.
3. **Dependenciomanía**: `npm install` o `pip install` para utilidades de 5 líneas de código.
4. **Configuritis Extrema**: Sistemas hiperconfigurables que nadie necesita en lugar de convenciones sanas.
