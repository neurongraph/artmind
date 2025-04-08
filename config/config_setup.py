import cattrs
from attrs import define
import yaml

# ---------------------------------------------------------
# Defining the config structure in the form of classes, and then loading it via a function
# ---------------------------------------------------------
# All configurations required for the interface are stored in the file below
CONFIG_YAML = "./config/config.yaml"


@define
class PersonaModelConfig:
    persona_name: str
    model: str
    llm_host: str
    base_url: str    
    api_key: str
    icon: str
    persona_prompt: str

@define
class Config:
    page_title: str
    artmind_server_url: str
    database_config_server_url: str
    database_data_server_url: str
    file_storage: str
    persona_models: dict[str, PersonaModelConfig]

def init_config():
    with open(CONFIG_YAML) as yaml_stream:
        data = yaml.safe_load(yaml_stream)
        config = cattrs.structure(data, Config)
    return config