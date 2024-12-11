import requests
from datetime import datetime
import json
import re
import uuid
import threading
import time
from colorama import init, Fore, Style
from typing import List
import random
# Import the Proxy function and ProxyManager class
from proxy.Proxy import Proxy
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

# Initialize colorama for colored output
init()

# Create a global ProxyManager instance
global_proxy_manager = ProxyManager()

# Start the Proxy function to collect proxies
def start_proxy_collection():
    Proxy(prints=False)

# Start proxy collection in a background thread
proxy_thread = threading.Thread(target=start_proxy_collection, daemon=True)
proxy_thread.start()

# Wait for initial proxies to be collected
print(f"{Fore.CYAN}Starting proxy collection...{Style.RESET_ALL}")
time.sleep(10)  # Wait time may be adjusted as needed

def clade(message):
    url = "https://chat100.erweima.ai/api/v1/chat/claude3/chat"

    while True:
        proxy = global_proxy_manager.get_random_proxy()
        if not proxy:
            print(f"{Fore.YELLOW}No proxies available. Waiting...{Style.RESET_ALL}")
            time.sleep(2)
            continue

        proxies = {
            "http": proxy,
            "https": proxy
        }

        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "attachment": [],
            "chatUuid": uuid.uuid4().hex,
            "firstQuestionFlag": False,
            "language": "en",
            "prompt": message,
            "searchFlag": False,
            "sendTime": formatted_datetime
        }
        headers = {
            "uniqueId": uuid.uuid4().hex[:32]
        }

        try:
            response = requests.post(url, json=payload, headers=headers, proxies=proxies, timeout=10)
            if response.status_code == 200:
                # Attempt to extract the message
                try:
                    # Method 1: Regex extraction
                    messages = re.findall(r'"message"\s*:\s*"([^"]*)"', response.text)
                    if messages:
                        return ''.join(messages).strip()

                    # Method 2: JSON parsing
                    lines = response.text.strip().split('\n')
                    parsed_messages = [
                        json.loads(line)['data']['message']
                        for line in lines
                        if line != '[DONE]' and 'data' in json.loads(line) and 'message' in json.loads(line)['data']
                    ]
                    if parsed_messages:
                        return ''.join(parsed_messages).strip()

                    # Method 3: Fallback raw text extraction
                    return response.text

                except Exception as e:
                    print(f"{Fore.RED}Error extracting message: {e}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Raw response: {response.text}{Style.RESET_ALL}")
                    return "Error processing response"
            else:
                # Remove the proxy if response is not successful
                global_proxy_manager.remove_proxy(proxy)
                continue  # Try the next proxy

        except Exception as e:
            # Remove the proxy if an exception occurs
            global_proxy_manager.remove_proxy(proxy)
            print(f"{Fore.RED}Proxy {proxy} failed: {e}{Style.RESET_ALL}")
            continue  # Try the next proxy

    return "No response received"

# Main interaction loop
def main():
    print(f"{Fore.CYAN}Chat started. Type 'exit' to end.{Style.RESET_ALL}")
    query = ""
    while True:
        query = input("You: ")
        if query.lower() == 'exit':
            break

        response = clade(query)
        print(f"Claude: {response}\n")

if __name__ == "__main__":
    main()