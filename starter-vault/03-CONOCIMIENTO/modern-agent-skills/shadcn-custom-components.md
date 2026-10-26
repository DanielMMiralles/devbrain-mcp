---
name: shadcn-custom-components
description: >-
  Arquitectura de componentes personalizados de autor sobre Radix UI, shadcn/ui, CVA y Tailwind CSS.
  Elimina el aspecto generico/clonico de shadcn vanilla aplicando superficies Double-Bezel, tokens OKLCH,
  primitivas animadas con Framer Motion (Dialog, Tabs, Command/cmdk, Drawer/vaul, Sonner) y patrones
  interactivos estilo Aceternity UI, Magic UI, Cult UI y Raycast. Usar al construir sistemas de componentes,
  dashboards, SaaS, formularios interactivos o bibliotecas UI en React/Next.js.
---

# 🧩 Custom Component Architecture — Beyond Vanilla `shadcn/ui`

El error más común al usar `shadcn/ui` con IA es dejar los estilos por defecto (`rounded-md border bg-background`), lo que produce interfaces genéricas que parecen clones de plantilla. Esta skill mantiene **el 100% de la accesibilidad y composición de Radix UI + `cva` + `cn()`**, pero transforma la capa visual y cinética en un sistema de diseño de autor (nivel Linear, Raycast, Vercel, Cult UI).

---

## 🚫 1. Reglas Anti-Clon (Prohibido el "Vanilla shadcn Look")

1. **Prohibido usar tarjetas planas `border bg-card shadow-sm` sin tratamiento de superficie:**
   - Aplica **Superficies Multicapa (Double-Bezel)** o **Iluminación Interna (`shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)]`)**.
   - En modo oscuro, los bordes nunca deben ser grises sólidos opacos (`border-gray-700`); usa bordes translúcidos de refracción (`border-white/[0.07]`) que cambian a `border-white/[0.16]` en `:hover`.
2. **Prohibido usar `<Tabs>`, `<Dialog>` o `<DropdownMenu>` con cortes bruscos o fades genéricos:**
   - Los indicadores activos de `Tabs` y `NavigationMenu` deben deslizarse con `layoutId` de Framer Motion.
   - Los modales (`Dialog`) y menús desplegables deben escalar con física de resorte (`scale: 0.96 -> 1`, `y: 8 -> 0`).
3. **Tokens de Color en OKLCH con matiz intencional:**
   - Nunca uses neutros puros muertos (`#000000` / `#1a1a1a` sin tinte). Tiñe la escala de grises sutilmente hacia el color de marca o hacia piedra cálida/pizarra fría en `globals.css`.

---

## 🏗️ 2. Anatomía Estándar de un Componente de Autor (`cn` + `cva` + `motion`)

Todo componente reutilizable en `components/ui/` debe seguir este contrato limpio:

```tsx
"use client";
import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  // Base: tactilidad física (:active translate-y), focus ring limpio y transición con curva de resorte
  "group relative inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium transition-all duration-200 ease-[cubic-bezier(0.32,0.72,0,1)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-45 active:scale-[0.98] active:translate-y-[1px]",
  {
    variants: {
      variant: {
        // Primary con luz especular superior (inner highlight) y sombra profunda
        primary:
          "bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-950 shadow-[0_1px_2px_rgba(0,0,0,0.25),inset_0_1px_0_rgba(255,255,255,0.2)] hover:opacity-95",
        // Glass / Surface con borde refractivo
        surface:
          "border border-zinc-950/10 dark:border-white/10 bg-white/80 dark:bg-white/[0.04] backdrop-blur-md text-zinc-900 dark:text-zinc-100 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)] hover:bg-zinc-950/[0.04] dark:hover:bg-white/[0.08] hover:border-zinc-950/20 dark:hover:border-white/20",
        // Ghost minimalista
        ghost:
          "text-zinc-600 dark:text-zinc-400 hover:text-zinc-950 dark:hover:text-zinc-100 hover:bg-zinc-950/[0.04] dark:hover:bg-white/[0.05]",
      },
      size: {
        sm: "h-8 rounded-lg px-3 text-xs",
        md: "h-10 rounded-xl px-4 py-2",
        lg: "h-12 rounded-2xl px-6 text-base",
        pill: "h-10 rounded-full pl-5 pr-2", // Ideal para botón con ícono anidado (Button-in-Button)
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
```

---

## ✨ 3. Los 5 Componentes Personalizados de Alto Impacto (Recetario Listo)

### A. Superficie "Double-Bezel" (Arquitectura de Contenedor Anidado)
En lugar de una `Card` plana de shadcn, usa un chasis exterior acolchado que alberga un núcleo interior con su propio borde luminoso:

```tsx
export function DoubleBezelCard({
  children,
  header,
  className,
}: {
  children: React.ReactNode;
  header?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-[24px] border border-zinc-950/[0.06] dark:border-white/[0.06] bg-zinc-950/[0.02] dark:bg-white/[0.02] p-1.5 backdrop-blur-sm",
        className
      )}
    >
      {header && <div className="px-4 py-2 text-xs font-mono uppercase tracking-wider text-zinc-500">{header}</div>}
      <div className="rounded-[18px] border border-zinc-950/[0.06] dark:border-white/[0.08] bg-white dark:bg-zinc-950/90 p-6 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.08),inset_0_1px_0_rgba(255,255,255,0.08)]">
        {children}
      </div>
    </div>
  );
}
```

