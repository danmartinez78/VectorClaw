# VectorClaw Security Architecture

This document describes the security model of VectorClaw: its threat model,
credential handling practices, network security posture, and input validation
approach. For vulnerability *reporting* instructions, see
[SECURITY.md](../SECURITY.md).

---

## 1. Threat Model

### 1.1 System Architecture

```
┌─────────────┐    stdio MCP    ┌──────────────────┐    gRPC/WiFi    ┌─────────┐
│  AI Agent   │ ─────────────── │  vectorclaw-mcp  │ ─────────────── │  Vector │
│  (OpenClaw) │                 │  (Python)        │                 │  Robot  │
└─────────────┘                 └──────────────────┘                 └─────────┘
       ↑                                 ↑                                 ↑
  MCP client                     attack surface                   physical access
  (trust boundary)              (this process)                  (trust boundary)
```

### 1.2 Attack Surface

| Component | Description |
|-----------|-------------|
| **MCP protocol (stdio transport)** | VectorClaw communicates with the AI agent over stdin/stdout. All MCP tool calls enter the process through this channel. A compromised or malicious MCP client can send arbitrary tool inputs. |
| **SDK connection (WiFi to robot)** | The Anki Vector SDK communicates with the robot over the local WiFi network using gRPC over a TLS connection authenticated with per-robot certificates stored in `~/.anki_vector/`. Any device on the same LAN with access to those certificates can issue SDK commands. |
| **Physical robot access** | Any person with physical access to Vector can reset it, observe its camera feed, or interact with it directly. VectorClaw has no mechanism to prevent or detect physical access. |
| **Environment variables** | `VECTOR_SERIAL` and `VECTOR_HOST` are read from the process environment. A process that can modify the environment before VectorClaw starts could redirect connections. |

### 1.3 Trust Boundaries

```
User → AI Agent (OpenClaw) → MCP (stdio) → vectorclaw-mcp → SDK → Vector Robot
```

- **AI Agent** is trusted to call only the tools the user authorised. A
  compromised or prompt-injected agent is a realistic attack vector.
- **vectorclaw-mcp** is the last line of defence before SDK calls reach the
  robot. Input validation (Section 4) is enforced here.
- **Vector robot** is treated as a trusted but physically accessible actuator.
  VectorClaw cannot authenticate the physical robot it is speaking to beyond
  what the SDK certificate exchange provides.

### 1.4 Adversary Capabilities

| Adversary | Capabilities | Mitigations |
|-----------|-------------|-------------|
| **Local network attacker** | Can attempt to intercept WiFi traffic between VectorClaw and the robot. | SDK uses TLS with per-robot certificates; passive eavesdropping is limited. Certificates should have restrictive file permissions (see Section 2). |
| **Compromised MCP client** | Can call any exposed tool with arbitrary arguments. | Input validation rejects out-of-range values; tool dispatch is an explicit allowlist. Unknown tool names return an error rather than executing anything. |
| **Malicious input injection** | Can attempt to inject oversized payloads, invalid data types, or values designed to cause unexpected robot behaviour. | `vector_face` enforces `duration_sec` bounds (0.1–60.0 s) and validates Base64/image data before sending to the robot. `vector_drive` and `vector_cube` only accept typed values from the schema. |
| **Process environment manipulation** | Can redirect robot connections by changing `VECTOR_SERIAL` or `VECTOR_HOST` before the process starts. | These variables are only read at connection time. Deployments should use locked-down process environments (e.g., systemd `EnvironmentFile` with `0600` permissions). |

---

## 2. Credential Handling

### 2.1 `VECTOR_SERIAL`

`VECTOR_SERIAL` is the robot's serial number (e.g., `009050ae`). It is not a
secret in the cryptographic sense — it is printed on the robot and appears in
log output from the official app. However, it is PII-adjacent because it
uniquely identifies a specific physical device and its owner.

**Recommendations:**

- Do not commit `VECTOR_SERIAL` to version control.
- Do not include it in bug reports or public logs.
- Supply it via an environment variable or a secrets manager rather than
  hardcoding it in configuration files that may be shared.

### 2.2 SDK Certificates

The Anki Vector SDK stores per-robot TLS certificates and configuration in
`~/.anki_vector/<serial>.cert` and `~/.anki_vector/<serial>.conf`. These
files are used to authenticate the SDK client to the robot.

**Handling rules enforced by VectorClaw:**

- Certificate paths are never logged or returned in tool responses.
- Error messages from the SDK connection layer do not include certificate
  content (see Section 2.3).
- The connection manager reads only the serial and optional IP address from the
  environment; certificate paths are resolved internally by the SDK.

**Recommended file permissions:**

```bash
chmod 700 ~/.anki_vector/
chmod 600 ~/.anki_vector/*.cert ~/.anki_vector/*.conf
```

Wire-Pod users should apply the same permissions to cert files copied from the
Wire-Pod data directory.

### 2.3 Error Message Sanitization

Tool error responses are returned to the MCP client as JSON and may ultimately
be shown to an end user or logged by the AI agent.

Current practice in `server.py`:

