from brain.models.base_model import BaseModel
from .model_factory import ModelFactory
from loguru import logger
import json

class DomainRouter:
    def __init__(self, config):
        """Initialize the router with configuration."""
        self.config = config

    
    def get_handler(self, persona: str = None) -> BaseModel:
        """
        Get the appropriate handler for the given persona.
        
        Args:
            persona: The persona prompt to handle the chat
            
        Returns:
            A handler instance for the persona
        """
        logger.debug(f"Getting handler for persona: {persona}")
        return ModelFactory.create(self.config.persona_models[persona].llm_host,
                            base_url=self.config.persona_models[persona].base_url,
                            model=self.config.persona_models[persona].model,
                            api_key=self.config.persona_models[persona].api_key)


