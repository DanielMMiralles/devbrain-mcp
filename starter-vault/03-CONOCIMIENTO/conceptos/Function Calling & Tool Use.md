---
tags: [concepto, ai, llm, tools]
nombre: Function Calling & Tool Use
categoria: conceptos
---

# Function Calling & Tool Use

## Definición
Capacidad de los modelos de lenguaje modernos para detectar cuándo deben invocar una función externa y generar los argumentos estructurados (JSON Schema) correspondientes en lugar de generar texto plano.

## Flujo de Ejecución
1. El usuario envía una consulta al agente.
2. El LLM recibe la consulta junto con la definición de herramientas disponibles (Tools/JSON Schema).
3. El LLM retorna un payload de llamada a herramienta (`tool_call`: nombre y parámetros).
4. La aplicación ejecuta el código localmente (ej: consultar [[PostgreSQL]], llamar una API con [[FastAPI]]).
5. El resultado de la función se envía de vuelta al LLM para generar la respuesta final.
