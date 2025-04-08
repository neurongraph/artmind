import streamlit as st
from attrs import field, define
from loguru import logger
import getpass
from config.config_setup import init_config
from config.logging_setup import setup_logging
from interface.ui_components import handle_chat_input, display_chat_messages

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
    persona_selected: str = None
    user_name: str = field(factory=getpass.getuser)

    @classmethod
    def initialize(cls):
        """Initialize session state if not already present"""
        if "state" not in st.session_state:
            st.session_state.state = cls()
        return st.session_state.state

@logger.catch
def main():
    setup_logging()
    config = init_config()
    state = init_page(config.page_title)

    persona_icons_dict = {}
    for persona_model in config.persona_models.values():
        persona_icons_dict[persona_model.icon] = persona_model.persona_name

    persona_icon = st.sidebar.radio(
        f"Hi {state.user_name}:",
        options=persona_icons_dict.keys(),
        horizontal=True,
        index=0,
    )

    state.persona_selected = (persona_icons_dict[persona_icon])
    st.sidebar.markdown(persona_icon + " " + state.persona_selected)
    
    # Display chat history and handle new messages
    display_chat_messages(state.history)
    logger.deep_debug(f"{config=}")        
    handle_chat_input(config, state.persona_selected, state)

if __name__ == "__main__":
    main()