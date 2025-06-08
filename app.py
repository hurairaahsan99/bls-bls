from flask import Flask, render_template_string, jsonify
import threading
import play2
import logging
from datetime import datetime
import queue
import os

app = Flask(__name__)

# Queue to store log messages
log_queue = queue.Queue()
checker_thread = None
is_running = False

# Custom log handler to capture logs
class QueueHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage()
        }
        log_queue.put(log_entry)

# Configure logging
logging.getLogger().addHandler(QueueHandler())

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>BLS Appointment Checker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .status {
            text-align: center;
            margin: 20px 0;
            padding: 10px;
            border-radius: 4px;
        }
        .running {
            background-color: #d4edda;
            color: #155724;
        }
        .stopped {
            background-color: #f8d7da;
            color: #721c24;
        }
        .log-container {
            height: 500px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 4px;
            background-color: #f8f9fa;
        }
        .log-entry {
            margin: 5px 0;
            padding: 5px;
            border-bottom: 1px solid #eee;
        }
        .log-entry.INFO { color: #0c5460; }
        .log-entry.WARNING { color: #856404; }
        .log-entry.ERROR { color: #721c24; }
        .button {
            display: inline-block;
            padding: 10px 20px;
            margin: 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            color: white;
            text-decoration: none;
            text-align: center;
        }
        .start-button { background-color: #28a745; }
        .stop-button { background-color: #dc3545; }
        .button:hover { opacity: 0.9; }
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        .button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
    <script>
        let isRunning = false;

        function updateLogs() {
            fetch('/logs')
                .then(response => response.json())
                .then(data => {
                    const logContainer = document.getElementById('logs');
                    logContainer.innerHTML = '';
                    data.forEach(log => {
                        const entry = document.createElement('div');
                        entry.className = `log-entry ${log.level}`;
                        entry.innerHTML = `<h3>[${log.timestamp}] ${log.level}: ${log.message}</h3>`;
                        logContainer.appendChild(entry);
                    });
                    logContainer.scrollTop = logContainer.scrollHeight;
                });
        }

        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    isRunning = data.running;
                    const statusDiv = document.getElementById('status');
                    const startButton = document.getElementById('startButton');
                    const stopButton = document.getElementById('stopButton');

                    statusDiv.className = `status ${isRunning ? 'running' : 'stopped'}`;
                    statusDiv.textContent = isRunning ? 'Checker is running' : 'Checker is stopped';

                    startButton.disabled = isRunning;
                    stopButton.disabled = !isRunning;
                });
        }

        function startChecker() {
            if (!isRunning) {
                fetch('/start', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        updateStatus();
                    });
            }
        }

        function stopChecker() {
            if (isRunning) {
                fetch('/stop', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        updateStatus();
                    });
            }
        }

        // Update logs and status every 5 seconds
        setInterval(updateLogs, 5000);
        setInterval(updateStatus, 5000);

        // Initial update when page loads
        window.onload = function() {
            updateLogs();
            updateStatus();
        };
    </script>
</head>
<body>
    <div class="container">
        <h1>BLS Appointment Checker</h1>
        <div id="status" class="status">Checking status...</div>
        <div class="controls">
            <button id="startButton" onclick="startChecker()" class="button start-button">Start Checker</button>
            <button id="stopButton" onclick="stopChecker()" class="button stop-button">Stop Checker</button>
        </div>
        <div id="logs" class="log-container">
            Loading logs...
        </div>
    </div>
</body>
</html>
"""

def run_checker():
    global is_running
    is_running = True
    play2.main()

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/logs')
def get_logs():
    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get())
    return jsonify(logs)

@app.route('/status')
def get_status():
    return jsonify({'running': is_running})

@app.route('/start', methods=['POST'])
def start_checker():
    global checker_thread, is_running
    if not is_running:
        checker_thread = threading.Thread(target=run_checker)
        checker_thread.daemon = True
        checker_thread.start()
    return jsonify({'status': 'started'})

@app.route('/stop', methods=['POST'])
def stop_checker():
    global is_running
    is_running = False
    return jsonify({'status': 'stopped'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))