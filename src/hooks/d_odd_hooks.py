"""
d_odd_hooks.py: Hooks de ciclo de vida de Antigravity para D-ODD automático.

Uso (desde hooks.json):  python d_odd_hooks.py <gate|evidence|stop>
Contrato: JSON por stdin, JSON por stdout. Ante CUALQUIER error imprime una respuesta
neutra y sale con código 0: un hook nunca debe romper el loop del agente.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

NEUTRAL = {"gate": {}, "evidence": {}, "stop": {"decision": "allow"}}

TEST_CMD = re.compile(
    r"\b(pytest|unittest|jest|vitest|mocha|go test|cargo test|flutter test|dart test|"
    r"(npm|pnpm|yarn|bun) (run )?test|playwright test)\b",
    re.IGNORECASE,
)


def hook_gate(payload: dict) -> dict:
    """PreInvocation: una evaluación barata por mensaje nuevo del usuario."""
    from creative_odd import gate_score, input_hash, load_calibration
    import decision_ledger as led

    text = (payload.get("lastUserInput") or "").strip()
    conv = payload.get("conversationId") or ""
    if not text or not conv:
        return {}
    h = input_hash(text)
    if led.last_gate_hash(conv) == h:
        return {}  # mismo mensaje: ya evaluado en una invocación anterior de este turno

    r = gate_score(text, load_calibration())
    led.record_gate_event(conv, h, r["score"], r["threshold"], r["fired"])
    if not r["fired"]:
        return {}
    msg = (
        f"[D-ODD gate · score {r['score']}] Este mensaje podría implicar una decisión de diseño. "
        f"Antes de actuar, llama a la tool MCP `assess_decision` de devbrain con las 5 dimensiones (0-3) "
        f"y conversation_id=\"{conv}\". Si concluyes que no es una decisión, sigue normal: el veredicto "
        f"calibra el gate automáticamente."
    )
    return {"injectSteps": [{"ephemeralMessage": msg}]}


def hook_evidence(payload: dict) -> dict:
    """PostToolUse(run_command): si corrieron tests, adjunta el resultado a decisiones abiertas."""
    import decision_ledger as led

    call = payload.get("toolCall") or {}
    cmd = str((call.get("args") or {}).get("CommandLine") or "")
    conv = payload.get("conversationId") or ""
    if not conv or not TEST_CMD.search(cmd):
        return {}
    err = payload.get("error") or ""
    led.attach_evidence(conv, {"type": "test_run", "command": cmd[:200], "passed": not err, "error": str(err)[:200]})
    return {}


def hook_stop(payload: dict) -> dict:
    """Stop: pide cerrar (una sola vez) decisiones comprometidas que ya tienen evidencia."""
    import decision_ledger as led

    if payload.get("terminationReason") not in (None, "", "NO_TOOL_CALL"):
        return {"decision": "allow"}
    conv = payload.get("conversationId") or ""
    if not conv:
        return {"decision": "allow"}
    pending = led.decisions_needing_close(conv)
    if not pending:
        return {"decision": "allow"}
    for d in pending:
        led.mark_close_requested(d["id"])
    lines = []
    for d in pending:
        ev = d["evidence"][-1]
        status = "✅ pasó" if ev.get("passed") else "❌ falló"
        lines.append(f"- `{d['id']}` ({d.get('chosen') or '?'}): {d['objective'][:80]} · último test {status}")
    reason = (
        "[D-ODD] Hay decisiones con evidencia y sin cerrar. Llama `close_decision` para cada una "
        "(outcome: success | partial | failed, con una nota breve). Si aún no terminó la implementación, "
        "dilo y termina el turno; no se volverá a pedir.\n" + "\n".join(lines)
    )
    return {"decision": "continue", "reason": reason}


HANDLERS = {"gate": hook_gate, "evidence": hook_evidence, "stop": hook_stop}


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    out = NEUTRAL.get(mode, {})
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        payload = json.loads(raw) if raw.strip() else {}
        if mode in HANDLERS:
            out = HANDLERS[mode](payload)
    except Exception as exc:  # nunca romper el loop del agente
        try:
            import decision_ledger as led
            (led.devbrain_home() / "hooks_errors.log").open("a", encoding="utf-8").write(f"{mode}: {exc!r}\n")
        except Exception:
            pass
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
