# Hotspot Sync Hub

A simple tool to share clipboard text and files between your Android phone and Windows PC over the same Wi-Fi network.

## What it does
- Send text to your PC clipboard from your phone
- Pull text from your PC clipboard to your phone
- Upload files from your phone to your PC
- Download files from your PC in the browser

## Requirements
- Python 3.9+
- A phone and PC on the same Wi-Fi network

## Run it on Windows
1. Open Command Prompt or PowerShell in this folder.
2. Install the required packages:
   ```bash
   pip install Flask pyperclip
   ```
   You can also use:
   ```bash
   py -m pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   py sync_server.py
   ```
4. The app will run at:
   ```text
   http://0.0.0.0:5000
   ```

## Use it from your Android phone
1. On your Windows PC, open Command Prompt and type:
   ```bash
   ipconfig
   ```
2. Find your Wi-Fi IPv4 Address. It will look something like:
   ```text
   192.168.1.20
   ```
3. On your Android phone, open Chrome and go to:
   ```text
   http://<YOUR_PC_IP>:5000
   ```
   Example:
   ```text
   http://192.168.1.20:5000
   ```
4. If Windows asks to allow network access, allow it.

## Stop the server
Press Ctrl + C in the terminal.
