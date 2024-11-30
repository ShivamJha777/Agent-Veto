import requests
import json
import threading
import random
import time
from typing import List
from Proxy import Proxy
from colorama import init, Fore, Style

# Initialize colorama
init()

# Create global proxy manager
class ProxyManager:
    def __init__(self):
        self.proxies: List[str] = []
        self.buffer_proxies: List[str] = []  # Buffer list for next rotation
        self.lock = threading.Lock()
        self.buffer_lock = threading.Lock()
        self.proxy_file = "Working_proxies.txt"
        self.last_refresh = 0
        self.refresh_interval = 90  # 90 seconds (allowing 30s overlap before 2min expiry)
        self.start_refresh_threads()

    def start_refresh_threads(self):
        # Start main proxy refresh thread
        self.refresh_thread = threading.Thread(target=self.refresh_proxies, daemon=True)
        self.refresh_thread.start()
        # Start buffer refresh thread
        self.buffer_thread = threading.Thread(target=self.refresh_buffer, daemon=True)
        self.buffer_thread.start()

    def refresh_buffer(self):
        """Maintain a buffer of fresh proxies"""
        while True:
            try:
                with open(self.proxy_file, 'r') as f:
                    new_proxies = [line.strip() for line in f if line.strip()]
                
                with self.buffer_lock:
                    self.buffer_proxies = new_proxies
                
                # Sleep for 60 seconds before next buffer refresh
                time.sleep(60)
            except Exception as e:
                print(f"{Fore.RED}Error refreshing buffer: {e}{Style.RESET_ALL}")
                time.sleep(5)

    def refresh_proxies(self):
        """Main proxy refresh logic"""
        while True:
            try:
                current_time = time.time()
                
                # If buffer has proxies and it's time to refresh
                if current_time - self.last_refresh >= self.refresh_interval:
                    with self.buffer_lock:
                        if self.buffer_proxies:
                            with self.lock:
                                self.proxies = self.buffer_proxies.copy()
                            self.last_refresh = current_time
                
                # Short sleep to prevent CPU spinning
                time.sleep(5)
            except Exception as e:
                print(f"{Fore.RED}Error in main refresh: {e}{Style.RESET_ALL}")
                time.sleep(2)

    def get_random_proxy(self) -> str:
        with self.lock:
            return random.choice(self.proxies) if self.proxies else None

    def remove_proxy(self, proxy: str):
        with self.lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
        with self.buffer_lock:
            if proxy in self.buffer_proxies:
                self.buffer_proxies.remove(proxy)
global_proxy_manager = ProxyManager()

def Type_gpt(message,system_message="You are a helpful assistant.",model="gpt-4o"):
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
    model_list=[
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
        "model": "claude-3-5-sonnet-20240620",
        "temperature": 0.5,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_p": 1,
        "max_tokens": 12000
    }

    # Create session for connection pooling
    session = requests.Session()

    while True:
        proxy = global_proxy_manager.get_random_proxy()
        if not proxy:
            time.sleep(2)  # Reduced wait time
            continue

        proxies = {
            "http": proxy,
            "https": proxy
        }
        
        try:
            with session.post(url, headers=headers, json=payload, stream=True, proxies=proxies) as response:
                if response.status_code != 200:
                    global_proxy_manager.remove_proxy(proxy)
                    continue
                    
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
            global_proxy_manager.remove_proxy(proxy)
            continue

def main():
    # Start proxy collection in background
    proxy_thread = threading.Thread(target=lambda: Proxy(prints=False), daemon=True)
    proxy_thread.start()
    print(f"{Fore.CYAN}Starting TypeGPT...{Style.RESET_ALL}")
    time.sleep(30)  # Wait for initial proxies
    
    while True:
        try:
            query = input(f"{Fore.CYAN}\nEnter Query: {Style.RESET_ALL}")
            Type_gpt(query)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()