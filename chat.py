from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
load_dotenv()
apikey=os.getenv("api_key")
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
client = InferenceClient(api_key=apikey)

def chatbot(context, query):
    query_template = f"""
    You are given a list of words which when combined make sense. Return answer to query:{query} 
    only based on context:{context}, else just say 'Not in the given context'.
    Do not give comments or anyother additional information. Stick to the context:{context}.
    If context:{context} is blank just say, no context provided. """

    messages = [
        {"role": "system", "content": query_template},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
    ]
    response = client.chat.completions.create(
        model=repo_id,
        messages=messages
    )

    my_response = response['choices'][0]['message']['content']
    return my_response.split(',')