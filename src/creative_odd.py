"""
creative_odd.py: Núcleo D-ODD v2 (Dynamic Outcome-Driven Development).

Separación de responsabilidades:
  - El GATE (barato, determinista, calibrable) solo decide si vale la pena preguntarle al LLM.
  - El JUICIO lo hace el LLM entregando 5 dimensiones; aquí solo se mapean a Cynefin.
  - La DIVERGENCIA real ocurre en subagentes con contextos aislados (ver PROTOCOL_TEXT);
    este módulo NO fabrica tesis/antítesis/síntesis enlatadas, entrega un paquete de contexto.
  - Cuando el objetivo involucra UI/UX o un proyecto nuevo, sortea determinísticamente
    direcciones de arte no clonadas y aplica el Veto Anti-Clon contra la plantilla saturada.
  - La CALIBRACIÓN ajusta el umbral del gate con las etiquetas que deja assess_decision.

Solo stdlib: lo importan los hooks, que deben arrancar rápido.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from decision_ledger import devbrain_home, labeled_gate_events


class CynefinDomain(str, Enum):
    CLEAR = "clear"
    COMPLICATED = "complicated"
    COMPLEX = "complex"
    CHAOTIC = "chaotic"


VERDICT_BY_DOMAIN = {
    CynefinDomain.CLEAR.value: "fast_track",
    CynefinDomain.COMPLICATED.value: "analytical",
    CynefinDomain.COMPLEX.value: "d_odd",
    CynefinDomain.CHAOTIC.value: "stabilize_first",
}

DIMENSIONS = ("reversibility_cost", "blast_radius", "uncertainty", "vault_novelty", "viable_alternatives")

# ---------------------------------------------------------------------------
# Calibración (persistida en ~/.devbrain/d_odd_calibration.json)
# ---------------------------------------------------------------------------

DEFAULT_CALIBRATION: Dict[str, Any] = {
    "version": 1,
    "gate_threshold": 0.35,
    "complex_total": 8,
    "complicated_total": 4,
    # Pesos del gate por grupo de señales (los patrones viven en código, los pesos aquí)
    "weights": {
        "decision_verbs": 0.30,
        "comparatives": 0.25,
        "structural_nouns": 0.12,
        "stack_terms": 0.10,
        "weak_verbs": 0.12,
        "trivial_dampeners": -0.40,
        "read_only_dampeners": -0.35,
    },
    "caps": {"structural_nouns": 0.30, "stack_terms": 0.25},
    "min_labeled_for_calibration": 8,
    "step": 0.05,
    "threshold_bounds": [0.20, 0.80],
}


def calibration_path() -> Path:
    return devbrain_home() / "d_odd_calibration.json"


def load_calibration() -> Dict[str, Any]:
    cal = json.loads(json.dumps(DEFAULT_CALIBRATION))
    p = calibration_path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            for k, v in data.items():
                if isinstance(v, dict) and isinstance(cal.get(k), dict):
                    cal[k].update(v)
                else:
                    cal[k] = v
        except Exception:
            pass
    return cal


def save_calibration(cal: Dict[str, Any]) -> None:
    calibration_path().write_text(json.dumps(cal, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Gate barato (hook PreInvocation y fallback para clientes sin hooks)
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    t = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode("ascii")
    return " " + re.sub(r"\s+", " ", t) + " "


SIGNALS: Dict[str, List[str]] = {
    "decision_verbs": [
        r"\bdisen\w*", r"\barquitect\w*", r"\bmigr\w*", r"\belegir\b", r"\bescoger\b", r"\bdecid\w*",
        r"\bconviene\b", r"\bdeberiamos\b", r"\breemplaz\w*", r"\badopt\w*", r"\bestrateg\w*",
        r"\breestructur\w*", r"\bredisen\w*", r"\bdesacopl\w*", r"\bdecoupl\w*", r"\bdesign\w*",
        r"\barchitect\w*", r"\bchoose\b", r"\bshould we\b", r"\breplace\b", r"\bplanteamiento\b",
        r"\benfoque\b", r"\biniciar proyecto\b", r"\bdesde cero\b", r"\bmejorar\b", r"\bpotenciar\b",
        r"\bevolucion\w*", r"\borganiz\w*",
    ],
    "comparatives": [
        r"\bvs\.?\b", r"\bversus\b", r"\bo bien\b", r"\ben lugar de\b", r"\bmejor (manera|forma|opcion)\b",
        r"\balternativ\w*", r"\bpros y contras\b", r"\btrade-?offs?\b", r"\bcompar\w*", r"\bque es mejor\b",
    ],
    "structural_nouns": [
        r"\bmodul\w*", r"\bservici\w*", r"\bbase de datos\b", r"\bcolas?\b", r"\bcache\b", r"\besquema\w*",
        r"\bpipeline\w*", r"\binfraestructura\b", r"\bautenticacion\b", r"\bestado global\b",
        r"\bsincroniza\w*", r"\bconcurren\w*", r"\bescalab\w*", r"\bframework\b", r"\bmotor\b",
        r"\bmicroservici\w*", r"\bmonolito\b", r"\bevent\w* bus\b", r"\bprotocolo\b",
        r"\bdashboard\w*", r"\bprototipo\w*", r"\binterfaz\b", r"\bidentidad visual\b",
        r"\bsistema de diseno\b", r"\bui/ux\b", r"\blanding\b", r"\bconsola\b",
        r"\bontolog\w*", r"\bjerarqui\w*", r"\bportada\b", r"\bautonomi\w*", r"\bestructura\b",
    ],
    "stack_terms": [
        r"\bkafka\b", r"\bpostgres\w*", r"\bredis\b", r"\bsqlite\b", r"\bmongo\w*", r"\bgraphql\b",
        r"\bkubernetes\b", r"\bk8s\b", r"\bsupabase\b", r"\bnestjs\b", r"\bfastapi\b", r"\bnext\.?js\b",
        r"\brabbitmq\b", r"\bwebsockets?\b", r"\bgrpc\b", r"\brest\b", r"\borm\b", r"\bsse\b", r"\bmcp\b",
    ],
    "weak_verbs": [r"\brefactor\w*", r"\bevalu\w*", r"\boptimiz\w*", r"\bintegr\w*", r"\bimplement\w*"],
    "trivial_dampeners": [
        r"\btypo\b", r"\berrata\b", r"\brenombr\w*", r"\bnombre de (una|la) variable\b", r"\bcolor\w*",
        r"\bpadding\b", r"\bmargin\b", r"\bboton\b", r"\bicono\b", r"\bformatea\w*", r"\blint\w*",
        r"\bcomentario\w*", r"\bimports?\b", r"\btexto del\b", r"\bsi (el|los) tests? pasa\w*\b",
    ],
    "read_only_dampeners": [
        r"\bexplica\w*", r"\bque es\b", r"\bdonde esta\b", r"\bcomo funciona\b", r"\bmuestra\w*",
        r"\bresume\w*", r"\blista\w*\b",
    ],
}

_COMPILED = {k: [re.compile(p) for p in v] for k, v in SIGNALS.items()}


def gate_score(text: str, cal: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Score 0..1 de 'probablemente es una decisión de diseño'. Barato: solo regex sobre el texto."""
    cal = cal or load_calibration()
    t = _norm(text or "")
    weights = cal["weights"]
    caps = cal.get("caps", {})
    hits: Dict[str, int] = {
        group: sum(1 for p in pats if p.search(t))
        for group, pats in _COMPILED.items()
    }
    hits = {k: v for k, v in hits.items() if v > 0}
    has_design_intent = bool(
        hits.get("decision_verbs") or hits.get("comparatives") or hits.get("structural_nouns", 0) >= 2
    )
    score = 0.0
    for group, n in hits.items():
        if group == "read_only_dampeners" and has_design_intent:
            continue  # Un pedido de análisis + rediseño arquitectónico no es read-only trivial
        w = float(weights.get(group, 0.0))
        if group in caps:
            contrib = min(w * n, float(caps[group]))
        elif w < 0:
            contrib = w  # un amortiguador basta
        else:
            contrib = w if n == 1 else w * 1.3  # rendimiento decreciente
        score += contrib
    score = max(0.0, min(1.0, score))
    threshold = float(cal["gate_threshold"])
    return {"score": round(score, 3), "threshold": threshold, "fired": score >= threshold, "hits": hits}


