import requests
import json
import threading
import random
import time
from typing import List
from colorama import init, Fore, Style

def load_chat_history():
    """Loads chat history from chat_history.json, or initializes an empty list if the file doesn't exist, is empty, or contains invalid JSON."""
    try:
        with open("chat_history.json", "r") as f:
            data = f.read()
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return []
    except FileNotFoundError:
        return []

def save_chat_history(messages):
    """Saves chat history to chat_history.json, ensuring only new messages are appended."""
    try:
        with open("chat_history.json", "r+") as f:
            data = f.read()
            if not data:  # If the file is empty, write the entire messages list
                f.seek(0)  # Move the file pointer to the beginning
                json.dump(messages, f)
            else:
                existing_data = json.loads(data)
                existing_data.extend(messages)  # Append new messages to existing data
                f.seek(0)  # Move the file pointer to the beginning
                json.dump(existing_data, f)
    except FileNotFoundError:
        with open("chat_history.json", "w") as f:
            json.dump(messages, f)

messages = load_chat_history()  # Load chat history from file
def Type_gpt(message, system_message="You are a helpful assistant.", model="gpt-4o"):
    global messages
    url = "https://chat.typegpt.net/api/openai/v1/chat/completions"
    
    headers = {
        'authority': 'chat.typegpt.net',
        'accept': 'application/json, text/event-stream',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://chat.typegpt.net',
        'referer': 'https://chat.typegpt.net/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    model_list = [
        "claude-3-5-sonnet-20240620",
        "gpt-4o", 
        "gemini-pro"
    ]
    
    if model not in model_list:
        print(f"{Fore.RED}Invalid model. Choose from: claude-3-5-sonnet-20240620, gpt-4o, gemini-pro{Style.RESET_ALL}")
        return

    if not messages:  # Check if the chat history is empty
        message = "This is a new conversation. There is no previous history."

    payload = {
        "messages": messages + [{"role": "user", "content": message}],  # Concatenate messages into a single list
        "stream": True,
        "model": model,
        "temperature": 0.5,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_p": 1,
        "max_tokens": 200000
    }

    session = requests.Session()
    
    try:
        with session.post(url, headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()

            if message != "This is a new conversation. There is no previous history.":
                messages.append({"role": "user", "content": message})  # Add user message to history

            assistant_content = ""  # Initialize a variable to store the accumulating assistant content
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    line = line[6:]
                
                if line.strip() == '[DONE]':
                    messages.append({"role": "assistant", "content": assistant_content})  # Add the complete message to history
                    save_chat_history(messages)  # Save updated chat history
                    return
                
                try:
                    data = json.loads(line)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content')
                        if content:
                            print(f"{Fore.GREEN}{content}{Style.RESET_ALL}", end='', flush=True)
                            assistant_content += content  # Accumulate the assistant content
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

while True:
        try:
            query = input(f"{Fore.CYAN}\nEnter Query: {Style.RESET_ALL}")
            if query.lower() == "clear history":
                messages = []
                save_chat_history(messages)
                print(f"{Fore.YELLOW}\nChat history cleared.{Style.RESET_ALL}")
            else:
                Type_gpt(query)

        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
