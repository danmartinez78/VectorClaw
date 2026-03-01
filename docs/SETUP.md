# Vector Setup Guide for VectorClaw

**Goal:** Get your Vector robot set up and ready for OpenClaw integration testing.

---

## Prerequisites

- [ ] Vector robot (1.0 or 2.0, production or OSKR/unlocked)
- [ ] USB-C cable (included with Vector)
- [ ] 5V/2A USB power adapter (or powered USB port)
- [ ] WiFi network — **MUST be 2.4 GHz** (Vector doesn't support 5 GHz!)
- [ ] Computer with Bluetooth (for initial setup)
- [ ] Chrome browser (required for BLE setup)
- [ ] Python 3.11+ on your development machine

---

## Overview: Two Setup Paths

| Path | Pros | Cons | Recommended For |
|------|------|------|-----------------|
| **DDL Cloud** | Easier initial setup | Requires DDL account, servers may be deprecated/flaky | Quick testing if servers work |
| **Wire-Pod (Self-Hosted)** | Full control, no cloud dependency, works even if DDL shuts down | More setup steps | **Production use, long-term stability** |

**We recommend Wire-Pod** for reliable, cloud-independent operation. This guide covers both options.

---

## Path 1: Wire-Pod Setup (Recommended)

Wire-Pod is free, open-source server software that replaces Digital Dream Labs' cloud services. It enables full Vector functionality without relying on external servers.

### 1.1 Install Wire-Pod

Wire-Pod runs on Linux, macOS, Windows, and Android. Choose your platform:

#### Linux (Debian/Ubuntu/Raspberry Pi OS)

```bash
# Download the latest .deb package from releases
# https://github.com/kercre123/WirePod/releases/latest

# Check your architecture
uname -m
# x86_64 → use amd64
# armv7l → use armhf
# aarch64/arm64 → use arm64 (Pi 5) or armhf (Pi 4)

# Install
cd ~/Downloads
sudo apt update
sudo apt install -y ./wirepod_<arch>-<version>.deb
```

#### Linux (Source Install)

```bash
cd ~
git clone https://github.com/kercre123/wire-pod --depth=1
cd wire-pod
sudo STT=vosk ./setup.sh

# Start wire-pod
sudo ./chipper/start.sh
```

#### macOS

```bash
# Download WirePod-<version>.dmg from releases
# https://github.com/kercre123/WirePod/releases/latest

# Drag to Applications, run it
# Allow "unidentified developer" in Security settings
```

#### Windows

```bash
# Download WirePodInstaller-<version>.exe from releases
# https://github.com/kercre123/WirePod/releases/latest

# Run installer, follow prompts
# May need to click "More Info" → "Run Anyway" for SmartScreen
```

#### Docker

```bash
# Set up mDNS alias for escapepod.local
sudo apt install avahi-utils

# Create systemd service for mDNS alias
sudo cat > /etc/systemd/system/avahi-alias@.service << 'EOF'
[Unit]
Description=Publish %I as alias for %H.local via mdns

[Service]
Type=simple
ExecStart=/bin/bash -c "/usr/bin/avahi-publish -a -R %I $(avahi-resolve -4 -n %H.local | cut -f 2)"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now avahi-alias@escapepod.local.service

# Run wire-pod via Docker
docker compose up -d -f https://raw.githubusercontent.com/kercre123/wire-pod/main/compose.yaml
```

### 1.2 Configure Wire-Pod

1. **Open the web interface:**
   - Wire-Pod will display a URL like `http://192.168.1.xxx:8080`
   - Open that URL in a browser on the same network

2. **Complete initial setup:**
   - Follow the web interface prompts
   - Choose your speech-to-text engine (Vosk is recommended for offline)
   - Configure language settings

3. **Enable daemon mode (optional but recommended):**
   ```bash
   sudo ~/wire-pod/setup.sh daemon-enable
   sudo systemctl start wire-pod
   ```

### 1.3 Prepare Vector for Wire-Pod

**For production bots (not OSKR/unlocked):**

1. **Put Vector in recovery mode:**
   - Place Vector on charger
   - Hold backpack button for ~15 seconds until lights go off
   - Keep holding until lights come back on
   - Vector will show `anki.com/v` or `ddl.io/v` screen

2. **Apply Wire-Pod firmware:**
   - Open Chrome on a Bluetooth-enabled device
   - Go to https://wpsetup.keriganc.com/
   - Follow the prompts to pair with `vector-wirepod-setup`
   - The special firmware (with `ep` suffix) will be installed

   **Chrome BLE troubleshooting:**
   - If you see a Chrome error, enable `chrome://flags` → "Enable experimental web platform features"
   - On Linux, keep Bluetooth settings open and discovering during pairing

3. **Clear user data (IMPORTANT):**
   - Place Vector on charger
   - Double-press backpack button
   - Lift lift up, then down
   - Remove from charger
   - Twist wheel to select "RESET" or "CLEAR USER DATA"
   - Lift lift up, then down
   - Twist wheel to "CONFIRM"
   - Lift lift up, then down

   **Skipping this step causes weird behavior!**

**For OSKR/dev-unlocked bots:**
- Skip the firmware steps above
- Wire-Pod will work directly

### 1.4 Authenticate Vector with Wire-Pod

1. **Open Wire-Pod web interface** → "Bot Setup"

2. **Follow "Authenticate" section:**
   - You'll be directed to the BLE setup page (or use Wire-Pod's built-in BLE)
   - Click "ACTIVATE" or "AUTHENTICATE"
   - If it errors, wait 20 seconds and try again

