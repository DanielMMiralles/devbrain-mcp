"""
Automated Test Suite for DevBrain MCP Server (JSON-RPC stdio verification)
Sends initialize, tools/list, and ping to ensure full MCP spec compliance.
"""
import subprocess
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SERVER_SCRIPT = Path(__file__).resolve().parent.parent / "src" / "devbrain_mcp.py"

def run_test():
    print(f"[TEST] Launching DevBrain MCP Server: {SERVER_SCRIPT}")
    proc = subprocess.Popen(
        [sys.executable, "-u", str(SERVER_SCRIPT)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    # 1. Test initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "DevBrainTester", "version": "1.0.0"}
        }
    }
    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()
    init_response = json.loads(proc.stdout.readline())
    assert init_response.get("id") == 1, "Initialize response ID mismatch"
    assert "result" in init_response, "Initialize response missing result"
    server_info = init_response["result"].get("serverInfo", {})
    assert server_info.get("version") == "4.1.0", f"Expected version 4.1.0, got {server_info.get('version')}"
    print(f"  [OK] Initialized: {server_info.get('name')} v{server_info.get('version')}")

    # 2. Test tools/list
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    proc.stdin.write(json.dumps(tools_request) + "\n")
    proc.stdin.flush()
    tools_response = json.loads(proc.stdout.readline())
    tools = tools_response.get("result", {}).get("tools", [])
    print(f"  [OK] tools/list returned {len(tools)} tools:")
    for t in tools:
        print(f"       - {t['name']}: {t['description'][:60]}...")
    assert len(tools) == 12, f"Expected 12 consolidated tools, got {len(tools)}"
    tool_names = [t["name"] for t in tools]
    for expected in ["brain_context", "brain_tree", "brain_activity", "brain_remember", "assess_decision", "orchestrate_gentle_task", "capture_weekly_snapshot", "audit_cortex_health"]:
        assert expected in tool_names, f"{expected} missing from tools list"

    # 2b. Test resources/list
    res_request = {"jsonrpc": "2.0", "id": 21, "method": "resources/list", "params": {}}
    proc.stdin.write(json.dumps(res_request) + "\n")
    proc.stdin.flush()
    res_response = json.loads(proc.stdout.readline())
    resources = res_response.get("result", {}).get("resources", [])
    assert len(resources) == 3, f"Expected 3 MCP resources, got {len(resources)}"
    print(f"  [OK] resources/list returned {len(resources)} resources")

    # 3. Test tools/call (classify_odd_task)
    odd_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "classify_odd_task",
            "arguments": {
                "request_description": "Migrar módulo de usuarios a NestJS con OAuth2",
                "files_touched_estimate": 4
            }
        }
    }
    proc.stdin.write(json.dumps(odd_request) + "\n")
    proc.stdin.flush()
    odd_response = json.loads(proc.stdout.readline())
    assert "result" in odd_response, "tools/call classify_odd_task failed"
    odd_content = odd_response["result"].get("content", [])
    assert len(odd_content) > 0, "tools/call classify_odd_task returned empty content"
    assert "[SUBSTANTIAL_ODD]" in odd_content[0]["text"], "Classification mismatch"
    print("  [OK] tools/call (classify_odd_task) returned [SUBSTANTIAL_ODD] successfully")

    # 4. Test tools/call (optimize_token_budget)
    opt_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "optimize_token_budget",
            "arguments": {
                "target_text": "def compute_total(items):\n    # docstring\n    total = 0\n    for item in items:\n        total += item.price\n    return total\n",
                "mode": "ast",
                "language": "python"
            }
        }
    }
    proc.stdin.write(json.dumps(opt_request) + "\n")
    proc.stdin.flush()
    opt_response = json.loads(proc.stdout.readline())
    assert "result" in opt_response, "tools/call optimize_token_budget failed"
    opt_content = opt_response["result"].get("content", [])
    assert len(opt_content) > 0, "tools/call optimize_token_budget returned empty"
    print(f"       Debug optimize_token_budget response: {opt_content[0]['text'][:100]}")
    assert "Code AST Slicing" in opt_content[0]["text"], "AST slicing result missing header"
    print("  [OK] tools/call (optimize_token_budget) executed successfully")

    # 5. Test tools/call (list_projects)
    call_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "list_projects",
            "arguments": {}
        }
    }
    proc.stdin.write(json.dumps(call_request) + "\n")
    proc.stdin.flush()
    call_response = json.loads(proc.stdout.readline())
    assert "result" in call_response, "tools/call failed"
    content_list = call_response["result"].get("content", [])
    assert len(content_list) > 0, "tools/call returned empty content"
    print(f"  [OK] tools/call (list_projects) executed successfully:")
    for line in content_list[0]["text"].splitlines()[:4]:
        print(f"       {line}")

    # 6. Test ping
    ping_request = {"jsonrpc": "2.0", "id": 6, "method": "ping"}
    proc.stdin.write(json.dumps(ping_request) + "\n")
    proc.stdin.flush()
    ping_response = json.loads(proc.stdout.readline())
    assert ping_response.get("result") == {}, "Ping failed"
    print("  [OK] ping responded successfully")

    # Clean termination
    proc.stdin.close()
    proc.terminate()
    proc.wait(timeout=2)
    print("\n[SUCCESS] DevBrain MCP Server passed all JSON-RPC stdio contract tests!\n")

if __name__ == "__main__":
    run_test()
