---
name: threejs-r3f-webgl
description: >-
  Ingenieria 3D interactiva, WebGL y Shaders GLSL para la web usando Three.js, @react-three/fiber (R3F)
  y @react-three/drei. Cubre escenas 3D declarativas en React/Next.js, materiales fisicos y vidrio refractivo
  (MeshTransmissionMaterial), camaras acopladas al scroll, iluminacion de estudio (Environment, Lightformer),
  InstancedMesh de alto rendimiento, Shaders GLSL reactivos al cursor y presupuesto estricto de GPU a 60fps.
  Usar cuando el usuario pida Three.js, 3D, WebGL, shaders, fondos liquidos o experiencias inmersivas.
---

# 🌐 Three.js, React Three Fiber (R3F) & WebGL Shaders — 60fps Engineering Skill

Esta skill guía la creación de experiencias 3D, objetos interactivos y Shaders GLSL en el navegador sin destruir el rendimiento, sin fugas de memoria VRAM y con integración perfecta con el DOM (HTML/CSS/GSAP/Motion).

---

## 🧭 1. Árbol de Decisión: ¿Cuándo usar R3F vs. Three.js Vanilla vs. Shader 2D?

1. **Proyecto en React / Next.js con objetos 3D, luces y cámara:**
   - Usa **`@react-three/fiber` (R3F) + `@react-three/drei`**. R3F gestiona automáticamente la limpieza (`dispose()`) de geometrías y materiales al desmontar componentes.
2. **Proyecto HTML/JS Vanilla o Astro sin React:**
   - Usa **`three` (Vanilla Three.js)** mediante ES Modules (`import * as THREE from 'three'`), asegurando un `ResizeObserver` limpio y un método `dispose()` explícito.
3. **Fondo atmosférico líquido, aurora sutil, grano dinámico o distorsión al cursor (sin modelos 3D):**
   - **NO cargues modelos `.glb` pesados.** Usa un único plano `PlaneGeometry(2, 2)` en ortográfica con un **Fragment Shader GLSL personalizado** (ruido Simplex / FBM reactivo a `uMouse` y `uTime`). Pesa menos de 5 KB y corre a 120fps.

---

## ⚡ 2. Presupuesto Estricto de GPU y Rendimiento (Obligatorio)

Cuando los LLMs escriben Three.js sin restricciones, suelen bloquear el hilo principal o agotar la batería. **Cumple siempre estas 6 reglas:**

1. **Límite de Pixel Ratio (`dpr`):**
   - En `<Canvas dpr={[1, 1.5]}>` o `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))`. Nunca renderices a `dpr=3` en pantallas Retina/4K porque multiplica los píxeles por 9x sin ganancia visual perceptible.
2. **Prohibido usar `setState` dentro de `useFrame`:**
   - `useFrame((state, delta) => { ... })` se ejecuta 60-120 veces por segundo. Mutar siempre directamente las referencias (`meshRef.current.rotation.y += delta * 0.4`) usando `MathUtils.lerp` para suavizado.
3. **Geometrías Masivas = `InstancedMesh` o `Points`:**
   - Si necesitas más de 50 objetos repetidos (partículas, nodos de red, grilla 3D), **prohibido mapear `<mesh>` individuales**. Usa `<Instances>` de `@react-three/drei` o `<instancedMesh>` (1 solo *draw call* en GPU).
4. **Pausa Automática fuera del Viewport (`frameloop`):**
   - Si el `<Canvas>` solo vive en el Hero, detén el renderizado cuando el usuario baje por la página usando `IntersectionObserver` o `frameloop={isVisible ? "always" : "never"}`.
5. **No bloquear el Scroll ni los clics del DOM:**
   - El contenedor del `<Canvas>` de fondo debe tener `pointer-events-none`, y en R3F usa `eventSource={containerRef}` para capturar las coordenadas del mouse desde el contenedor padre sin secuestrar el scroll ni los botones HTML.
6. **Carga Diferida (Lazy & Suspense) + Accesibilidad:**
   - En Next.js, importa siempre la escena 3D con `dynamic(() => import("./Scene3D"), { ssr: false })` envuelta en `<Suspense fallback={<HeroFallback />}>`. Si `prefers-reduced-motion: reduce` está activo, reduce la velocidad `uTime` a `0` o `0.05`.

---

## 💎 3. Patrones Canónicos en React Three Fiber (`@react-three/fiber` + `drei`)

### A. Objeto Central de Vidrio / Cristal Refractivo (Estilo Apple / Linear / Monolith)
El look 3D más limpio y editorial se logra con **`MeshTransmissionMaterial`** e iluminación de estudio con **`Environment`** y **`Lightformer`**:

