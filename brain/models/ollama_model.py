import ollama
from brain.models.base_model import BaseModel
from loguru import logger

class OllamaModel(BaseModel):
    def __init__(self, base_url="http://localhost:11434", model="llama3.2"):
        self.base_url = base_url
        self.client = ollama.Client(host=base_url)
        self.model = model

    async def _async_chat(self, messages):
        """Async method to handle streaming responses"""
        try:
            self._has_yielded = False  # Initialize the flag
            async_client = ollama.AsyncClient(host=self.base_url)
            async for chunk in await async_client.chat(
                model=self.model,
                messages=messages,
                stream=True
            ):
                logger.deep_debug(f"Received chunk from Ollama: {chunk}")
                if 'message' in chunk and chunk['message'].get('content'):
                    content = chunk['message']['content']
                    logger.deep_debug(f"Yielding content: {content}")
                    self._has_yielded = True  # Set flag when content is yielded
                    yield {'message': content, 'is_chunk': True}
                elif chunk.get('done', False):
                    # If we're done and haven't yielded anything, yield a default response
                    if not self._has_yielded:
                        logger.warning("No content was yielded before done signal, sending default response")
                        yield {'message': "I apologize, but I couldn't generate a valid response. Please try rephrasing your question.", 'is_chunk': True}
        except Exception as e:
            logger.error(f"Error in _async_chat: {str(e)}")
            yield {'message': f"Error generating response: {str(e)}", 'is_chunk': True}

    def chat(self, messages, stream=False):
        if stream:
            logger.deep_debug(f"Sending streaming request to model: {self.model}")
            # Return async generator for streaming
            return self._async_chat(messages)        
        else:
            logger.deep_debug(f"Sending non-streaming request to model: {self.model}")
            logger.deep_debug(f"Messages sent: {messages}")
            response = self.client.chat(
                model=self.model,
                messages=messages,
                stream=False
            )
            logger.deep_debug(f"Response received: {response}")
            return {'message': {'role': 'assistant', 'content': response['message']['content']}}

    def embed(self, input_texts):
        if isinstance(input_texts, str):
            input_texts = [input_texts]

        embeddings = []
        for text in input_texts:
            response = ollama.embeddings(
                model=self.model,
                prompt=text
            )
            embeddings.append(response["embedding"])
        
        # Log some debugging info
        if embeddings:
            logger.deep_debug(f"Generated {len(embeddings)} embeddings")
            logger.deep_debug(f"Embedding dimension: {len(embeddings[0])}")
            logger.deep_debug(f"Sample values: {embeddings[0][:5]}") 
        
        return embeddings