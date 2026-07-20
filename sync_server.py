import json, os, socket, urllib.error, urllib.request
from flask import Flask, jsonify, make_response, redirect, render_template_string, request, send_from_directory
import pyperclip

app = Flask(__name__)

# --- CONFIGURATION ---
SECRET_TOKEN = "0000"  # Your clean 4-digit PIN
GIST_ID = "8865a686ebec4a9904a2015c0c8c0ee7"
GITHUB_TOKEN = "YOUR_GITHUB_PAT_HERE"  # Replace with your actual ghp_... token
PORT = 5000
# ---------------------

UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "HotspotShare")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def is_authenticated():
    return request.cookies.get('hub_auth') == SECRET_TOKEN

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hub Login</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 80vh; background: #f9f9f9; margin: 0; }
        .box { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center; width: 260px; border: 1px solid #e0e0e0; }
        input { width: 100%; padding: 12px; margin: 15px 0; font-size: 20px; text-align: center; letter-spacing: 6px; box-sizing: border-box; border-radius: 6px; border: 1px solid #ccc; }
        button { width: 100%; padding: 12px; font-size: 16px; cursor: pointer; border-radius: 6px; border: 1px solid #ccc; background: #fff; transition: 0.2s; }
        button:active { transform: scale(0.98); }
    </style>
</head>
<body>
    <div class="box">
        <h3>Enter PIN</h3>
        <form method="POST" action="/">
            <input type="password" name="token" maxlength="10" autofocus required>
            <button type="submit">Unlock Hub</button>
        </form>
    </div>
</body>
</html>
"""

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hotspot Hub</title>
    <style>
        body { font-family: sans-serif; padding: 20px; max-width: 500px; margin: auto; background: #f9f9f9; }
        button { display: block; width: 100%; margin: 10px 0; padding: 12px; font-size: 16px; cursor: pointer; border-radius: 6px; border: 1px solid #ccc; background: white; transition: 0.2s; }
        button:active { transform: scale(0.98); }
        textarea { width: 100%; height: 90px; font-size: 16px; padding: 8px; box-sizing: border-box; border-radius: 6px; border: 1px solid #ccc; }
        .box { border: 1px solid #e0e0e0; padding: 15px; margin-bottom: 15px; border-radius: 8px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .success { background-color: #d4edda !important; border-color: #c3e6cb !important; color: #155724 !important; }
    </style>
</head>
<body>
    <h2>Hotspot Sync Hub</h2>
    <div class="box">
        <h3>Clipboard</h3>
        <textarea id="clipText" placeholder="Type or paste text here..."></textarea>
        <button id="btnPush" onclick="pushClipboard()">Push to PC Clipboard</button>
        <button id="btnPull" onclick="fetchClipboard()">Pull from PC Clipboard</button>
    </div>
    <div class="box">
        <h3>File Sharing</h3>
        <input type="file" id="fileInput" style="display:none" onchange="onFileSelected()">
        <button id="btnSelect" onclick="document.getElementById('fileInput').click()">📁 Select File to Upload</button>
        <button id="btnUpload" onclick="uploadFile()" style="display:none; font-weight: bold; background: #eef8ff; border-color: #b8daff;">⬆️ Push File to PC</button>
        <small><a href="/files">View / Download PC Files</a></small>
    </div>
    <script>
        function flashButton(btnId, text) {
            let btn = document.getElementById(btnId);
            let originalText = btn.innerText;
            btn.innerText = text;
            btn.classList.add('success');
            setTimeout(() => {
                btn.innerText = originalText;
                btn.classList.remove('success');
            }, 1500);
        }

        async function fetchClipboard() {
            try {
                let res = await fetch('/clipboard');
                let data = await res.json();
                if (data.error) throw new Error();
                document.getElementById('clipText').value = data.text;
                flashButton('btnPull', '✅ Pulled from PC!');
            } catch (e) { flashButton('btnPull', '❌ Pull Failed'); }
        }

        async function pushClipboard() {
            let text = document.getElementById('clipText').value;
            try {
                let res = await fetch('/clipboard', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text})
                });
                if (res.ok) flashButton('btnPush', '✅ Pushed to PC!');
                else throw new Error();
            } catch (e) { flashButton('btnPush', '❌ Push Failed'); }
        }

        function onFileSelected() {
            let file = document.getElementById('fileInput').files[0];
            if (file) {
                document.getElementById('btnSelect').innerText = "📄 " + file.name;
                document.getElementById('btnUpload').style.display = "block";
            }
        }

        async function uploadFile() {
            let fileInput = document.getElementById('fileInput');
            let file = fileInput.files[0];
            if (!file) return;

            let formData = new FormData();
            formData.append("file", file);

            let btn = document.getElementById('btnUpload');
            btn.innerText = "⏳ Uploading...";

            try {
                let res = await fetch('/upload', { method: 'POST', body: formData });
                if (res.ok) {
                    flashButton('btnUpload', '✅ Upload Complete!');
                    setTimeout(() => {
                        document.getElementById('btnSelect').innerText = "📁 Select File to Upload";
                        btn.style.display = "none";
                        fileInput.value = "";
                    }, 1500);
                } else throw new Error();
            } catch (e) {
                flashButton('btnUpload', '❌ Upload Failed');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and request.form.get('token') == SECRET_TOKEN:
        resp = make_response(redirect('/'))
        resp.set_cookie('hub_auth', SECRET_TOKEN, max_age=31536000, httponly=True, samesite='Lax')
        return resp
        
    if is_authenticated():
        return render_template_string(INDEX_HTML)
        
    return render_template_string(LOGIN_HTML)

@app.route('/clipboard', methods=['GET'])
def get_clipboard():
    if not is_authenticated(): return jsonify({"error": "Unauthorized"}), 403
    try: return jsonify({"text": pyperclip.paste()})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/clipboard', methods=['POST'])
def set_clipboard():
    if not is_authenticated(): return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    if data and 'text' in data:
        pyperclip.copy(data['text'])
        return jsonify({"status": "success"})
    return jsonify({"error": "Invalid payload"}), 400

@app.route('/upload', methods=['POST'])
def upload_file():
    if not is_authenticated(): return jsonify({"error": "Unauthorized"}), 403
    file = request.files.get('file')
    if not file or file.filename == '': return jsonify({"error": "No file selected"}), 400
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return jsonify({"status": "success"})

@app.route('/files')
def list_files():
    if not is_authenticated(): return "Unauthorized", 403
    files = os.listdir(UPLOAD_FOLDER)
    links = "".join([f'<li><a href="/files/{f}">{f}</a></li>' for f in files])
    return f"<h3>Available Files</h3><ul>{links}</ul><br><a href='/'>← Back to Hub</a>"

@app.route('/files/<filename>')
def download_file(filename):
    if not is_authenticated(): return "Unauthorized", 403
    return send_from_directory(UPLOAD_FOLDER, filename)

def init_network():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception: ip = '127.0.0.1'
    finally: s.close()
    
    payload = json.dumps({
        "files": {
            "ip.json": {
                "content": json.dumps({"ip": ip})
            }
        }
    }).encode('utf-8')

    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'Python-Beacon',
        'Content-Type': 'application/json'
    }

    req = urllib.request.Request(url, data=payload, headers=headers, method='PATCH')
    try: 
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"[*] Successfully updated GitHub Gist beacon with IP: {ip}")
    except urllib.error.HTTPError as e:
        print(f"[!] Beacon update failed (HTTP {e.code}): Check your GITHUB_TOKEN and permissions.")
    except Exception as e: 
        print(f"[!] Beacon update failed: {e}")
        
    return ip

if __name__ == '__main__':
    ip = init_network()
    print(f"\n[*] Server running -> http://{ip}:{PORT}\n")
    app.run(host='0.0.0.0', port=PORT, debug=False)