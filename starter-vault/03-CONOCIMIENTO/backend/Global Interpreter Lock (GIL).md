---
tags: [backend, python, internals]
---
# Global Interpreter Lock (GIL)
Mutex en CPython que impide que múltiples hilos nativos ejecuten código de bytes de Python simultáneamente. Superado mediante procesos separados, workers de Gunicorn o concurrencia asíncrona con [[Python Asyncio & Event Loop]].
