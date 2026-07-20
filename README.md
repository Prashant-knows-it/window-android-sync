```markdown
# 🔄 Hotspot Sync Hub

A lean, self-healing, bi-directional clipboard and file transfer bridge between Windows and Android over a local Wi-Fi hotspot. 

Designed to bypass cloud storage latency, internet dependency, and the friction of manually tracking dynamic local IP addresses.

---

## ✨ Features

* **📋 Instant Clipboard Sync:** Push text to your PC's clipboard or pull the PC's current clipboard text directly to your phone in real time.
* **📁 Asynchronous File Transfer:** Smooth, zero-reload AJAX file uploads from mobile directly to your Windows Desktop, alongside instant file downloading.
* **🛰️ Auto-Healing IP Beacon:** A background daemon monitors network routing table changes every 30 seconds and patches your current local IP address to an unlisted GitHub Gist automatically.
* **🔒 Zero-Cloud Exposure Security:** A sleek 4-digit PIN authentication lock lives strictly on the local Windows PC. Your public GitHub Pages repository contains **zero secrets, tokens, or passwords**.
* **👻 Silent Background Execution:** Configured to run invisibly on Windows Startup via `pythonw.exe`—no lingering terminal windows or system tray clutter.
* **🚫 Zero Mixed-Content Warnings:** Uses clean top-level GET redirects (`location.replace`) and explicit `SameSite=Lax` cookies to prevent modern mobile browser security blocks.

---

## 🏗️ Architecture Overview

```text
[ Android Phone ] 
       │
       ▼ (1. Reads latest local IP via public API)
[ GitHub Pages (Static Frontend) ] ───► [ GitHub Gist (IP Beacon) ]
       │                                         ▲
       │ (2. Seamless Top-Level Redirect)        │ (3. Background Watchdog
       ▼                                         │     updates IP on network change)
[ Local Windows PC (Flask Server on 0.0.0.0:5000) ]

```

1. **The Beacon:** When your PC connects to a hotspot, `sync_server.pyw` detects its local RFC 1918 IP address (e.g., `192.168.43.15`) and silently updates an unlisted GitHub Gist using a Personal Access Token.
2. **The Lookup:** When you open your static GitHub Pages site on your phone, it fetches the latest IP from the Gist and immediately redirects your browser to the PC's local server.
3. **The Lock:** If unauthenticated, the PC serves a clean PIN pad. Upon typing the correct PIN, the PC drops an HTTP-only cookie valid for 365 days and unlocks the hub.

---

## 🚀 Setup & Installation

### Prerequisites

* **Python 3.x** installed on Windows.
* Required Python libraries:
```bash
pip install flask pyperclip

```


* A **GitHub Account** (for Pages hosting and Gist API creation).

---

### Step 1: Create the IP Beacon (GitHub Gist)

1. Go to [gist.github.com](https://gist.github.com/) and create a **Secret Gist**.
2. Name the file `ip.json` and add initial dummy content:
```json
{ "ip": "127.0.0.1" }

```


3. Click **Create secret gist** and copy the **Gist ID** from the URL:
`https://gist.github.com/username/`<**`YOUR_GIST_ID`**>

---

### Step 2: Generate a Personal Access Token (PAT)

1. Go to **GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)**.
2. Click **Generate new token (classic)**.
3. Check the box for **`gist`** (Create gists).
4. Generate and copy your token (`ghp_xxxxxxxxxxxx`).

---

### Step 3: Configure the Windows Backend (`sync_server.pyw`)

Open `sync_server.pyw` and update the configuration block at the top:

```python
# --- CONFIGURATION ---
SECRET_TOKEN = "0000"  # Set your desired 4-digit PIN
GIST_ID = "YOUR_GIST_ID"
GITHUB_TOKEN = "YOUR_GITHUB_PAT_HERE"
PORT = 5000
# ---------------------

```

---

### Step 4: Configure the Static Frontend (`index.html`)

Open `index.html` (hosted on your GitHub Pages repository) and insert your Gist ID:

```javascript
const GIST_ID = "YOUR_GIST_ID";
const PORT = "5000";

```

*Deploy this file to your GitHub Pages repository. Notice there are no tokens or passwords stored here.*

---

### Step 5: Configure Windows Silent Startup

To make the server run automatically in the background without opening a command prompt:

1. Press `Win + R`, type `shell:startup`, and press **Enter**.
2. Right-click inside the Startup folder → **New → Shortcut**.
3. Point the target to `pythonw.exe` followed by the full path to your script:
```text
pythonw.exe "E:\path\to\your\sync_server.pyw"

```


4. Name it **HotspotSync** and save.
5. Double-click the shortcut once to launch it immediately.

---

## 📱 Usage

1. Turn on your mobile Wi-Fi hotspot and connect your PC to it.
2. Open your deployed **GitHub Pages URL** on your Android browser.
3. The page will automatically resolve your PC's current local IP and redirect you.
4. Type your 4-digit PIN on the clean login screen.
5. Your browser is now authenticated for **1 full year**—instant clipboard syncing and AJAX file uploads are ready to use.

---

## 🛑 Process Management

Because the server runs silently via `pythonw.exe`, it has no taskbar icon. To stop or restart the server manually:

1. Open **Task Manager** (`Ctrl + Shift + Esc`).
2. Look under **Background processes** for **Python**.
3. Right-click and select **End Task**.

---

## 🛡️ Security Note

This application binds to `0.0.0.0:5000`, meaning it is accessible to any device connected to your local network. **Do not run this server on unsecured public Wi-Fi networks (e.g., cafes, airports, or campus networks).** It is strictly designed for personal, private WPA3 mobile hotspots or secure home LANs where your Wi-Fi password acts as the primary firewall.

```

```
