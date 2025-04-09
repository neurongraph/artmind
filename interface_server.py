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
    histories = chat_manager.get_chat_histories(user_name=state.user_name)
    history_options = ["New Chat"]
    history_dict = {"New Chat": None}
    existing_titles = set()
    
    if histories:
        for history in histories:
            option_text = history["title"]
            history_options.append(option_text)
            history_dict[option_text] = history["id"]
            existing_titles.add(option_text)
    
    selected_chat = st.sidebar.selectbox(
        "Select Chat",
        options=history_options,
        key="chat_history_dropdown"
    )
    
    # Handle chat selection
    if selected_chat != "New Chat":
        history_id = history_dict[selected_chat]
        if history_id != state.current_history_id:
            try:
                history = chat_manager.get_chat_history(history_id)
                if history:
                    state.history = history["messages"]
                    state.current_history_id = history_id
                    st.rerun()
            except Exception as e:
                logger.error(f"Failed to load chat history: {str(e)}")
                st.sidebar.error("Failed to load chat history")

    # New Chat button
    if st.sidebar.button("Start New Chat", type="primary"):
        try:
            if state.history and len(state.history) > 1:
                title = "New Chat"
                for message in state.history:
                    if message["role"] == "user":
                        title = chat_manager.generate_chat_title(message["content"], existing_titles)
                        break
                
                chat_manager.save_chat_history(state.user_name, state.persona_selected, state.history, title)
                logger.info(f"Saved chat history with title: {title}")
            
            current_persona = state.persona_selected
            state.clear_chat()
            state.persona_selected = current_persona
            st.rerun()
        except Exception as e:
            logger.error(f"Failed to handle new chat: {str(e)}")
            st.sidebar.error("Failed to start new chat")
    
    # Display chat history and handle new messages
    display_chat_messages(state.history)
    logger.deep_debug(f"{config=}")        
    handle_chat_input(config, state.persona_selected, state)

if __name__ == "__main__":
    main()