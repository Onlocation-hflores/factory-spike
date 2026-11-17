#!/usr/bin/env python3
"""SPIKE-01 stub engine for gh-aw: no model. Runs in place of the `claude` executable.

1. H3 canary: reports the sha256 (never the value) of canaries it can see from inside the agent sandbox.
2. H2: edits a file and calls the safe-outputs MCP tool create_pull_request with a fixed branch name.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request


def h(v):
    return hashlib.sha256(v.encode()).hexdigest()[:16] if v else "absent"


print("STUB argc:", len(sys.argv))
print("CANARY_A (via $GITHUB_ENV)   :", h(os.environ.get("CANARY_A", "")))
print("CANARY_B (workflow env)      :", h(os.environ.get("CANARY_B", "")))
for p in ["/tmp/canary_c.txt", os.path.expanduser("~/canary_c.txt")]:
    v = pathlib.Path(p).read_text().strip() if os.path.exists(p) else ""
    print(f"CANARY_C file {p}:", h(v))
print("ENV NAMES visible:", len(os.environ))

pathlib.Path("spike-change.txt").write_text(f"stub edit {time.time_ns()}\n")
subprocess.run(["git", "add", "spike-change.txt"], check=True)
subprocess.run(["git", "-c", "user.name=stub", "-c", "user.email=stub@invalid", "commit", "-qm", "stub edit"], check=True)

cfg_path = pathlib.Path(os.environ["RUNNER_TEMP"]) / "gh-aw/mcp-config/mcp-servers.json"
cfg = json.loads(cfg_path.read_text())["mcpServers"]
so = next(v for k, v in cfg.items() if "safe" in k.lower())
url, headers = so["url"], dict(so.get("headers", {}))
headers.update({"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})


def rpc(method, params, rid):
    body = {"jsonrpc": "2.0", "method": method, "params": params}
    if rid is not None:
        body["id"] = rid
    r = urllib.request.urlopen(urllib.request.Request(url, json.dumps(body).encode(), headers), timeout=60)
    if r.headers.get("Mcp-Session-Id"):
        headers["Mcp-Session-Id"] = r.headers["Mcp-Session-Id"]
    return r.read().decode()


rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "stub", "version": "0"}}, 1)
rpc("notifications/initialized", {}, None)
out = rpc("tools/call", {"name": "create_pull_request", "arguments": {
    "title": "spike: duplicate test", "body": "stub engine, no model", "branch": "factory/ghaw-dup"}}, 2)
print("create_pull_request ->", out[:500])
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "num_turns": 1, "result": "stub done"}))
