from openai import OpenAI
import tiktoken
import json
import hashlib
import os
from dotenv import load_dotenv

def num_tokens_from_string(string: str, encoding_name="cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def chat_with_gpt_multi_round(prompt, model="gpt-4-1106-preview", messages=None, log=False, cache=False):
    load_dotenv()
    if num_tokens_from_string(prompt) > 8000:
        
        print("Exceed Token Limit!", num_tokens_from_string(prompt), prompt)
        return False, None, []
    
    if messages is None:
        messages = []
    
    # query cache first, to save GPT4 tokens
    Queries = os.listdir("./Explianable_Vulnerability/GPTQueryCache/")
    str = prompt + model + json.dumps(messages)
    key =  hashlib.sha256(str.encode()).hexdigest()
    messages.append({"role": "user", "content": prompt})
    if cache == True and key + '.txt' in Queries:
        with open("./Explianable_Vulnerability/GPTQueryCache/" + key + '.txt', 'r') as f:
            content = f.read()
            assistant_response = content
            messages.append({"role": "assistant", "content": content})
            return True, assistant_response, messages
    client = OpenAI(
        api_key=os.getenv("API_KEY"),
    )

    # try: 
    # Add the new prompt message to the message history
    response = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=0,
    )

    assistant_response = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_response})
    if log:
        print("Q:", prompt.strip())
        print("A:", assistant_response.strip())
        
    with open("./Explianable_Vulnerability/GPTQueryCache/" + key + '.txt', 'w+') as f:
        f.write(assistant_response)
        
    return True, assistant_response, messages



def chat_with_gpt_single_round(prompt, model="gpt-4-1106-preview"):
    load_dotenv()
    client = OpenAI(
        api_key=os.getenv("API_KEY"),
    )

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0,
    )

    assistant_response = response.choices[0].message.content
    return assistant_response