```python
except Exception as exc:
    logger.exception("Tool %r raised an exception", name)
    result = {"status": "error", "message": str(exc)}
```

**Known considerations:**

- `str(exc)` for SDK connection errors may include the robot's IP address (from
  `VECTOR_HOST` or the SDK's internal discovery). This is generally low risk
  on a local network, but deployments that log tool responses externally should
  be aware of this.
- The robot serial number (`VECTOR_SERIAL`) is not included in SDK exception
  messages in normal operation.
- Certificate file contents are never included in exception messages.

If stricter sanitization is required (e.g., when logs are forwarded to an
external system), wrap the `call_tool` exception handler to strip IP addresses
from error strings before returning them.

---

## 3. Network Security

### 3.1 WiFi Requirements

Vector only supports **2.4 GHz WiFi** (802.11 b/g/n). It does not support
5 GHz bands. VectorClaw and the robot must be on the same local network
segment; no public internet access is required or used.

### 3.2 Local-Only Operation

VectorClaw has no cloud dependency at runtime. All communication is:

- **MCP ↔ vectorclaw-mcp:** stdio (local process boundary).
- **vectorclaw-mcp ↔ Vector robot:** gRPC over TLS, local WiFi only.

No data is sent to Anki, Digital Dream Labs, or any third-party service during
normal operation (Wire-Pod setup path).

### 3.3 Wire-Pod (Self-Hosted Server)

Wire-Pod replaces the Digital Dream Labs cloud services with a locally-hosted
server. Security considerations:

- Wire-Pod listens on a local HTTP port (default `8080`) for its management
  interface. This port should not be exposed to untrusted networks (e.g., do
  not port-forward it to the internet).
- Wire-Pod generates the TLS certificates that the SDK uses to authenticate
  with the robot. The security of the robot connection therefore depends on
  the security of the Wire-Pod host.
- Certificates from Wire-Pod should be stored with `0600` permissions as
  described in Section 2.2.

### 3.4 mDNS / `escapepod.local` Exposure

Wire-Pod uses mDNS (Bonjour/Avahi) to advertise itself as `escapepod.local` on
the local network. This hostname is how Vector discovers its server after
firmware modification.

- `escapepod.local` is only resolvable on the local network; it is not routable
  over the internet.
- Any device on the same LAN can resolve `escapepod.local` and reach the
  Wire-Pod management interface. Ensure the LAN is trusted (e.g., not a public
  guest network).
- If multiple Wire-Pod instances are running on the same LAN, mDNS conflicts
  may cause Vector to connect to the wrong server.

---

## 4. Input Validation

### 4.1 Base64 Decoding (`vector_face`)

The `vector_face` tool accepts a Base64-encoded image from the MCP client and
decodes it before sending to the robot.

**Risks and mitigations:**

| Risk | Mitigation |
|------|-----------|
| **DoS via large payload** | The MCP stdio transport does not impose a hard message size limit. A very large Base64 string will consume memory during decoding and PIL image processing. Consider adding an explicit size check (e.g., reject strings longer than ~10 MB) in high-throughput or multi-tenant deployments. |
| **Malformed Base64** | `base64.b64decode` raises an exception on invalid input; `vector_face` catches this and returns `{"status": "error", ...}` without crashing the server. |
| **Malicious image data** | PIL's `Image.open` is used to decode the image. PIL/Pillow has historically had parsing vulnerabilities; keep Pillow updated. The image is immediately resized to 144×108 pixels, which limits memory amplification from large inputs. |

### 4.2 `duration_sec` Bounds (`vector_face`)

```python
if not (0.1 <= duration_sec <= 60.0):
    return {"status": "error", "message": "duration_sec must be between 0.1 and 60.0"}
```

Values outside the range 0.1–60.0 seconds are rejected before any robot
interaction. This prevents accidentally locking the robot's face display for
an arbitrarily long time.

### 4.3 Movement Limits (`vector_drive`)

`vector_drive` does not currently impose bounds on `distance_mm` or
`angle_deg` beyond what the robot's firmware enforces internally. Very large
values will cause the robot to drive until it hits an obstacle or the firmware
limits are reached. Callers should be aware of the physical environment when
issuing drive commands.

### 4.4 Command Injection Prevention

VectorClaw does not invoke any shell commands or subprocesses. All robot
control goes through the typed Python SDK API. There is no shell interpolation
or `eval`-style execution path, so traditional command injection is not
applicable.

### 4.5 Tool Dispatch Allowlist

The `call_tool` dispatcher in `server.py` uses an explicit dict of known tool
names:

```python
dispatch: dict[str, Any] = {
    "vector_say": ...,
    "vector_animate": ...,
    ...
}
handler = dispatch.get(name)
if handler is None:
    result = {"status": "error", "message": f"Unknown tool: {name!r}"}
```

Unknown tool names produce an error response and are not executed. This
prevents a compromised MCP client from invoking arbitrary Python callables.

---

## 5. Related Documents

- [SECURITY.md](../SECURITY.md) — Vulnerability reporting policy
- [docs/SETUP.md](SETUP.md) — Robot and SDK setup guide
- [README.md](../README.md) — Project overview