### B. Radix Tabs con Indicador Magnético (`layoutId`)
Nunca uses el cambio de fondo instantáneo de `<TabsTrigger>` por defecto. Inyecta una píldora animada con `layoutId`:

```tsx
"use client";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { motion } from "motion/react";
import { useState } from "react";

export function KineticTabs({
  tabs,
}: {
  tabs: { id: string; label: string; content: React.ReactNode }[];
}) {
  const [active, setActive] = useState(tabs[0].id);

  return (
    <TabsPrimitive.Root value={active} onValueChange={setActive}>
      <TabsPrimitive.List className="inline-flex items-center gap-1 rounded-full border border-zinc-950/10 dark:border-white/10 bg-zinc-950/[0.03] dark:bg-white/[0.03] p-1">
        {tabs.map((tab) => {
          const isSelected = active === tab.id;
          return (
            <TabsPrimitive.Trigger
              key={tab.id}
              value={tab.id}
              className="relative rounded-full px-4 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none"
            >
              {isSelected && (
                <motion.span
                  layoutId="kinetic-tab-pill"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  className="absolute inset-0 rounded-full bg-white dark:bg-zinc-800 shadow-sm border border-zinc-950/5 dark:border-white/10"
                />
              )}
              <span className="relative z-10">{tab.label}</span>
            </TabsPrimitive.Trigger>
          );
        })}
      </TabsPrimitive.List>

      {tabs.map((tab) => (
        <TabsPrimitive.Content key={tab.id} value={tab.id} className="mt-6 focus:outline-none">
          <motion.div
            initial={{ opacity: 0, y: 8, filter: "blur(4px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
          >
            {tab.content}
          </motion.div>
        </TabsPrimitive.Content>
      ))}
    </TabsPrimitive.Root>
  );
}
```

### C. Contador Numérico Físico (`NumberTicker`)
Para métricas, precios interactivos o dashboards en vivo (nunca muestres números estáticos cuando cambian por un filtro o slider):

```tsx
"use client";
import { useEffect, useRef } from "react";
import { useInView, useMotionValue, useSpring } from "motion/react";

export function NumberTicker({
  value,
  prefix = "",
  suffix = "",
  decimals = 0,
}: {
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, { damping: 36, stiffness: 180 });
  const isInView = useInView(ref, { once: true, margin: "-40px" });

  useEffect(() => {
    if (isInView) motionValue.set(value);
  }, [motionValue, isInView, value]);

  useEffect(() => {
    return springValue.on("change", (latest) => {
      if (ref.current) {
        ref.current.textContent = `${prefix}${Intl.NumberFormat("en-US", {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        }).format(Number(latest.toFixed(decimals)))}${suffix}`;
      }
    });
  }, [springValue, decimals, prefix, suffix]);

  return <span ref={ref} className="tabular-nums tracking-tight" />;
}
```

### D. Command Menu (`cmdk`) & Drawers Físicos (`vaul`)
- En cualquier dashboard o herramienta de productividad, añade un **Command Palette (`⌘K`)** basado en `cmdk` con vista previa contextual y atajos de teclado visibles (`<kbd className="rounded border px-1.5 py-0.5 font-mono text-[10px]">⌘K</kbd>`).
- En móvil, reemplaza los `<Dialog>` tradicionales por **Drawers con física de arrastre (`vaul`)** que escalan el `<body>` trasero (`shouldScaleBackground`).

### E. Bento Grid con Micro-Apps Interactivas (Prohibido el Bento decorativo)
Cada celda de un Bento Grid debe contener un **micro-componente vivo** (no texto estático con un ícono):
1. **Celda de Telemetría / Logs:** Lista con `AnimatePresence mode="popLayout"` que rota eventos cada 3.5s o al hacer clic en "Simular evento".
2. **Celda de Configuración:** Toggles de Radix `<Switch>` que modifican visualmente la vista previa dentro de la misma tarjeta en tiempo real.
3. **Celda de Arquitectura:** Nodos conectados por un `AnimatedSvgBeam` que iluminan la ruta activa al hacer hover sobre cada nodo.

---

## 🛠️ 4. Checklist Antes de Entregar Cualquier UI con `shadcn`
- [ ] ¿Los números usan `tabular-nums` (`font-variant-numeric: tabular-nums`) para no bailar al animarse?
- [ ] ¿Las tarjetas tienen bordes sutiles de refracción (`border-white/[0.08]` o `DoubleBezelCard`) en vez del borde gris duro por defecto?
- [ ] ¿Los controles (`Tabs`, `Switch`, `Accordion`, `Dialog`) tienen interpolación fluida de física o curva `cubic-bezier(0.32, 0.72, 0, 1)`?
- [ ] ¿Existe al menos un componente interactivo con estado real (calculadora de precios, filtro reactivo, command bar o simulador de flujo)?
