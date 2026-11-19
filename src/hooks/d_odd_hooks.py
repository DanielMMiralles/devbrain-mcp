"""
d_odd_hooks.py: Hooks de ciclo de vida de Antigravity para DevBrain v4 (D-ODD + ECC Guardrails + SessionStart).

Uso (desde hooks.json del plugin):  python d_odd_hooks.py <session_start|gate|guard|evidence|stop>
Contrato: JSON por stdin, JSON por stdout. Ante CUALQUIER error imprime una respuesta
neutra y sale con código 0: un hook nunca debe romper el loop del agente.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

NEUTRAL = {
    "session_start": {},
    "gate": {},
    "guard": {"decision": "allow"},
    "evidence": {},
    "stop": {"decision": "allow"},
}

TEST_CMD = re.compile(
    r"\b(pytest|unittest|jest|vitest|mocha|go test|cargo test|flutter test|dart test|"
    r"(npm|pnpm|yarn|bun) (run )?test|playwright test)\b",
    re.IGNORECASE,
)

RISKY_CMD = re.compile(
    r"(--no-verify\b|git\s+push\b[^\n]*(--force|-f)\b.*\b(main|master)\b|\bDROP\s+DATABASE\b|\bTRUNCATE\s+TABLE\b)",
    re.IGNORECASE,
)

SECRET_PAT = re.compile(
    r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,})"
)


def hook_session_start(payload: dict) -> dict:
    """SessionStart: inyecta el briefing L1 ontológico (<400 tokens, <15ms) una vez al abrir sesión."""
    try:
        from ontology_engine import build_session_briefing
        briefing = build_session_briefing(payload.get("workspacePaths") or [], payload.get("cwd") or "")
        if not briefing.strip():
            return {}
        return {"injectSteps": [{"systemMessage": {"systemMessage": briefing}}]}
    except Exception:
        return {}


def hook_gate(payload: dict) -> dict:
    """PreInvocation: una evaluación barata por mensaje nuevo del usuario usando systemMessage oficial."""
    from creative_odd import gate_score, input_hash, load_calibration
    import decision_ledger as led

    text = (payload.get("lastUserInput") or "").strip()
    conv = payload.get("conversationId") or ""
    if not text or not conv:
        return {}
    h = input_hash(text)
    if led.last_gate_hash(conv) == h:
        return {}

    r = gate_score(text, load_calibration())
    led.record_gate_event(conv, h, r["score"], r["threshold"], r["fired"])
    if not r["fired"]:
        return {}
    msg = (
        f"[D-ODD gate · score {r['score']}] Este mensaje podría implicar una decisión de diseño/arquitectura. "
        f"Antes de actuar, llama a la tool MCP `assess_decision` de devbrain con las 5 dimensiones (0-3) "
        f"y conversation_id=\"{conv}\". Si concluyes que no es una decisión, sigue normal: el veredicto "
        f"calibra el gate automáticamente."
    )
    return {"injectSteps": [{"systemMessage": {"systemMessage": msg}}]}


def hook_guard(payload: dict) -> dict:
    """PreToolUse (<5ms, 0 tokens, patrón ECC AgentShield): frena comandos riesgosos y fugas de secretos."""
    call = payload.get("toolCall") or {}
    tname = (call.get("name") or "").lower()
    args = call.get("args") or {}

    if tname == "run_command":
        cmd = str(args.get("CommandLine") or "")
        if RISKY_CMD.search(cmd):
            return {
                "decision": "ask",
                "reason": "[DevBrain ECC Guard] Comando riesgoso detectado (--no-verify / force-push / SQL destructivo); confirma antes de ejecutar.",
            }
        return {"decision": "allow"}

    if tname in ("write_file", "edit_file"):
        fpath = str(args.get("Path") or "")
        fname = Path(fpath).name.lower()
        if fname in ("mcp_config.json", ".env") or fname.startswith(".env.") or fname.startswith("test_"):
            return {"decision": "allow"}
        body = str(args.get("Content") or args.get("Replacement") or "")
        if body and SECRET_PAT.search(body):
            return {
                "decision": "ask",
                "reason": f"[DevBrain ECC Guard] Posible secreto/API key detectado en {fname}; confirma o muévelo a variables de entorno.",
            }
        return {"decision": "allow"}

    return {"decision": "allow"}


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
    """Stop: guarda resumen mínimo de sesión (Strategic Compact ligero) y pide cerrar decisiones con evidencia."""
    import decision_ledger as led

    conv = payload.get("conversationId") or ""
    if conv:
        try:
            from ontology_engine import resolve_project, save_session_state, ready_activities
            wpaths = payload.get("workspacePaths") or []
            cwd = payload.get("cwd") or ""
            proj = "General"
            for cand in [*wpaths, cwd]:
                if cand:
                    r = resolve_project(str(cand))
                    if r != str(cand) and r != "General":
                        proj = r
                        break
            last_in = (payload.get("lastUserInput") or "").strip()[:180]
            acts = [a["id"] for a in ready_activities(proj if proj != "General" else "", limit=4)]
            save_session_state(conv, proj, last_in, acts)
        except Exception:
            pass

    if payload.get("terminationReason") not in (None, "", "NO_TOOL_CALL"):
        return {"decision": "allow"}
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


HANDLERS = {
    "session_start": hook_session_start,
    "gate": hook_gate,
    "guard": hook_guard,
    "evidence": hook_evidence,
    "stop": hook_stop,
}


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    out = NEUTRAL.get(mode, {})
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        payload = json.loads(raw) if raw.strip() else {}
        if mode in HANDLERS:
            out = HANDLERS[mode](payload)
    except Exception as exc:
        try:
            import decision_ledger as led
            (led.devbrain_home() / "hooks_errors.log").open("a", encoding="utf-8").write(f"{mode}: {exc!r}\n")
        except Exception:
            pass
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
