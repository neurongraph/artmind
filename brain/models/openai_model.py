import openai
from .base_model import BaseModel

# ToDo: Rewrite this once the ollama_model.py is tested

class OpenAIModel(BaseModel):
    def __init__(self, base_url, model, api_key):
        if api_key is None:
            raise ValueError("OpenAI API key is required.")
        openai.api_key = api_key
        self.model = model
        if base_url:
            openai.base_url = base_url 

    def chat(self, messages, stream=False):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            stream=stream
        )
        if stream:
            full_response = ""
            for chunk in response:
                content = chunk.choices[0].delta.get("content", "")
                print(content, end="", flush=True)
                full_response += content
            print()
            return full_response
        else:
            return response.choices[0].message["content"]
