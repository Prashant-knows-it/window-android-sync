import os
from flask import Flask, request, jsonify, send_from_directory
import pyperclip

app = Flask(__name__)

# Hardcode the directory where you want to store shared files
UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "HotspotShare")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML Web UI for easy phone access via browser
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hotspot Sync</title>
    <style>
        body { font-family: sans-serif; padding: 20px; max-width: 500px; margin: auto; }
        button, input[type="file"] { display: block; width: 100%; margin: 10px 0; padding: 10px; font-size: 16px; }
        textarea { width: 100%; height: 80px; font-size: 16px; }
        .box { border: 1px solid #ccc; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <h2>Hotspot Sync Hub</h2>
    
    <div class="box">
        <h3>Clipboard</h3>
        <textarea id="clipText" placeholder="Type or view clipboard here..."></textarea>
        <button onclick="pushClipboard()">Push to PC Clipboard</button>
        <button onclick="fetchClipboard()">Pull from PC Clipboard</button>
    </div>

    <div class="box">
        <h3>File Sharing</h3>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Upload File to PC</button>
        </form>
        <small><a href="/files">View / Download PC Files</a></small>
    </div>

    <script>
        async function fetchClipboard() {
            try {
                let res = await fetch('/clipboard');
                let data = await res.json();
                document.getElementById('clipText').value = data.text;
            } catch (e) {
                alert('Failed to fetch clipboard: ' + e);
            }
        }
        async function pushClipboard() {
            let text = document.getElementById('clipText').value;
            try {
                let res = await fetch('/clipboard', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text})
                });
                if (res.ok) {
                    alert('Pushed to PC!');
                } else {
                    alert('Server error while pushing.');
                }
            } catch (e) {
                alert('Failed to push clipboard: ' + e);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return INDEX_HTML

# --- CLIPBOARD ENDPOINTS ---
@app.route('/clipboard', methods=['GET'])
def get_clipboard():
    try:
        text = pyperclip.paste()
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clipboard', methods=['POST'])
def set_clipboard():
    data = request.get_json()
    if data and 'text' in data:
        try:
            pyperclip.copy(data['text'])
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"status": "error", "message": "Invalid payload"}), 400

# --- FILE SHARING ENDPOINTS ---
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return "File uploaded successfully! <br><br><a href='/'>Go back</a>"

@app.route('/files')
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    links = "".join([f'<li><a href="/files/{f}">{f}</a></li>' for f in files])
    return f"<h3>Available Files</h3><ul>{links}</ul><p><a href='/'>Back</a></p>"

@app.route('/files/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)