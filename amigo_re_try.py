import requests
import json

def generate_response(query, model="gpt-4o-2024-11-20", system_prompt=''):
    url = "https://api.amigochat.io//v1/chat/completion"
    auth = "Bearer "
    header = {
        "Authorization": auth
    }
    scrape_sources = [
            'https://free-proxy-list.net/',
            'https://www.us-proxy.org/',
            'https://www.sslproxies.org/',
            'https://www.freeproxylists.net/http.html',
            'http://www.freeproxy.world/',
            'https://www.proxynova.com/proxy-server-list/',
            'https://www.proxyrack.com/free-proxy-list/',
            'https://www.hide-my-ip.com/proxylist.shtml',
            'http://www.httptunnel.ge/ProxyListForFree.aspx',
            'https://www.ip-adress.com/proxy-list',
            'https://proxyservers.pro/',
            'https://www.proxy-list.org/',
            'https://www.proxydocker.com/',
            'https://www.socks-proxy.net/',
            'https://www.cool-proxy.net/',
            'https://premproxy.com/list/',
            'https://www.proxy-list.download/HTTP',
            'https://www.proxyniche.com/proxy-list/',
            'http://proxydb.net/',
            'http://www.proxylists.net/',
            'http://www.megaproxy.com/freeproxy.html',
            'https://vpnoverview.com/privacy/anonymous-browsing/free-proxy-servers/',
            'https://www.freeproxylists.net/',
            'https://www.my-proxy.com/free-proxy-list.html',
            'https://www.proxyrotator.com/free-proxy-list/',
            'https://free-proxy-list.com/',
        ]


    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "model": model,
        "frequency_penalty": 0,
        "max_tokens": 4000,
        "presence_penalty": 0,
        "stream": True,  # Enable streaming
        "top_p": 0.95
    }

    try:
        # Make the actual request with the working proxy
        with requests.post(url, headers=header, json=payload, stream=True,proxies={"https":"http://165.155.228.14:9480","http":"http://165.155.228.14:9480"}) as response:
            if response.status_code == 201:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data_json = json.loads(data_str)
                                choices = data_json.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        print(content, end='', flush=True)
                            except json.JSONDecodeError:
                                print(f"Received non-JSON data: {data_str}")
            else:
                print(f"Request failed with status code {response.status_code}")
                print(response.text)
    except Exception as e:
        print(f"Error during request with working proxy: {e}")

generate_response(query="Hey! How are you?")
