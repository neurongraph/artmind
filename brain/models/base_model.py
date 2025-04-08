from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def chat(self, messages, stream=False):
        pass

    # @abstractmethod
    # def embed(self, input_texts):
    #     pass
