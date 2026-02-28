# VectorClaw Setup Skill (`vector_setup`)

The **`vector_setup`** OpenClaw skill gives any user a guided, foolproof path
from zero to a working VectorClaw MCP integration.  It covers configuration,
SDK installation, connectivity validation, and a self-test — all in one step.

---

## Quick Start

### Option A — Interactive CLI wizard

Run the `vectorclaw-setup` console script after installing the package:

```bash
pip install vectorclaw-mcp
vectorclaw-setup
```

You will be prompted for:

| Field | Required? | Where to find it |
|---|---|---|
| **Robot serial number** | ✅ Yes | Vector app → Settings → My Vector → Serial Number, or sticker under the robot |
| **Robot IP address** | ❌ Optional | Only needed if Wire-Pod auto-discovery fails |

The wizard writes your config to
`~/.openclaw/workspace/config/mcporter.json` and then runs connectivity
and smoke checks.  At the end you get a clear **SETUP PASSED** or
**SETUP FAILED** with exact remediation steps.

**Example output (success):**

```
============================================================
  VectorClaw MCP — Setup Wizard
============================================================

Robot serial number (required): 00e20142
Robot IP address (optional, press Enter to skip): 

  Serial : 00e20142
  Host   : (auto-discover via Wire-Pod)

  ✅ python_version: Python 3.11.8 is fully compatible.
  ✅ write_config: Configuration written to ~/.openclaw/workspace/config/mcporter.json
  ✅ sdk_import: anki_vector SDK imported successfully (version: 0.8.0).
  ✅ connectivity: Successfully connected to robot 00e20142.
  ✅ smoke_test: All smoke tests passed.

============================================================
  ✅  SETUP PASSED
============================================================

VectorClaw is configured and ready to use!
Start the MCP server with: vectorclaw-mcp
Or restart OpenClaw — it will pick up the updated config automatically.
```

**Example output (failure):**

```
============================================================
  ❌  SETUP FAILED
============================================================

Remediation steps:
• connectivity: Ensure Wire-Pod is running and the robot is on the same
  network.  If using VECTOR_HOST, verify the IP address is reachable.
  See docs/SETUP.md for full troubleshooting steps.
```

---

### Option B — MCP tool (`vector_setup`)

Ask your OpenClaw-connected AI assistant to run the setup skill:

```
Please run vector_setup with serial="00e20142"
```

Or with an explicit IP:

```
Run vector_setup with serial="00e20142" and host="192.168.1.50"
```

The tool returns a structured JSON report:

```json
{
  "status": "pass",
  "summary": "  ✅ python_version: ...\n  ✅ connectivity: ...\n  ...",
  "checks": [...],
  "next_steps": "VectorClaw is configured and ready to use! ..."
}
```

On failure the report includes a `"remediation"` field with exact fix steps.

---

## Tool Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `serial` | string | env `VECTOR_SERIAL` | Robot serial number |
| `host` | string | env `VECTOR_HOST` | Robot IP address (optional) |
| `write_config` | bool | `true` | Write config to `~/.openclaw/workspace/config/mcporter.json` |
| `install_sdk` | bool | `true` | Auto-install `wirepod_vector_sdk` if missing |
| `run_connectivity` | bool | `true` | Attempt a live connection to the robot |
| `run_smoke` | bool | `true` | Run status read + head-move smoke test |

---

## What the Skill Checks

| Step | What it validates |
|---|---|
| `python_version` | Python ≥ 3.10 (3.11+ recommended) |
| `config_validation` | `VECTOR_SERIAL` is present |
| `write_config` | Config file is writable at the OpenClaw path |
| `sdk_import` | `import anki_vector` succeeds |
| `sdk_install` | (Only runs when SDK is absent) — installs from pinned upstream commit |
| `connectivity` | Robot responds to a live connection attempt |
| `smoke_test` | Status read + harmless head-move both return success |

---

## Failure Modes and Remediation

| Failure check | Likely cause | Exact fix |
|---|---|---|
| `python_version` | Python < 3.10 | Install Python 3.11: https://python.org/downloads |
| `config_validation` | No serial number supplied | Find serial in Vector app → Settings → My Vector → Serial Number |
| `write_config` | Permission denied on `~/.openclaw/` | `mkdir -p ~/.openclaw/workspace/config` then re-run |
| `sdk_import` | wirepod_vector_sdk not installed | `pip install git+https://github.com/kercre123/wirepod-vector-python-sdk.git@065fc197d592d76a164d64dcf0a768183ab37855` |
| `connectivity` | Wire-Pod not running or wrong IP | Start Wire-Pod; verify `VECTOR_HOST` if set; see [SETUP.md](SETUP.md) |
| `smoke_test` | Robot not responding to commands | Check physical robot state; repeat connectivity check |

---

## Config File Location

The skill writes to `~/.openclaw/workspace/config/mcporter.json`.

**Resulting file (example):**

```json
{
  "env": {
    "VECTOR_SERIAL": "00e20142",
    "VECTOR_HOST": "192.168.1.50"
  }
}
```

Any pre-existing keys in the file are preserved — the skill only merges the
`env.VECTOR_SERIAL` and `env.VECTOR_HOST` entries.

---

## Environment Variables

You can pre-populate values using environment variables to skip the prompts:

```bash
export VECTOR_SERIAL=00e20142
export VECTOR_HOST=192.168.1.50   # optional
vectorclaw-setup
```

---

## See Also

- [SETUP.md](SETUP.md) — Full Wire-Pod + SDK installation guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Deep-dive failure diagnosis
- [MCP_API_REFERENCE.md](MCP_API_REFERENCE.md) — All available MCP tools
