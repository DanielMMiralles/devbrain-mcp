"""
creative_odd.py: Núcleo D-ODD v2 (Dynamic Outcome-Driven Development).

Separación de responsabilidades:
  - El GATE (barato, determinista, calibrable) solo decide si vale la pena preguntarle al LLM.
  - El JUICIO lo hace el LLM entregando 5 dimensiones; aquí solo se mapean a Cynefin.
  - La DIVERGENCIA real ocurre en subagentes con contextos aislados (ver PROTOCOL_TEXT);
    este módulo NO fabrica tesis/antítesis/síntesis enlatadas, entrega un paquete de contexto.
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
        r"\breestructur\w*", r"\bredisen\w*", r"\bdesacopl\w*", r"\bdecoupl\w*", r"\bdesign\w*", r"\barchitect\w*", r"\bchoose\b",
        r"\bshould we\b", r"\breplace\b", r"\bplanteamiento\b", r"\benfoque\b",
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
    ],
    "stack_terms": [
        r"\bkafka\b", r"\bpostgres\w*", r"\bredis\b", r"\bsqlite\b", r"\bmongo\w*", r"\bgraphql\b",
        r"\bkubernetes\b", r"\bk8s\b", r"\bsupabase\b", r"\bnestjs\b", r"\bfastapi\b", r"\bnext\.?js\b",
        r"\brabbitmq\b", r"\bwebsockets?\b", r"\bgrpc\b", r"\brest\b", r"\borm\b", r"\bsse\b",
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
    hits: Dict[str, int] = {}
    score = 0.0
    for group, pats in _COMPILED.items():
        n = sum(1 for p in pats if p.search(t))
        if not n:
            continue
        hits[group] = n
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
# Paquete de contexto + protocolo (lo consumen el LLM y sus subagentes)
# ---------------------------------------------------------------------------

PROTOCOL_TEXT = """\
## Protocolo D-ODD (divergencia con contextos aislados)
1. **Contrato de outcomes** (tú, antes de nada): job-to-be-done, 2-4 criterios de aceptación verificables, invariantes.
2. **Tesis** — subagente CON acceso al Vault/MCP: la mejor solución alineada al historial del proyecto, citando las notas en las que se apoya.
3. **Antítesis** — subagente SIN notas del Vault (pásale SOLO el contrato de outcomes y las provocaciones): solución desde primeros principios. No le compartas la tesis.
   Lanza tesis y antítesis en paralelo. Si tu cliente no tiene subagentes, redacta la antítesis ANTES de leer la evidencia del Vault.
4. **Síntesis** — evalúa ambas contra el contrato (no contra preferencias): elige `thesis`, `antithesis` o `hybrid` y justifica con criterios concretos.
5. Llama `commit_decision` con la elección y la síntesis. Implementa. Al verificar con evidencia real, llama `close_decision`.
Regla: si la antítesis no aporta nada mejor, elegir la tesis es un resultado válido; no fuerces la novedad.
"""


def build_context_packet(objective: str, project: str, assessment: Dict[str, Any],
                         vault_evidence: str = "", decision_id: str = "") -> str:
    provs = provocations_for(assessment["dominant_dimension"])
    dims = assessment["dimensions"]
    lines = [
        f"### 🌀 D-ODD activado — decisión `{decision_id}`" if decision_id else "### 🌀 D-ODD activado",
        f"- **Proyecto**: [[{project}]]",
        f"- **Objetivo**: {objective}",
        f"- **Dominio**: `{assessment['domain']}` (total {assessment['total']}/15, dominante: `{assessment['dominant_dimension']}`)",
        f"- **Razón**: {assessment['reason']}",
        "- **Dimensiones**: " + ", ".join(f"{k}={v}" for k, v in dims.items()),
        "",
        PROTOCOL_TEXT,
        "### 🎲 Provocaciones para la antítesis (elegidas por la dimensión dominante)",
    ]
    for p in provs:
        lines.append(f"- **{p['title']}**: {p['question']}")
    lines.append("")
    lines.append("### 🏛️ Evidencia del Vault (SOLO para el subagente de tesis)")
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
