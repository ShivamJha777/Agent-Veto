import requests
import json
import threading
import random
import time
from typing import List
from colorama import init, Fore, Style
def Type_gpt(message, system_message="You are a helpful assistant.", model="claude-3-5-sonnet-20240620"):
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
        
    payload = {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ],
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
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    line = line[6:]
                
                if line.strip() == '[DONE]':
                    return
                
                try:
                    data = json.loads(line)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content')
                        if content:
                            print(f"{Fore.GREEN}{content}{Style.RESET_ALL}", end='', flush=True)
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
while True:
        try:
            query = input(f"{Fore.CYAN}\nEnter Query: {Style.RESET_ALL}")
            Type_gpt(query)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
