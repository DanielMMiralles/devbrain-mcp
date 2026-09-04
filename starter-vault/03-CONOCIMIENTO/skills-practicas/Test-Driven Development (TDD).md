---
tags: [skill, tdd, testing, software-engineering]
nombre: Test-Driven Development (TDD)
categoria: practicas-desarrollo
---

# 🔴🟢🔵 Test-Driven Development (TDD)

## Ciclo Red-Green-Refactor
1. **🔴 Red (Rojo)**: Escribir una prueba unitaria automatizada que falle antes de escribir cualquier línea de código de producción.
2. **🟢 Green (Verde)**: Escribir la cantidad mínima de código necesaria para que la prueba pase exitosamente.
3. **🔵 Refactor (Refactorizar)**: Limpiar y optimizar el código eliminando duplicaciones y mejorando diseño, asegurando que todos los tests sigan en verde.

## Estilos de TDD
- **Inside-Out (Escuela de Detroit / Clásica)**: Comienza probando el dominio puro y objetos de valor, subiendo gradualmente hacia los controladores. Prioriza pruebas de estado.
- **Outside-In (Escuela de Londres / Mockist)**: Comienza desde el endpoint o interfaz externa guiado por contratos y especificaciones ([[Spec-Driven Development (SDD)]]), utilizando dobles de prueba (mocks/stubs) para diseñar las interacciones entre colaboradores.

## Beneficios con Agentes de IA
- El agente opera con un objetivo determinista: escribir código hasta que el test pase.
- Previene regresiones y evita que el LLM agregue código superfluo o no solicitado.
