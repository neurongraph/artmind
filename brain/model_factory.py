from brain.models.openai_model import OpenAIModel
from brain.models.ollama_model import OllamaModel

class ModelFactory:
    @staticmethod
    def create(llm_host, **kwargs):
        if llm_host == "openai":
            return OpenAIModel(
                base_url=kwargs.get("base_url"),                
                model=kwargs.get("model"),
                api_key=kwargs.get("api_key")
            )
        elif llm_host == "ollama":
            return OllamaModel(
                base_url=kwargs.get("base_url"),                
                model=kwargs.get("model")
            )
        else:
            raise ValueError(f"Unsupported backend: {llm_host}")
