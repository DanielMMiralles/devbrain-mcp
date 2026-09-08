"""
Automated Test Suite for DevBrain MCP Server (JSON-RPC stdio verification)
Sends initialize, tools/list, and ping to ensure full MCP spec compliance.
"""
import subprocess
import json
import sys
from pathlib import Path

SERVER_SCRIPT = Path(__file__).resolve().parent.parent / "src" / "devbrain_mcp.py"

def run_test():
    print(f"[TEST] Launching DevBrain MCP Server: {SERVER_SCRIPT}")
    proc = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
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
    assert len(tools) == 16, f"Expected 16 tools, got {len(tools)}"

    # 3. Test tools/call (list_projects)
    call_request = {
        "jsonrpc": "2.0",
        "id": 3,
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

    # 4. Test ping
    ping_request = {"jsonrpc": "2.0", "id": 4, "method": "ping"}
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
