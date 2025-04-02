import streamlit as st
import cattrs
import yaml
from attrs import define, field
from loguru import logger
import sys

def setup_logging():
    """
    Configures the logging system using the loguru library.

    This function performs the following:
    - Removes any existing loggers.
    - Adds a file logger that writes logs to `logs/interface.log` with:
        - Level: INFO | DEBUG
        - Format: "{time} | {level} | {message}"
        - Rotation: 10 MB
        - Serialization: Enabled
    - Adds a console logger (`sys.stderr`) for ERROR level logs.

    Returns
    -------
    None
    """
    logger.remove()
    logger.add("logs/interface.log", level="DEBUG", format="{time} | {level} | {message}", rotation="10 MB", serialize=True)
    logger.add(sys.stderr, level="ERROR")

# ---------------------------------------------------------
# Defining the config structure in the form of classes, and then loading it via a function
# ---------------------------------------------------------
# All configurations required for the interface are stored in the file below
CONFIG_YAML = "config.yaml"

@define
class Persona:
    name: str
    persona_prompt: str

@define
class Config:
    page_title: str
    artmind_server_url: str
    database_config_server_url: str
    database_data_server_url: str
    file_storage: str

def init_config(config_file):
    with open(config_file) as yaml_stream:
        data = yaml.safe_load(yaml_stream)
        config = cattrs.structure(data, Config)
    return config

def init_page(page_title):
    # Set page title and favicon
    st.set_page_config(page_title=page_title, page_icon="🧠", layout="wide")
    # Initialize session state
    return SessionState.initialize()

@define
class SessionState:
    """Centralized session state management"""
    history: list = field(factory=list)
    current_history_id: str = None

    @classmethod
    def initialize(cls):
        """Initialize session state if not already present"""
        if "state" not in st.session_state:
            st.session_state.state = cls()
        return st.session_state.state


def main():
    setup_logging()
    config = init_config(CONFIG_YAML)
    state = init_page(config.page_title)

    options = {"💬": "Chat", "📖": "Documents", "⊞⊞": "Database"}
    persona_icon = st.sidebar.radio(
        "What persona do  you want to use?:",
        options=options.keys(),
        horizontal=True,
        index=0,
    )

    persona = (options[persona_icon])
    st.sidebar.markdown(persona_icon + " " + persona)

if __name__ == "__main__":
    main()