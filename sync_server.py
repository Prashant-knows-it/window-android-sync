import json, os, socket, urllib.error, urllib.request
from flask import Flask, jsonify, render_template_string, request, send_from_directory
import pyperclip

app = Flask(__name__)

# --- CONFIGURATION ---
GIST_ID = "8865a686ebec4a9904a2015c0c8c0ee7"
GITHUB_TOKEN = "<Put-Your_Github_Token_Here"  # Replace with your actual ghp_... token
PORT = 5000
# ---------------------

UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "HotspotShare")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hotspot Hub</title>
    <style>
        body { font-family: sans-serif; padding: 20px; max-width: 500px; margin: auto; background: #f9f9f9; }
        button, input[type="file"] { display: block; width: 100%; margin: 10px 0; padding: 12px; font-size: 16px; cursor: pointer; border-radius: 6px; border: 1px solid #ccc; background: white; transition: 0.2s; }
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
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload File to PC</button>
        </form>
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
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/clipboard', methods=['GET'])
def get_clipboard():
    try: return jsonify({"text": pyperclip.paste()})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/clipboard', methods=['POST'])
def set_clipboard():
    data = request.get_json()
    if data and 'text' in data:
        pyperclip.copy(data['text'])
        return jsonify({"status": "success"})
    return jsonify({"error": "Invalid payload"}), 400

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or file.filename == '': return "No file selected", 400
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return "<h3>✅ File Uploaded!</h3><br><a href='/'>← Go Back</a>"

@app.route('/files')
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    links = "".join([f'<li><a href="/files/{f}">{f}</a></li>' for f in files])
    return f"<h3>Available Files</h3><ul>{links}</ul><br><a href='/'>← Back to Hub</a>"

@app.route('/files/<filename>')
def download_file(filename):
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