import requests
import json
from colorama import init, Fore, Style
import threading
import time
import tiktoken
import os

# Add global variable for current model
current_model = "gpt-4o"  # default model

def manage_token_count():
    global current_model
    print(f"\n{Fore.YELLOW}Token management thread started{Style.RESET_ALL}\n")
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    print(f"{Fore.YELLOW}Encoding initialized{Style.RESET_ALL}")
    
    def truncate_by_tokens(messages, max_tokens):
        print(f"{Fore.YELLOW}Starting truncation. Messages count: {len(messages)}, Max tokens: {max_tokens}{Style.RESET_ALL}")
        total_tokens = 0
        for i in range(len(messages)-1, -1, -1):
            msg_tokens = len(encoding.encode(str(messages[i])))
            print(f"{Fore.YELLOW}Message {i}: {msg_tokens} tokens{Style.RESET_ALL}")
            if total_tokens + msg_tokens > max_tokens:
                print(f"{Fore.YELLOW}Token limit reached. Truncating to last {len(messages)-i-1} messages{Style.RESET_ALL}")
                return messages[i+1:]
            total_tokens += msg_tokens
        print(f"{Fore.YELLOW}Total tokens: {total_tokens}{Style.RESET_ALL}")
        return messages
    
    def handle_size_range(messages, min_mb, max_mb, current_size_mb):
        print(f"{Fore.YELLOW}Processing {min_mb}-{max_mb}MB range (current: {current_size_mb:.2f}MB){Style.RESET_ALL}")
        
        if min_mb == 0:  # 0-1MB: Light cleanup
            messages = messages[-200:]
            return truncate_by_tokens(messages, 50000)
        elif min_mb == 1:  # 1-2MB: Moderate cleanup
            messages = messages[-150:]
            return truncate_by_tokens(messages, 40000)
        elif min_mb == 2:  # 2-3MB: Aggressive cleanup
            messages = messages[-100:]
            return truncate_by_tokens(messages, 30000)
        elif min_mb == 3:  # 3-4MB: Very aggressive cleanup
            messages = messages[-75:]
            return truncate_by_tokens(messages, 20000)
        elif min_mb < 10:  # 4-9MB: Emergency cleanup
            messages = messages[-50:]
            return truncate_by_tokens(messages, 10000)
        else:  # 10MB+: Critical cleanup
            messages = messages[-25:]
            return truncate_by_tokens(messages, 5000)
    
    while True:
        try:
            print(f"{Fore.YELLOW}Starting token management cycle{Style.RESET_ALL}")
            try:
                file_size = os.path.getsize("chat_history.json")
                current_size_mb = file_size/1_000_000
                print(f"{Fore.YELLOW}Current file size: {current_size_mb:.2f}MB{Style.RESET_ALL}")
                
                if file_size > 0:  # If file exists and has content
                    with open("chat_history.json", "r") as f:
                        messages = json.loads(f.read())
                    print(f"{Fore.YELLOW}Loaded {len(messages)} messages{Style.RESET_ALL}")
                    
                    # Determine which size range to process
                    for mb in range(0, 11):
                        if current_size_mb <= mb + 1:
                            messages = handle_size_range(messages, mb, mb + 1, current_size_mb)
                            break
                    
                    print(f"{Fore.YELLOW}After processing: {len(messages)} messages{Style.RESET_ALL}")
                    
                    with open("chat_history.json", "w") as f:
                        json.dump(messages, f)
                    print(f"{Fore.YELLOW}Chat history saved after processing{Style.RESET_ALL}")
                    
            except OSError as e:
                print(f"{Fore.RED}OSError during file check: {str(e)}{Style.RESET_ALL}")
                continue

        except Exception as e:
            print(f"{Fore.RED}Error in token management: {str(e)}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}Sleeping for 60 seconds...{Style.RESET_ALL}")
        time.sleep(60)

token_thread = threading.Thread(target=manage_token_count, daemon=True)
token_thread.start()
def Type_gpt(message, system_message="You are a helpful assistant.", model="gpt-4o"):
    global current_model, token_thread
    current_model = model  # Update the global model
    
    """Test version of Type_gpt with combined functionality"""
    
    def load_chat_history():
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
        try:
            with open("chat_history.json", "r+") as f:
                data = f.read()
                if not data:
                    f.seek(0)
                    json.dump(messages, f)
                else:
                    existing_data = json.loads(data)
                    existing_data.extend(messages)
                    f.seek(0)
                    json.dump(existing_data, f)
        except FileNotFoundError:
            with open("chat_history.json", "w") as f:
                json.dump(messages, f)

    messages = load_chat_history()
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
    
    model_list = ["claude-3-5-sonnet-20240620", "gpt-4o", "gemini-pro"]
    
    if model not in model_list:
        print(f"{Fore.RED}Invalid model. Choose from: claude-3-5-sonnet-20240620, gpt-4o, gemini-pro{Style.RESET_ALL}")
        return

    if not messages:
        message = "This is a new conversation. There is no previous history."

    payload = {
        "messages": messages + [{"role": "user", "content": message}],
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
                messages.append({"role": "user", "content": message})

            assistant_content = ""
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    line = line[6:]
                
                if line.strip() == '[DONE]':
                    messages.append({"role": "assistant", "content": assistant_content})
                    save_chat_history(messages)
                    return
                
                try:
                    data = json.loads(line)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content')
                        if content:
                            print(f"{Fore.CYAN}{content}{Style.RESET_ALL}", end='', flush=True)
                            assistant_content += content
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

# Test the function
if __name__ == "__main__":
    init()  # Initialize colorama
    print("Testing the new Type_gpt implementation...")
    while True:
        test_message = input("User:")
        print()
        print("Assistant:",end=" ")
        Type_gpt(test_message)

        print("\n")