3. **Configure bot settings:**
   - Enter desired name, location, etc.
   - Click "SAVE SETTINGS"

4. **Verify success:**
   - You should see "Vector setup is complete!"
   - Bot should appear in "Bot Settings" section

### 1.5 Configure Vector for Your WiFi

After Wire-Pod authentication, Vector needs to connect to your local WiFi:

1. **If Vector isn't on WiFi yet:**
   - Put Vector in setup mode (double-press backpack)
   - Use the Wire-Pod interface or `wpsetup.keriganc.com` to configure WiFi

2. **Verify connection:**
   ```bash
   # Find Vector on your network
   nmap -sP 192.168.1.0/24 | grep -i vector
   # or
   arp -a | grep -i vector
   ```

3. **Note the IP address:** You'll need this for SDK configuration.

---

## Path 2: DDL Cloud Setup (Alternative)

If you want to try the official Digital Dream Labs cloud first:

### 2.1 Download Vector App

- **iOS:** App Store → "Vector by Anki"
- **Android:** Play Store → "Vector by Anki"

### 2.2 Create DDL Account

1. Open the app
2. Create account or sign in with existing Anki/DDL credentials
3. The app may prompt for email verification

### 2.3 Pair and Configure Vector

1. **Power on Vector** and place on flat surface
2. **Put Vector in pairing mode:** Double-press backpack button
3. **Follow app instructions:**
   - Connect to Vector's WiFi hotspot
   - Enter your home WiFi credentials
   - Wait for firmware update

### 2.4 Note Serial and IP

- Serial: Found in app under Robot Info, or on sticker under Vector
- IP: Check your router's DHCP client list

**If DDL servers are down or reject your credentials:**
→ Fall back to Wire-Pod (Path 1)

---

## SDK Authentication

Once Vector is on your WiFi and Wire-Pod is running, configure the Python SDK.

### Option A: Wire-Pod SDK (Canonical — Recommended)

`wirepod_vector_sdk` is the officially supported SDK distribution for VectorClaw. It
installs under the `anki_vector` Python namespace, works with Wire-Pod out of the box,
and is maintained for modern Python runtimes.

```bash
# Create venv for Vector work
python3 -m venv ~/.venv/vector
source ~/.venv/vector/bin/activate

# Install SDK (exposes the anki_vector Python module)
pip install wirepod_vector_sdk

# Run configuration wizard
python -m anki_vector.configure
```

**When prompted:**
- Serial number: Enter your Vector's serial (printed on the underside of the robot)
- The wizard will download the cert from your running Wire-Pod instance automatically

### Option B: Legacy anki_vector package (Best-Effort Only)

> ⚠️ **Legacy / best-effort support only.** The standalone `anki_vector` package
> requires working DDL cloud servers and is brittle on modern Python runtimes.
> Use `wirepod_vector_sdk` (Option A) instead whenever possible.

```bash
pip install "vectorclaw-mcp[legacy]"   # installs legacy anki_vector alongside vectorclaw-mcp

# Run configuration wizard
python -m anki_vector.configure
```

### Option C: Manual Config File

If the SDK configuration wizard fails, create the config file manually:

```bash
mkdir -p ~/.anki_vector

cat > ~/.anki_vector/<serial>.conf << 'EOF'
[009050ae]
cert = /home/youruser/.anki_vector/009050ae.cert
ip = 192.168.1.xxx
name = Vector-009050ae
serial = 009050ae
EOF
```

**For Wire-Pod, certificates are generated during authentication.** Check the Wire-Pod data directory for cert files.

### Option D: Extract Cert from Wire-Pod

Wire-Pod stores certificates after bot authentication:

```bash
# Wire-Pod certs are typically in:
# Linux: ~/wire-pod/chipper/certs/
# macOS: /Applications/WirePod.app/Contents/Resources/certs/
# Windows: C:\Users\<user>\AppData\Local\WirePod\certs\

# Copy to SDK location
cp ~/wire-pod/chipper/certs/<serial>.cert ~/.anki_vector/
```

---

## Test SDK Connection

```bash
# Activate venv
source ~/.venv/vector/bin/activate

# Test connection (anki_vector module, installed via wirepod_vector_sdk)
python -c "
import anki_vector
robot = anki_vector.Robot(serial='YOUR_SERIAL')
robot.connect()
robot.behavior.say_text('Hello, I am Vector!')
print('Connection successful!')
robot.disconnect()
"
```

**Expected:** Vector says "Hello, I am Vector!" and script prints success.

---

## VectorClaw MCP Setup

### Install VectorClaw

```bash
# From PyPI (once published)
pip install vectorclaw-mcp

# Or from source
cd ~/projects/VectorClaw
pip install -e .
```

