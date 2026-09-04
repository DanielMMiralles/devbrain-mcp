---
tags: [frontend, react, internals]
---
# [[React]] Fiber Architecture
Motor de reconciliación interno de [[React]] introducido en v16. Permite dividir el trabajo de renderizado en unidades incrementales (fibras) y pausar/priorizar tareas para mantener 60 FPS en la interfaz. Se conecta con [[Concurrent Mode]] y [[Virtual DOM]].