def input_hash(text: str) -> str:
    return hashlib.sha1((text or "").strip().encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Juicio: dimensiones del LLM -> dominio Cynefin
# ---------------------------------------------------------------------------

def assess(dimensions: Dict[str, Any], incident: bool = False, cal: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Mapea las 5 dimensiones (0..3) entregadas por el LLM a un dominio Cynefin y un veredicto."""
    cal = cal or load_calibration()
    dims = {d: max(0, min(3, int(dimensions.get(d, 0) or 0))) for d in DIMENSIONS}
    total = sum(dims.values())

    if incident:
        domain = CynefinDomain.CHAOTIC.value
        reason = "Incidente activo: estabilizar o revertir antes de explorar."
    elif total >= int(cal["complex_total"]) or (dims["uncertainty"] >= 2 and dims["viable_alternatives"] >= 2):
        domain = CynefinDomain.COMPLEX.value
        reason = "Alta incertidumbre con varias alternativas viables (o costo agregado alto): no converger en una sola receta."
    elif total >= int(cal["complicated_total"]):
        domain = CynefinDomain.COMPLICATED.value
        reason = "Problema analítico: hay una respuesta correcta, se encuentra con análisis (Graphify, FTS5, tests)."
    else:
        domain = CynefinDomain.CLEAR.value
        reason = "Causa-efecto obvia y reversible: ejecutar directo."

    top = max(dims, key=lambda k: dims[k])
    return {"dimensions": dims, "total": total, "domain": domain,
            "verdict": VERDICT_BY_DOMAIN[domain], "dominant_dimension": top, "reason": reason}


# ---------------------------------------------------------------------------
# Provocaciones: se eligen según la dimensión dominante, no al azar
# ---------------------------------------------------------------------------

PROVOCATIONS: Dict[str, Dict[str, str]] = {
    "ZERO_DEPENDENCY": {
        "title": "Cero dependencias",
        "question": "¿Cómo se resuelve solo con la stdlib y primitivas nativas del runtime?",
    },
    "DEEP_MODULE": {
        "title": "Módulo profundo",
        "question": "¿Cuál es la interfaz más pequeña posible que esconda toda la complejidad?",
    },
    "REVERSIBILITY": {
        "title": "Puerta de dos vías",
        "question": "¿Qué versión de esta decisión se puede revertir en menos de una hora si sale mal?",
    },
    "INVERSION": {
        "title": "Inversión contrafáctica",
        "question": "Si la premisa que da por hecha el Vault fuese falsa hoy, ¿qué harías distinto?",
    },
    "RADICAL_PRUNING": {
        "title": "Poda radical",
        "question": "¿Qué 20% del alcance entrega el 90% del valor? ¿Qué pasa si no se construye nada?",
    },
    "FAILURE_FIRST": {
        "title": "Pre-mortem",
        "question": "Es dentro de 6 meses y esta decisión fracasó. ¿Cuál fue la causa más probable?",
    },
}

PROVOCATIONS_BY_DIMENSION = {
    "reversibility_cost": ["REVERSIBILITY", "FAILURE_FIRST"],
    "blast_radius": ["DEEP_MODULE", "REVERSIBILITY"],
    "uncertainty": ["FAILURE_FIRST", "RADICAL_PRUNING"],
    "vault_novelty": ["INVERSION", "ZERO_DEPENDENCY"],
    "viable_alternatives": ["RADICAL_PRUNING", "DEEP_MODULE"],
}


def provocations_for(dominant_dimension: str) -> List[Dict[str, str]]:
    keys = PROVOCATIONS_BY_DIMENSION.get(dominant_dimension, ["INVERSION", "RADICAL_PRUNING"])
    return [{"id": k, **PROVOCATIONS[k]} for k in keys]


# ---------------------------------------------------------------------------
# Motor de Varianza Visual & Veto Anti-Clon (para decisiones de UI / Frontend)
# ---------------------------------------------------------------------------

_UI_PAT = re.compile(
    r"\b(ui|ux|interfaz|diseno visual|dashboard\w*|prototipo\w*|frontend|landing|maquet\w*|"
    r"pantalla\w*|consola|web app|aplicacion web|layout\w*|componentes|tema|paleta|tipografia)\b"
)

VISUAL_DIRECTIONS: List[Dict[str, str]] = [
    {
        "id": "SWISS_TECHNICAL_PAPER",
        "name": "Swiss Technical Paper (Luz Diurna & Retícula de Tinta)",
        "palette": "Fondo papel técnico `#F4F1EA` / `#EBE6DC`, texto tinta `#141413`, bordes de línea continua `1px solid #CFC8BC`, acento primario Bermellón `#D9381E` y secundario Azul Cobalto `#1849D6`.",
        "typography": "Titulares en `'Space Grotesk'` (700, tracking `-0.03em`), cuerpo en `'DM Sans'`, datos tabulares en `'IBM Plex Mono'`.",
        "layout": "Retícula suiza de celdas unidas por bordes de 1px sin tarjetas flotantes ni sombras. Navegación lateral izquierda vertical (`220px`) con numeración índice (`01`, `02`, `03`).",
    },
    {
        "id": "INDUSTRIAL_DAYLIGHT_HMI",
        "name": "ISA-101 High-Contrast Field HMI (Consola Industrial Antirreflejo)",
        "palette": "Lienzo piedra claro `#E6E8EC` con paneles de control blanco puro `#FFFFFF` y cabecera de grafito sólido `#181B20`. Acentos Naranja Seguridad `#EA580C`, Azul Instrumentación `#0284C7` y Verde Operativo `#15803D`.",
        "typography": "Titulares industriales condensados en `'Barlow'` / `'Chivo'` (700/800), lectura técnica en `'Fira Code'`.",
        "layout": "Arquitectura de consola dividida (Split-Workbench): barra de estado física compacta + riel izquierdo de modos + área de trabajo de doble panel sin 'hero' ni tarjetas decorativas.",
    },
    {
        "id": "BRUTALIST_HAIRLINE_MATRIX",
        "name": "Brutalist Telemetry Matrix (Cero Tarjetas / Bordes al Ras)",
        "palette": "Fondo carbón cálido `#0E0E10` (prohibido azul `slate-950`), líneas divisorias expuestas `#27272A`, texto marfil `#F4F3EF`, acento Lima Ácido `#A3E635` y Cian Técnico `#06B6D4`.",
        "typography": "Titulares de alto impacto en `'Syne'` o `'Archivo'` (800), métricas gigantes (`clamp(2rem,3.5vw,3.25rem)`) en `'JetBrains Mono'`.",
        "layout": "Matriz continua de borde a borde (`gap-px bg-zinc-800`) donde ninguna celda tiene `rounded-xl` ni margen flotante. Cero íconos decorativos en las esquinas.",
    },
    {
        "id": "EDITORIAL_DOSSIER_SPLIT",
        "name": "Editorial Asymmetric Dossier (Pliego Narrativo + Lienzo en Vivo)",
        "palette": "Fondo alabastro `#FAF8F5` (o expreso profundo `#161311`), texto `#1C1917`, acento Terracota/Cobre `#C25E38` y Verde Bosque `#2D6A4F`.",
        "typography": "Contraste editorial: titulares en serif (`'Fraunces'` o `'Instrument Serif'`), interfaz en `'Plus Jakarta Sans'`, código en `'Commit Mono'`.",
        "layout": "Pliego asimétrico de 2 columnas (`320px` columna índice fija + lienzo principal fluido). Las métricas se integran dentro de bloques tipográficos, nunca en 4 cajitas iguales.",
    },
]

ANTI_CLONE_VETO = """\
### 🚫 VETO ANTI-CLON VISUAL (Obligatorio para UI / Frontend)
Queda **prohibido** repetir la plantilla saturada de proyectos anteriores del Vault:
1. **Prohibida la paleta clon:** `bg-slate-950` / `#0b0f19` con tarjetas `bg-slate-900` y acentos `amber-400` + `emerald-400`.
2. **Prohibido el esqueleto clon:** Topbar horizontal con cuadrado `32x32` de iniciales a la izquierda + 4 pestañas + píldora verde a la derecha, seguido de un *eyebrow* en `font-mono uppercase`, seguido de una fila de **4 tarjetas KPI iguales (`grid-cols-4`)**, seguido de un panel ancho.
3. **Tipografía real obligatoria:** Carga las fuentes elegidas con `<link>` de Google Fonts en `index.html` y decláralas en `index.css` (nunca dejes la sans del sistema por omisión).
"""


def is_ui_objective(text: str) -> bool:
    return bool(_UI_PAT.search(_norm(text or "")))


_REDESIGN_PAT = re.compile(
    r"\b(redisen\w*|simplific\w*|limpi\w*|abrumador\w*|sobrecarg\w*|demasiad\w*|"
    r"menos (?:datos|informacion|ruido|tarjetas|metricas|elementos)|densidad|despej\w*|minimal\w*|"
    r"redesign\w*|declutter\w*|simplif\w*|overwhelm\w*|too much (?:data|info)|clean up|cleaner)\b"
)


def detect_redesign_intent(objective: str) -> Dict[str, Any]:
    """Detecta si una petición pide rediseñar o reducir densidad cognitiva en UI."""
    norm = _norm(objective or "")
    is_ui = is_ui_objective(objective)
    hits = _REDESIGN_PAT.findall(norm)
    is_subtractive = bool(hits)
    return {
        "is_ui": is_ui,
        "is_subtractive": is_subtractive,
        "quarantine_legacy_ui": bool(is_ui and is_subtractive),
        "signal_hits": hits,
    }


def compile_ui_density_budget(
    objective: str,
    redesign_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compila peticiones cualitativas de simplificación UI en cotas verificables en DOM real."""
    info = redesign_info or detect_redesign_intent(objective)
    if not info.get("is_ui"):
        return {"active": False, "mode": "non_ui"}
    if info.get("quarantine_legacy_ui"):
        return {
            "active": True,
            "mode": "subtractive_ui_redesign",
            "max_primary_kpis": 4,
            "max_visible_tables": 1,
            "max_charts_above_fold": 1,
            "require_progressive_disclosure": True,
            "require_real_fonts_in_index_html": True,
            "forbid_clone_palette": True,
        }
    return {
        "active": True,
        "mode": "standard_ui",
        "max_primary_kpis": 6,
        "max_visible_tables": 2,
        "max_charts_above_fold": 3,
        "require_progressive_disclosure": False,
        "require_real_fonts_in_index_html": True,
        "forbid_clone_palette": True,
    }


def deal_visual_directions(objective: str, project: str = "General", count: int = 2) -> List[Dict[str, str]]:
    """Sortea determinísticamente direcciones de arte distintas por proyecto/objetivo."""
    seed = int(hashlib.sha1(f"{project.strip().lower()}::{objective.strip().lower()}".encode("utf-8")).hexdigest()[:8], 16)
    pool = list(VISUAL_DIRECTIONS)
    chosen: List[Dict[str, str]] = []
    for i in range(min(count, len(pool))):
        idx = (seed + i * 2 + 1) % len(pool)
        chosen.append(pool.pop(idx))
    return chosen


# ---------------------------------------------------------------------------
# Enrutamiento de Flota de Especialistas ODD (Proporcional al dominio Cynefin)
# ---------------------------------------------------------------------------

_DATA_PAT = re.compile(
    r"\b(postgres\w*|sql\w*|supabase|migracion\w*|esquema\w*|tabla\w*|rls|indice\w*|base de datos|db|prisma|orm)\b"
)
_BACKEND_PAT = re.compile(
    r"\b(api\w*|backend|servicio\w*|endpoint\w*|nestjs|fastapi|python|worker\w*|cola\w*|auth\w*|webhook\w*|mcp|cli)\b"
)


def recommend_specialists(objective: str, domain: str) -> List[Dict[str, str]]:
    """Determina la flota mínima de especialistas según dominio Cynefin y capas afectadas."""
    norm_obj = _norm(objective or "")
    has_ui = is_ui_objective(objective)
    has_data = bool(_DATA_PAT.search(norm_obj))
    has_backend = bool(_BACKEND_PAT.search(norm_obj))

    if domain == CynefinDomain.CLEAR.value:
        if has_ui:
            return [{"agent": "odd-ui-crafter", "model": "flash", "focus": "Ajuste UI puntual"}]
        return []

    fleet: List[Dict[str, str]] = []
    if domain == CynefinDomain.COMPLEX.value:
        fleet.append({
            "agent": "odd-antithesis",
            "model": "inherit",
            "focus": "Propuesta neurodivergente aislada del Vault (primeros principios)",
        })

    if has_backend or not (has_ui or has_data):
        fleet.append({
            "agent": "odd-backend-architect",
            "model": "inherit",
            "focus": "Arquitectura, lógica de dominio, AST y contratos API",
        })
    if has_data:
        fleet.append({
            "agent": "odd-data-guardian",
            "model": "inherit",
            "focus": "Esquemas SQL, migraciones, RLS e integridad de datos",
        })
    if has_ui:
        fleet.append({
            "agent": "odd-ui-crafter",
            "model": "inherit" if domain == CynefinDomain.COMPLEX.value else "flash",
            "focus": "Interfaz, sistema de diseño y Veto Anti-Clon Visual",
        })

    fleet.append({
        "agent": "odd-qa-sentinel",
        "model": "flash",
        "focus": "Verificación independiente (tests reales, build, Playwright)",
    })
    return fleet


# ---------------------------------------------------------------------------
# Paquete de contexto + protocolo (lo consumen el LLM y sus subagentes)
# ---------------------------------------------------------------------------

PROTOCOL_TEXT = """\
## Protocolo D-ODD v4 (Bifurcación + Cuarentena Sustractiva + Lentes + Cero Bucles)
1. **Contrato de outcomes**: job-to-be-done, 2-4 criterios verificables e invariantes. Separa zonas conocidas (`flash`/`flash_lite`) de los 1-2 puntos de bifurcación reales (donde sí inviertes modelo fuerte + `odd-antithesis`, sin papeleo JSON).
2. **Tesis (con Lente Epistémico)** — usa `brain_context(agent_role=...)` para traer solo memoria del dominio afectado (`ui` | `backend` | `data` | `qa`) sin contaminación cruzada.
3. **Antítesis (`odd-antithesis`)** — subagente SIN notas del Vault (`inheritMcp: false`): recibe SOLO el contrato de outcomes, provocaciones y (si es UI) direcciones de arte. **Cuarentena Sustractiva**: si es un rediseño/simplificación UI, también se oculta el código UI legado durante esta fase.
4. **Síntesis + FMEA de 1 Sola Pasada (Sin Bucles)**: decide `thesis` | `antithesis` | `hybrid` en `commit_decision` con 1 chequeo de riesgos. **Prohibido abrir bucles de debate o borradores intermedios.**
5. **Ejecución Acotada + Verificación Real (`odd-qa-sentinel`)**: aplica Veto Anti-Clon + fuentes reales en `index.html` tanto en UI nueva como en rediseños, y audita presupuestos de densidad en DOM/Playwright real.
6. **Vigilia Silenciosa → Cierre (`close_decision`)**: cero ensayos en Markdown durante la ejecución; al verificar con tests reales, cierra la decisión para consolidar memoria útil en segundo plano.
"""


def build_context_packet(objective: str, project: str, assessment: Dict[str, Any],
                         vault_evidence: str = "", decision_id: str = "") -> str:
    provs = provocations_for(assessment["dominant_dimension"])
    dims = assessment["dimensions"]
    fleet = recommend_specialists(objective, assessment["domain"])
    lines = [
        f"### 🌀 D-ODD activado — decisión `{decision_id}`" if decision_id else "### 🌀 D-ODD activado",
        f"- **Proyecto**: [[{project}]]",
        f"- **Objetivo**: {objective}",
        f"- **Dominio**: `{assessment['domain']}` (total {assessment['total']}/15, dominante: `{assessment['dominant_dimension']}`)",
        f"- **Razón**: {assessment['reason']}",
        "- **Dimensiones**: " + ", ".join(f"{k}={v}" for k, v in dims.items()),
        "",
        PROTOCOL_TEXT,
        "### 🤖 Flota de Especialistas Recomendada (Rinden cuentas a AGY)",
    ]
    for sp in fleet:
        lines.append(f"- **`{sp['agent']}`** (`model: {sp['model']}`): {sp['focus']}")

    lines.append("")
    lines.append("### 🎲 Provocaciones para la antítesis (elegidas por la dimensión dominante)")
    for p in provs:
        lines.append(f"- **{p['title']}**: {p['question']}")

    if is_ui_objective(objective):
        directions = deal_visual_directions(objective, project, count=2)
        redesign_info = detect_redesign_intent(objective)
        if redesign_info["quarantine_legacy_ui"]:
            budget = compile_ui_density_budget(objective, redesign_info)
            lines.append("")
            lines.append("### 🧹 Cuarentena Sustractiva & Presupuesto de Densidad UI (D-ODD v4)")
            lines.append(
                "- **Cuarentena en Antítesis**: **PROHIBIDO** entregar el TSX/CSS legado a `odd-antithesis`; "
                "diseña la arquitectura de información solo desde tipos/contratos de dominio."
            )
            lines.append(
                "- **Mandato Sustractivo**: aplica `EXCEPTION_FIRST` / `PROGRESSIVE_DISCLOSURE` / `SINGLE_FOCUS_WORKSPACE` "
                "y mueve >=60% de elementos secundarios a `Drawer`/`Tabs`/`Accordion`/`role=\"tablist\"`."
            )
            lines.append(
                f"- **Presupuesto verificable en DOM/Playwright**: `max_primary_kpis={budget['max_primary_kpis']}`, "
                f"`max_visible_tables={budget['max_visible_tables']}`, `max_charts_above_fold={budget['max_charts_above_fold']}`, "
                f"`require_progressive_disclosure={budget['require_progressive_disclosure']}`, "
                f"fuentes reales en `index.html` obligatorio."
            )
        lines.append("")
        lines.append(ANTI_CLONE_VETO.rstrip())
        lines.append("")
        lines.append("### 🎨 Direcciones de Arte Sorteadas para la Antítesis (elige 1 o combínalas)")
        for idx, d in enumerate(directions, 1):
            lines.append(f"**Opción {idx}: `{d['id']}` — {d['name']}**")
            lines.append(f"- **Paleta**: {d['palette']}")
            lines.append(f"- **Tipografía**: {d['typography']}")
            lines.append(f"- ** Disposición Espacial**: {d['layout']}")

    lines.append("")
    lines.append("### 🏛️ Evidencia del Vault (SOLO para la rama de Tesis / Especialistas con MCP)")
    lines.append(vault_evidence.strip() if vault_evidence.strip() else "_Sin notas relevantes: la tesis se basa en el código actual del proyecto._")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Calibración automática del umbral del gate
# ---------------------------------------------------------------------------

def calibrate(events: Optional[List[Dict[str, Any]]] = None, persist: bool = True) -> Dict[str, Any]:
    """Ajusta gate_threshold con eventos etiquetados (score, verdict).

    - Positivo = el LLM concluyó d_odd. Si un positivo quedó bajo el umbral (omisión), se baja el umbral.
    - Si no hay omisiones y la tasa de falsos positivos entre los disparos > 40%, se sube un paso
      sin dejar ningún positivo por debajo.
    """
    cal = load_calibration()
    events = events if events is not None else labeled_gate_events()
    min_n = int(cal["min_labeled_for_calibration"])
    lo, hi = cal["threshold_bounds"]
    step = float(cal["step"])
    old = float(cal["gate_threshold"])
    report = {"labeled": len(events), "old_threshold": old, "new_threshold": old, "changed": False, "reason": ""}
    if len(events) < min_n:
        report["reason"] = f"Datos insuficientes ({len(events)}/{min_n})."
        return report

    positives = [float(e["score"]) for e in events if e["verdict"] == "d_odd"]
    fired = [e for e in events if float(e["score"]) >= old]
    fp = [e for e in fired if e["verdict"] != "d_odd"]
    missed = [s for s in positives if s < old]

    new = old
    if missed:
        new = max(lo, min(missed) - 0.01, old - step)
        report["reason"] = f"{len(missed)} decisión(es) omitida(s) por el gate: se baja el umbral."
    elif fired and len(fp) / len(fired) > 0.40:
        candidate = min(hi, old + step)
        if positives and min(positives) < candidate:
            candidate = max(old, min(positives))
        new = candidate
        report["reason"] = f"Falsos positivos {len(fp)}/{len(fired)}: se sube el umbral."
    else:
        report["reason"] = "Umbral estable."

    new = round(new, 3)
    if new != old:
        cal["gate_threshold"] = new
        report.update(new_threshold=new, changed=True)
        if persist:
            save_calibration(cal)
    return report
