---
tags: [ai, agents, gentle-pi, gentleman-programming, pi, sdd, tdd, codegraph]
categoria: automation-agents
version_actual: "v2.5.0"
ultima_actualizacion: 2026-09-08
---

# 🎩 Gentle-Pi (Senior-Architect Development Harness para Pi)

## ¿Qué es Gentle-Pi?
**Gentle-Pi** (`Gentleman-Programming/gentle-pi`) es un arnés a medida diseñado para transformar al agente de código **Pi** en un desarrollador y arquitecto de software senior (*"El Gentleman"*). Incorpora flujos rigurosos de **Desarrollo Guiado por Especificaciones (SDD / OpenSpec)**, evidencia estricta de **TDD**, guardarraíles de revisión por pares y descubrimiento de habilidades del ecosistema.

Está estrechamente acoplado con [[Gentle-AI & Sub-Agent Orchestration (Token Saving)]] y transporta el binario **Gentle-AI v2.7.0** y el paquete de contratos **Provider Contract Bundle 1.2.0**.

---

## ⚡ Capacidades y Novedades en la Versión v2.5.0 ("The Visual & Subagent Upgrade")

### 1. Gentle Shell: Nueva Capa Visual Unificada
- **Statusline Compacta**: Una única línea superior/inferior inteligente reemplaza el antiguo pie de página de tres líneas de Pi: visualiza proyecto, rama git, modelo actual, nivel de *effort*, indicador de costo/suscripción (`sub`), estado del servidor MCP y nombre de la sesión.
- **Context Gauge**: Indicador gráfico de consumo de contexto con alerta en color ámbar al alcanzar el 80% y rojo crítico al 95%.
- **Prompt Frame & Petal Spinner**: Marco redondeado con un pétalo animado giratorio mientras el agente procesa comandos y alerta ámbar cuando hay mensajes en cola.
- **Diff Overlay en Vivo (`/gentle:changes` / `alt+g`)**: Inspección visual de modificaciones en el *working-tree* con capacidad de saltar directamente al `$EDITOR` y regresar al buffer.

### 2. Gentle Agents: Sub-Agentes Nativos en Pi
- **Sub-Agentes Integrados sin Paquetes Externos**: Reemplaza dependencias de terceros (como `pi-subagents-j0k3r`). Cada sub-agente corre como un proceso hijo aislado de Pi.
- **Streaming Cards**: Visualización en tiempo real sobre el editor con la tarea, modelo, tokens utilizados, costo y tiempo transcurrido.
- **Persistencia Completa en Disco**: Historiales, sesiones hijas y transcripciones completas en Markdown persistidas por tarea.
- **Panel de Control `/gentle:agents` (`alt+a`)**: Vista dividida con lista de subtareas a la izquierda e hilo completo de ejecución con herramientas y bloques de pensamiento a la derecha. Permite pausar o cancelar sub-agentes individualmente o en lote.

### 3. Gentle Todo Nativo
- Gestor de tareas embebido que sustituye `rpiv-todo`. Sigue la misma estética visual de tarjetas, plegando listas extensas y depurando listas completadas al recargar la sesión.

### 4. Delegación Sensible a Evidencias (RDD-Aware Delegation)
- Si el desarrollo guiado por evidencias (*receipt-driven development*) está activo y la revisión nativa concluye, el sub-agente autor ejecuta la verificación y la revisión actúa como auditor independiente, **ahorrando el costo de un segundo verificador en cada cambio**.
- Si el interruptor está inactivo o se omite la revisión, el comando `gentle-review` invoca la evaluación de riesgo de Gentle-AI v2.7.0: solo los cambios catalogados como `medium` o `high` riesgo disparan un verificador separado.

### 5. Consentimiento de Revisión por Sesión
- Autorización a nivel de sesión (`/gentle:review`): concede permiso una única vez para toda la sesión de trabajo en lugar de solicitar confirmación interactiva en cada candidato generado.

### 6. Optimizaciones en Entornos Windows
- Aceptación de modos ejecutables de candidatos en Windows.
- Shim de **CodeGraph** resuelto y lanzado de manera nativa sin envoltorio de shell, normalizando variables `PATH` entrecomilladas y preservando las rutas del árbol de trabajo.

---

## 🛠️ Instalación y Actualización

```bash
# Actualización / Instalación a través del gestor de paquetes de Pi
pi install npm:gentle-pi@2.5.0

# O actualizar la versión instalada
pi update

# Sincronizar arnés y configuración de agentes
gentle-ai sync
```

> [!IMPORTANT]
> **Nota de Migración v2.5.0**: Si tenías instalados previamente `npm:pi-subagents-j0k3r` o `npm:rpiv-todo`, desinstálalos de tu entorno Pi (`pi remove ...`), ya que Gentle-Pi ahora incorpora **Gentle Agents** y **Gentle Todo** de forma nativa.

---

## 🔗 Conexiones en el Grafo DevBrain
- Capa de orquestación padre: [[Gentle-AI & Sub-Agent Orchestration (Token Saving)]]
- Memoria persistente: [[Engram (Gentleman Programming Persistent Memory)]]
- Análisis AST de código: [[devbrain_graphify]] / `query_code_graph`
- Metodología SDD: [[Spec-Driven Development (SDD)]]