### Set Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc
export VECTOR_SERIAL="009050ae"
export VECTOR_HOST="192.168.1.xxx"  # Optional, auto-discovered if omitted
```

### Configure mcporter (OpenClaw)

Edit `~/.openclaw/workspace/config/mcporter.json`:

```json
{
  "mcpServers": {
    "vectorclaw": {
      "command": "uvx",
      "args": ["vectorclaw-mcp"],
      "env": {
        "VECTOR_SERIAL": "009050ae"
      }
    }
  }
}
```

**Restart the OpenClaw gateway** after updating config.

### Test MCP Server

```bash
# Manual test
VECTOR_SERIAL=009050ae vectorclaw-mcp

# The server will start and listen on stdio for MCP messages
```

---

## Integration Testing with OpenClaw

Once everything is configured:

### Basic Test

```
You: "Hey Tachi, make Vector say 'OpenClaw is online'"
```

Tachi should call `vector_say` and Vector should speak.

### Test All Tools

| Tool | Test Command |
|------|--------------|
| `vector_say` | "Make Vector say 'Integration test successful'" |
| `vector_animate` | "Make Vector do a happy animation" |
| `vector_drive` | "Make Vector drive forward 100 millimeters" |
| `vector_look` | "Take a picture with Vector's camera" |
| `vector_face` | "Display a smiley face on Vector's screen" |
| `vector_pose` | "Where is Vector right now?" |
| `vector_cube` | "Make Vector dock with its cube" |
| `vector_status` | "What's Vector's battery level?" |

---

## Troubleshooting

### "Unable to connect to robot"

1. **Check WiFi:** Vector must be on same network as your computer
2. **Check IP:** Ping the IP address
3. **Check power:** Vector must be awake (not on charger, not sleeping)
4. **Wake Vector:** Tap backpack button
5. **Check SDK config:** Verify `~/.anki_vector/<serial>.conf` exists and has correct IP

### "Authentication failed"

1. **Wire-Pod not running:** Start it with `sudo systemctl start wire-pod`
2. **Wrong server:** SDK may be trying to reach DDL cloud — check config
3. **Missing cert:** Ensure certificate file exists in `~/.anki_vector/`

### "BLE pairing fails"

1. **Use Chrome:** Other browsers may not support Web BLE
2. **Enable experimental flags:** `chrome://flags` → "Enable experimental web platform features"
3. **Keep Bluetooth settings open:** On Linux, have BT settings discovering during pairing
4. **Distance:** Keep Vector close to the Bluetooth adapter

### "Robot not responding to SDK commands"

1. **Wake Vector:** Tap backpack button
2. **Check if charging:** Vector won't move while on charger
3. **Check battery:** Low battery limits behavior
4. **Reboot Vector:** Hold backpack button 5+ seconds

### "Camera image is black"

1. Vector may be in a dark area
2. Call `vector_look` again — camera may need re-initialization
3. Check if Vector's eyes are covered (he disables camera)

### "Cube not found"

1. Power on the cube (press button, should light up)
2. Place cube near Vector and wait 30 seconds for pairing
3. Wire-Pod may need to be configured for cube support

### "Wire-Pod shows 'not running' error"

1. Run authentication twice — first attempt may fail
2. Check Wire-Pod logs: `journalctl -u wire-pod -f`
3. Restart Wire-Pod: `sudo systemctl restart wire-pod`

---

## Quick Reference

| Info | Your Value |
|------|------------|
| Serial number | `_______________________` |
| IP address | `_______________________` |
| WiFi network (2.4 GHz) | `_______________________` |
| Wire-Pod URL | `http://______________:8080` |
| SDK config location | `~/.anki_vector/` |

---

## Useful Commands

```bash
# Find Vector on network
nmap -sP 192.168.1.0/24 | grep -B2 -i vector

# Test SDK connection (anki_vector module, installed via wirepod_vector_sdk)
python -c "import anki_vector; r=anki_vector.Robot('SERIAL'); r.connect(); print('OK'); r.disconnect()"

# Start Wire-Pod
sudo systemctl start wire-pod

# View Wire-Pod logs
journalctl -u wire-pod -f

# Run VectorClaw MCP manually
VECTOR_SERIAL=009050ae vectorclaw-mcp

# View SDK config
cat ~/.anki_vector/*.conf
```

---

## Resources

- [VectorClaw Repository](https://github.com/danmartinez78/VectorClaw)
- [Wire-Pod Vector SDK (wirepod_vector_sdk)](https://github.com/kercre123/vector-python-sdk)
- [Wire-Pod GitHub](https://github.com/kercre123/wire-pod)
- [Wire-Pod Wiki](https://github.com/kercre123/wire-pod/wiki)
- [Wire-Pod Setup Tool](https://wpsetup.keriganc.com/)
- [Vector Python SDK (legacy)](https://github.com/anki/vector-python-sdk)
- [Vector SDK Docs (legacy)](https://developer.anki.com/vector/docs/index.html)
- [awesome-anki-vector](https://github.com/open-ai-robot/awesome-anki-vector)

---

*Created for VectorClaw integration testing - 2026-02-26*
