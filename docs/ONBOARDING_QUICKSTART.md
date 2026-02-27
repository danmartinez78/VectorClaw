# Onboarding Quickstart (5-Minute Path)

## Goal
Get a first-time user to a working VectorClaw MCP setup quickly and safely.

## Prerequisites
- Wire-Pod running and robot reachable
- Python 3.11+
- OpenClaw environment ready
- Vector serial available

## 1) Install SDK
```bash
pip install git+https://github.com/kercre123/wirepod-vector-python-sdk.git
```

## 2) Set required env
```bash
export VECTOR_SERIAL=<your-vector-serial>
# optional:
export VECTOR_HOST=<robot-ip-or-host>
```

## 3) Verify import
```bash
python -c "import anki_vector; print('anki_vector import ok')"
```

## 4) Run baseline smoke
Run tools in this order and verify physical behavior where applicable:
1. `vector_status`
2. `vector_say`
3. `vector_drive_off_charger`
4. `vector_drive`
5. `vector_look`
6. `vector_head`
7. `vector_lift`

## 5) If something fails
See `docs/TROUBLESHOOTING.md` and capture:
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