```tsx
"use client";
import { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, Float, Lightformer, MeshTransmissionMaterial } from "@react-three/drei";
import * as THREE from "three";

function GlassSculpture() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state, delta) => {
    if (!meshRef.current) return;
    // Rotación continua suave + respuesta magnética sutil al puntero
    meshRef.current.rotation.x = THREE.MathUtils.lerp(
      meshRef.current.rotation.x,
      state.pointer.y * 0.35 + state.clock.elapsedTime * 0.15,
      delta * 3
    );
    meshRef.current.rotation.y = THREE.MathUtils.lerp(
      meshRef.current.rotation.y,
      state.pointer.x * 0.45 + state.clock.elapsedTime * 0.2,
      delta * 3
    );
  });

  return (
    <Float speed={1.6} rotationIntensity={0.4} floatIntensity={0.6}>
      <mesh ref={meshRef} scale={1.35}>
        <torusKnotGeometry args={[1, 0.32, 180, 32]} />
        <MeshTransmissionMaterial
          backside
          samples={6}
          resolution={512}
          transmission={0.98}
          roughness={0.08}
          thickness={1.4}
          ior={1.45}
          chromaticAberration={0.04}
          anisotropy={0.2}
          color="#e2e8f0"
        />
      </mesh>
    </Float>
  );
}

export default function HeroScene3D() {
  return (
    <div className="relative h-[560px] w-full overflow-hidden">
      <Canvas
        dpr={[1, 1.5]}
        camera={{ position: [0, 0, 5.2], fov: 38 }}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      >
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 5, 5]} intensity={1.2} />
        <GlassSculpture />
        {/* Estudio de iluminación sintético sin cargar archivos HDR externos pesados */}
        <Environment resolution={256}>
          <group rotation={[-Math.PI / 3, 0, 1]}>
            <Lightformer form="circle" intensity={4} rotation-x={Math.PI / 2} position={[0, 5, -9]} scale={2} />
            <Lightformer form="ring" color="#38bdf8" intensity={2.5} onUpdate={(self) => self.lookAt(0, 0, 0)} position={[10, 2, 0]} scale={4} />
            <Lightformer form="rect" color="#f8fafc" intensity={2} position={[-5, -2, -1]} scale={[10, 2, 1]} />
          </group>
        </Environment>
      </Canvas>
    </div>
  );
}
```

### B. Shader GLSL Interactivo Ligero (Superficie Líquida / Aurora Editorial Reactiva al Mouse)
Ideal cuando quieres una atmósfera viva a pantalla completa sin el peso de geometrías 3D complejas:

```tsx
"use client";
import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

const vertexShader = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = vec4(position, 1.0);
  }
`;

const fragmentShader = /* glsl */ `
  uniform float uTime;
  uniform vec2 uMouse;
  uniform vec3 uColorA;
  uniform vec3 uColorB;
  uniform vec3 uColorAccent;
  varying vec2 vUv;

  // Ruido trigonométrico rápido y suave (0 texturas externas)
  float waveNoise(vec2 p, float t) {
    return sin(p.x * 3.2 + t * 0.4) * cos(p.y * 2.8 - t * 0.3)
         + 0.5 * sin((p.x + p.y) * 5.0 + t * 0.6);
  }

  void main() {
    vec2 uv = vUv;
    float distToMouse = length(uv - uMouse);
    float mouseInfluence = smoothstep(0.55, 0.0, distToMouse) * 0.25;

    float n = waveNoise(uv * 1.6 + mouseInfluence, uTime);
    float mask = smoothstep(-1.2, 1.2, n);

    vec3 base = mix(uColorA, uColorB, uv.y * 0.8 + mask * 0.35);
    vec3 finalColor = mix(base, uColorAccent, mouseInfluence * 1.4 + smoothstep(0.65, 1.1, n) * 0.22);

    gl_FragColor = vec4(finalColor, 1.0);
  }
`;

function ShaderPlane() {
  const matRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uMouse: { value: new THREE.Vector2(0.5, 0.5) },
      uColorA: { value: new THREE.Color("#090a0f") },
      uColorB: { value: new THREE.Color("#121624") },
      uColorAccent: { value: new THREE.Color("#38bdf8") },
    }),
    []
  );

  useFrame((state, delta) => {
    if (!matRef.current) return;
    matRef.current.uniforms.uTime.value += delta;
    // Interpolación suave hacia el puntero normalizado (0 a 1)
    const targetX = (state.pointer.x + 1) * 0.5;
    const targetY = (state.pointer.y + 1) * 0.5;
    matRef.current.uniforms.uMouse.value.lerp(new THREE.Vector2(targetX, targetY), delta * 4);
  });

  return (
    <mesh>
      <planeGeometry args={[2, 2]} />
      <shaderMaterial
        ref={matRef}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        depthWrite={false}
      />
    </mesh>
  );
}
```

---

## 🔗 4. Coreografía DOM + Escena 3D (Sincronización con Scroll)

Cuando quieras que el objeto 3D rote, se desplace o cambie de cámara mientras el usuario hace scroll por las secciones HTML de la página:
1. **Con GSAP ScrollTrigger:** Guarda una referencia mutable al estado de la escena (`const sceneProgress = useRef({ progress: 0 })`), anima `sceneProgress.current.progress` con `gsap.to(sceneProgress.current, { progress: 1, scrollTrigger: { scrub: 1 } })` y lee `sceneProgress.current.progress` dentro de `useFrame` para interpolar posición/rotación de la cámara o malla.
2. **Contraste Tipográfico garantizado:** Nunca coloques texto de lectura pequeño directamente sobre un objeto 3D de alto contraste sin un gradiente de protección (`bg-gradient-to-t` / `backdrop-blur`) o posicionando el modelo 3D en el tercio derecho del grid asimétrico mientras la tipografía editorial respira en los dos tercios izquierdos.
