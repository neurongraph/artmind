import streamlit as st
from attrs import field, define
from loguru import logger
import getpass
from config.config_setup import init_config
from config.logging_setup import setup_logging
from interface.ui_components import handle_chat_input, display_chat_messages
from interface.chat_history import ChatHistoryManager

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
    
    def clear_chat(self):
        """Clear chat history and related state"""
        self.history = []
        self.current_history_id = None    

@logger.catch
def main():
    # Initialize logging and configuration, history and upload manager
    setup_logging()
    config = init_config()
    state = init_page(config.page_title)
    chat_manager = ChatHistoryManager(config.database_config_server_url)

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
    st.sidebar.divider()

    # Handle chat history
    history_options, history_dict, existing_titles = chat_manager.build_history_options(state.user_name)

    selected_chat = st.sidebar.selectbox(
        "Select Chat",
        options=history_options,
        key="chat_history_dropdown"
    )

    # Handle chat selection
    if selected_chat != "New Chat":
        history_id = history_dict[selected_chat]
        if history_id != state.current_history_id:
            if chat_manager.load_chat_history(state, history_id):
                st.rerun()
            else:
                st.sidebar.error("Failed to load chat history")

    # New Chat button
    if st.sidebar.button("Start New Chat", type="primary"):
        if chat_manager.save_and_reset_chat(state, existing_titles):
            st.rerun()
        else:
            st.sidebar.error("Failed to start new chat")
    
    # Display chat history and handle new messages
    display_chat_messages(state.history)
    logger.deep_debug(f"{config=}")        
    handle_chat_input(config, state.persona_selected, state)

if __name__ == "__main__":
    main()