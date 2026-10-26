---
name: framer-motion
description: >-
  Ingenieria avanzada de animacion con Motion v12 (Framer Motion) y SVG Cinetico para React 19 y Next.js.
  Cubre MotionValues sin re-render (useMotionValue, useMotionTemplate, useSpring), scroll-linked physics
  (useScroll, useTransform), layout morphing (layoutId), AnimatePresence, diagramas SVG animados (pathLength,
  beams) y el protocolo de coexistencia hibrida con GSAP ScrollTrigger. Usar siempre que se animen componentes,
  bento grids interactivos, cursores magneticos, transiciones de estado o diagramas vectoriales.
---

# 🎭 Framer Motion (Motion v12) & Kinetic SVG — Ultra Engineering Skill

Esta skill equipa al agente con patrones de ingeniería de animación a **60fps reales**, física reactiva sin re-renderizados de React, diagramas SVG cinéticos estilo Linear/Stripe y reglas estrictas de coexistencia con **GSAP ScrollTrigger** (`gpt-taste` / `design-taste-frontend`).

---

## 🤝 1. Protocolo de Coexistencia Híbrida: GSAP vs. Motion

Cuando un proyecto combina **GSAP** y **Framer Motion (`motion/react`)**, NUNCA deben competir por la propiedad `transform` o `opacity` del mismo nodo DOM:

| Caso de Uso | Motor Obligatorio | Por qué |
| :--- | :--- | :--- |
| **Scroll Pinning de página completa, Scrubbing de secciones, Horizontal Pan** | **GSAP (`@gsap/react` + `ScrollTrigger`)** | GSAP calcula alturas de pin-spacer y scrub timelines con precisión sub-píxel sin depender del ciclo de vida de React. |
| **Micro-interacciones de UI, Tabs, Modales, Drawers, Listas dinámicas, Hover/Tap** | **Motion (`motion/react`)** | Integración nativa con el árbol de React (`AnimatePresence`, `layoutId`, variantes declarativas). |
| **Cursores magnéticos, Spotlight Cards, Tilt 3D al mover el mouse** | **Motion (`useMotionValue` + `useSpring` + `useMotionTemplate`)** | Actualiza el DOM directamente fuera del ciclo de render de React (0 re-renders por frame). |

> **Regla de Oro de Aislamiento DOM:** Si una sección padre está controlada por un `ScrollTrigger` de GSAP (por ejemplo, una tarjeta en un *Sticky-Stack*), aplica GSAP al `<section>` o contenedor externo, y aplica `motion.div` únicamente a los **elementos hijos internos** (botones, badges, tabs, diagramas).

---

## ⚡ 2. Reglas de Oro de Rendimiento (Garantía 60fps & Zero Re-renders)

1. **Prohibido usar `useState` para coordenadas de mouse o scroll:**
   - Hacer `onMouseMove={(e) => setPos({ x: e.clientX, y: e.clientY })}` dispara 60-120 re-renders por segundo en React y destruye el rendimiento.
   - **Solución obligatoria:** Usar `useMotionValue` + `useSpring` + `useMotionTemplate`.
2. **Solo propiedades aceleradas por GPU:**
   - Animar exclusivamente `x`, `y`, `scale`, `scaleX`, `scaleY`, `rotate`, `rotateX`, `rotateY`, `opacity` y `filter` (con moderación).
   - Para cambios de tamaño/posición estructural, usar siempre `layout` o `layoutId` (que aplica técnica FLIP mediante matrices `transform`).
3. **Configuraciones de Física Canónicas (Prohibido el easing lineal por defecto):**
   - **Micro-interacción rápida (Botones, Toggles, Hover):**
     ```ts
     const snappySpring = { type: "spring", stiffness: 450, damping: 28, mass: 0.6 } as const;
     ```
   - **Transición de Layout / Morphing (`layoutId`, Modales, Drawers):**
     ```ts
     const fluidSpring = { type: "spring", stiffness: 320, damping: 32, mass: 0.9 } as const;
     ```
   - **Entrada Editorial Elegante (Tween):**
     ```ts
     const editorialEase = { duration: 0.65, ease: [0.16, 1, 0.3, 1] } as const;
     ```

---

## 🧲 3. Patrones Avanzados Sin Re-render (MotionValues)

### A. Spotlight Card / Borde Reactivo al Cursor (0 Re-renders)
```tsx
"use client";
import { motion, useMotionTemplate, useMotionValue } from "motion/react";
import type { MouseEvent } from "react";

export function SpotlightCard({ children }: { children: React.ReactNode }) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove({ currentTarget, clientX, clientY }: MouseEvent<HTMLDivElement>) {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  return (
    <div
      onMouseMove={handleMouseMove}
      className="group relative overflow-hidden rounded-2xl border border-white/10 bg-zinc-950/90 p-8"
    >
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-2xl opacity-0 transition duration-300 group-hover:opacity-100"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              420px circle at ${mouseX}px ${mouseY}px,
              rgba(255, 255, 255, 0.10),
              transparent 80%
            )
          `,
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
```

### B. Botón Magnético con Física de Resorte (`useMotionValue` + `useSpring`)
```tsx
"use client";
import { motion, useMotionValue, useSpring } from "motion/react";
import { useRef } from "react";

