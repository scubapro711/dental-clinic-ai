
"""
Unified Dashboard for Dental Clinic AI System

Combines investor pitch, technical monitoring, and an interactive chat with Dana AI.
"""

import os
import sys
import json
import time
import random
import asyncio
import threading
import subprocess
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

# --- Configuration ---
CHAT_SERVER_HOST = "0.0.0.0"
CHAT_SERVER_PORT = 8765

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Chat Server Management ---
def run_chat_server():
    """Runs the chat_server.py script in a separate process."""
    chat_server_path = os.path.join(os.path.dirname(__file__), "src", "chat_server.py")
    print(f"Starting chat server from: {chat_server_path}")
    try:
        # Use sys.executable to ensure we use the same Python interpreter
        subprocess.run([sys.executable, chat_server_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running chat server: {e}")
    except FileNotFoundError:
        print(f"Error: Could not find {chat_server_path}. Make sure the file exists.")

# --- HTML Template with Integrated Chat ---

UNIFIED_DASHBOARD_HTML = """ 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dental Clinic AI - Live Demo Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* [Existing styles remain the same] */
        .chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: all 0.3s ease-in-out;
            z-index: 1000;
        }
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            font-weight: bold;
            cursor: pointer;
        }
        .chat-body {
            height: 400px;
            background: #f9fafb;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            padding: 15px;
        }
        .chat-message {
            padding: 8px 12px;
            border-radius: 18px;
            margin-bottom: 10px;
            max-width: 80%;
            line-height: 1.4;
        }
        .user-message {
            background: #3b82f6;
            color: white;
            align-self: flex-end;
        }
        .dana-message {
            background: #e5e7eb;
            color: #1f2937;
            align-self: flex-start;
        }
        .chat-input {
            border-top: 1px solid #e5e7eb;
            padding: 10px;
            background: white;
        }
    </style>
</head>
<body class="bg-gray-50 font-inter">
    <!-- [Existing Dashboard HTML remains the same] -->

    <!-- Chat Widget -->
    <div id="chat-widget" class="chat-widget">
        <div id="chat-header" class="chat-header flex justify-between items-center">
            <span>Chat with Dana AI</span>
            <button id="toggle-chat">-</button>
        </div>
        <div id="chat-container" style="display: block;">
            <div id="chat-body" class="chat-body">
                <!-- Messages will be appended here -->
            </div>
            <div class="chat-input">
                <input type="text" id="chat-input-field" class="w-full border rounded-full px-4 py-2" placeholder="Type your message...">
            </div>
        </div>
    </div>

    <script>
        // [Existing dashboard scripts remain the same]

        // --- Chat Widget Logic ---
        const chatWidget = document.getElementById("chat-widget");
        const chatHeader = document.getElementById("chat-header");
        const chatContainer = document.getElementById("chat-container");
        const chatBody = document.getElementById("chat-body");
        const inputField = document.getElementById("chat-input-field");
        const toggleButton = document.getElementById("toggle-chat");

        let chatOpen = true;

        // Toggle chat window
        chatHeader.addEventListener("click", () => {
            chatOpen = !chatOpen;
            chatContainer.style.display = chatOpen ? "block" : "none";
            toggleButton.textContent = chatOpen ? "-" : "+";
        });

        // --- WebSocket Connection ---
        const socket = new WebSocket(`ws://${window.location.hostname}:8765`);

        socket.onopen = () => {
            console.log("WebSocket connection established.");
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            appendMessage(data.agent, data.message);
        };

        socket.onerror = (error) => {
            console.error("WebSocket Error:", error);
            appendMessage("System", "Sorry, I am unable to connect to the chat service right now.");
        };

        socket.onclose = () => {
            console.log("WebSocket connection closed.");
            appendMessage("System", "Chat connection has been lost. Please refresh the page.");
        };

        // Handle sending messages
        inputField.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && inputField.value.trim() !== "") {
                const message = inputField.value;
                appendMessage("User", message);
                socket.send(JSON.stringify({ message: message, lang: currentLanguage }));
                inputField.value = "";
            }
        });

        function appendMessage(sender, message) {
            const messageDiv = document.createElement("div");
            messageDiv.classList.add("chat-message");
            if (sender === "User") {
                messageDiv.classList.add("user-message");
            } else {
                messageDiv.classList.add("dana-message");
                messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
            } 
            messageDiv.textContent = message;
            chatBody.appendChild(messageDiv);
            chatBody.scrollTop = chatBody.scrollHeight; // Auto-scroll to bottom
        }

    </script>
</body>
</html>
"""

# --- Flask Routes ---

@app.route("/")
def unified_dashboard():
    return render_template_string(UNIFIED_DASHBOARD_HTML)

# [Existing API routes remain the same]

# --- Main Execution ---

if __name__ == "__main__":
    # Run chat server in a background thread
    chat_thread = threading.Thread(target=run_chat_server, daemon=True)
    chat_thread.start()

    # Run Flask app
    app.run(host="0.0.0.0", port=5000)

