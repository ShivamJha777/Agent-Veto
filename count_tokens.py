import tiktoken
import json

with open('chat_history.json', 'r') as f:
    data = json.load(f)

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
print(f'Total tokens in chat history: {len(encoding.encode(str(data)))}')