export function MagneticButton({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLButtonElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const springX = useSpring(x, { stiffness: 250, damping: 18, mass: 0.5 });
  const springY = useSpring(y, { stiffness: 250, damping: 18, mass: 0.5 });

  function handleMouseMove(e: React.MouseEvent<HTMLButtonElement>) {
    const rect = ref.current?.getBoundingClientRect();
    if (!rect) return;
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    x.set((e.clientX - centerX) * 0.28);
    y.set((e.clientY - centerY) * 0.28);
  }

  function handleMouseLeave() {
    x.set(0);
    y.set(0);
  }

  return (
    <motion.button
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      whileTap={{ scale: 0.96 }}
      style={{ x: springX, y: springY }}
      className="relative inline-flex items-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-medium text-zinc-950"
    >
      {children}
    </motion.button>
  );
}
```

### C. Tilt 3D con Perspectiva Reactiva
```tsx
"use client";
import { motion, useMotionValue, useSpring, useTransform } from "motion/react";

export function Tilt3DCard({ children }: { children: React.ReactNode }) {
  const x = useMotionValue(0.5);
  const y = useMotionValue(0.5);

  const rotateX = useSpring(useTransform(y, [0, 1], [7, -7]), { stiffness: 300, damping: 30 });
  const rotateY = useSpring(useTransform(x, [0, 1], [-7, 7]), { stiffness: 300, damping: 30 });

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    x.set((e.clientX - rect.left) / rect.width);
    y.set((e.clientY - rect.top) / rect.height);
  }

  function handleMouseLeave() {
    x.set(0.5);
    y.set(0.5);
  }

  return (
    <motion.div
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
      className="relative rounded-2xl border border-white/10 bg-zinc-900/60 p-6"
    >
      <div style={{ transform: "translateZ(24px)" }}>{children}</div>
    </motion.div>
  );
}
```

---

## 🔄 4. Transiciones Compartidas (`layoutId`) & Ciclos de Vida (`AnimatePresence`)

### A. Morphing de Píldora Activa y Tarjetas Expandibles (`layoutId`)
- Usa siempre `layoutId` para indicadores de navegación activa, filtros de categorías y tarjetas que se expanden a vista de detalle.
- Cuando animes texto dentro de un contenedor con `layout`, añade `layout="position"` al texto para evitar que la tipografía se estire o deforme durante la interpolación.

### B. `AnimatePresence` con `mode="popLayout"`
- Para listas interactivas donde se agregan, filtran o eliminan elementos en vivo (regla *"One live thing"*), usa `<AnimatePresence mode="popLayout">` y coloca `layout` en cada `<motion.li>` para que los elementos restantes se deslicen suavemente hacia su nuevo lugar.

---

## 〰️ 5. SVG Cinético & Diagramas de Producto (Estilo Linear / Stripe / Vercel)

Para evitar usar imágenes estáticas en las tarjetas de características o Bento Grids, construye **diagramas SVG vivos** usando `motion.path` y gradientes animados:

### Haz de Luz / Telemetría Animada sobre un Path SVG (`AnimatedBeam`)
```tsx
"use client";
import { motion } from "motion/react";
import { useId } from "react";

export function AnimatedSvgBeam({ d = "M 10 60 Q 150 10 290 60" }: { d?: string }) {
  const gradId = useId();
  return (
    <svg viewBox="0 0 300 120" fill="none" className="w-full h-auto overflow-visible">
      {/* Trazado base estático */}
      <path d={d} stroke="currentColor" strokeOpacity="0.15" strokeWidth="1.5" />
      {/* Trazado cinético con pulso luminoso */}
      <path d={d} stroke={`url(#${gradId})`} strokeWidth="2" strokeLinecap="round" />
      <defs>
        <motion.linearGradient
          id={gradId}
          gradientUnits="userSpaceOnUse"
          initial={{ x1: "-20%", x2: "0%", y1: "0%", y2: "0%" }}
          animate={{ x1: "100%", x2: "120%", y1: "0%", y2: "0%" }}
          transition={{ duration: 2.4, repeat: Infinity, ease: "linear", repeatDelay: 0.6 }}
        >
          <stop stopColor="#38bdf8" stopOpacity="0" />
          <stop offset="0.5" stopColor="#38bdf8" stopOpacity="1" />
          <stop offset="1" stopColor="#818cf8" stopOpacity="0" />
        </motion.linearGradient>
      </defs>
    </svg>
  );
}
```

### Dibujo Progresivo de Iconos o Líneas (`pathLength`)
```tsx
<motion.path
  d="M5 13l4 4L19 7"
  initial={{ pathLength: 0, opacity: 0 }}
  whileInView={{ pathLength: 1, opacity: 1 }}
  viewport={{ once: true }}
  transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
/>
```

---

## ♿ 6. Accesibilidad (`useReducedMotion`) y Gotchas de Next.js / React 19

1. **Imports modernos:** En versiones actuales (`motion` v11/v12+), prefiere `import { motion, AnimatePresence } from "motion/react"` (o `"framer-motion"` si el `package.json` del proyecto ya lo declara así).
2. **`useReducedMotion()` obligatorio:** Si `useReducedMotion()` devuelve `true`, desactiva desplazamientos (`x`, `y`, `rotate`) y conserva únicamente transiciones suaves de `opacity`.
3. **Directiva `"use client"`:** Todo archivo que importe hooks o componentes `motion.*` en Next.js App Router debe iniciar con `"use client";`.
