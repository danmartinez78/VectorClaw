# Onboarding Quickstart (5-Minute Path)

## Goal
Get a first-time user to a working VectorClaw MCP setup quickly and safely.

## Prerequisites
- Wire-Pod running and robot reachable
- Python 3.11+
- OpenClaw environment ready
- Vector serial available

## 1) Install SDK (pinned)
```bash
pip install git+https://github.com/kercre123/wirepod-vector-python-sdk.git@065fc197d592d76a164d64dcf0a768183ab37855
```

## 2) Set required env
```bash
export VECTOR_SERIAL="YOUR_VECTOR_SERIAL"
# optional:
export VECTOR_HOST="ROBOT_IP_OR_HOST"
```

## 3) One-time SDK auth/config
```bash
python -m anki_vector.configure --serial "$VECTOR_SERIAL"
```

## 4) Verify import
```bash
python -c "import anki_vector; print('anki_vector import ok')"
```

## 5) Run baseline smoke
Run these via your MCP client/OpenClaw integration (see `docs/MCP_API_REFERENCE.md` for tool contracts):
1. `vector_status`
2. `vector_say`
3. `vector_drive_off_charger`
4. `vector_drive`
5. `vector_look`
6. `vector_head`
7. `vector_lift`

## 6) If something fails
See [Troubleshooting](SETUP.md#troubleshooting) and capture:
- command
- exact error text
- observed robot behavior

## Success Criteria
You should end with:
- successful status response
- audible speech
- observed movement
- valid camera image payload

If all true, your environment is ready for integration and expanded tool testing.
