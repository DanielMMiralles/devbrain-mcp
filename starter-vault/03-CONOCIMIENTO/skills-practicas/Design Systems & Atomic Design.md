---
tags: [skill, frontend, ui-ux, design-system]
nombre: Design Systems & Atomic Design
categoria: diseno-ui
---

# 🎨 Design Systems & Atomic Design

## Fundamentos
Metodología para construir interfaces de usuario modulares y escalables, integrando [[Figma]], [[Tailwind CSS]] y [[shadcn-ui]].

## Jerarquía de Componentes
1. **Átomos**: Tokens de diseño (colores, espaciados, tipografías, botones e inputs base).
2. **Moléculas**: Combinaciones de átomos (ej. un campo de búsqueda con botón e icono).
3. **Organismos**: Secciones complejas de UI (ej. Navbar, Card de producto, Formulario de checkout).
4. **Plantillas (Templates)**: Estructuras de layout sin contenido real.
5. **Páginas**: Instancias reales con datos hidratados.

## Buenas Prácticas con [[Tailwind CSS]]
- Centralizar variables en `@theme` o tokens HSL.
- Utilizar componentes de accesibilidad no estilizados (`Radix UI`) envueltos con Tailwind.
