import streamlit as st
from loguru import logger
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def process_streaming_message(data_line, message_placeholder, full_response):
    """Process a single SSE data line and update the UI."""
    try:
        chunk_data = json.loads(data_line)
        if chunk_data.get('is_chunk') and (message := chunk_data.get('message')):
            full_response += message
            message_placeholder.markdown(full_response + "▌")
            logger.debug(f"Updated response: {full_response}")
    except json.JSONDecodeError:
        logger.error(f"Failed to parse chunk: {data_line}")
    except Exception as e:
        logger.error(f"Error processing chunk: {data_line}, error: {e}")
    return full_response

def get_response_handle(artmind_server_url: str, payload: dict) -> requests.Response:
    """Get response from server with increased timeout and retries."""
    try:
        # Increase timeout to 120 seconds and add retries
        session = requests.Session()
        retries = Retry(
            total=3,  # number of retries
            backoff_factor=0.5,  # wait 0.5, 1, 2 seconds between retries
            status_forcelist=[500, 502, 503, 504]  # retry on these status codes
        )
        session.mount('http://', HTTPAdapter(max_retries=retries))
        
        return session.post(
            url=artmind_server_url,
            data=payload,
            stream=True,
            timeout=(10, 120)  # (connect timeout, read timeout)
        )
    except requests.exceptions.Timeout:
        logger.error("Request timed out. The server is taking too long to respond.")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to server: {str(e)}")
        raise

def display_chat_messages(messages):
    """Display all messages in the chat history."""
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_chat_input(config, persona_selected, state):
    """Handle chat input and responses."""
    if not (prompt := st.chat_input("What is up?")):
        return

    # Add user message to history and display
    state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare for assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Ensure system prompt is included
            messages_with_system = state.history
            if not any(msg["role"] == "system" for msg in messages_with_system):
                persona_prompt = config.persona_models[persona_selected].persona_prompt
                messages_with_system = [{"role": "system", "content": persona_prompt}] + messages_with_system
            
            # Get streaming response
            response = get_response_handle(
                config.artmind_server_url,
                { ## -- The following should match the parameters received in the brain -- ##
                    "sender": state.user_name,
                    "persona_selected": state.persona_selected,
                    "messages": json.dumps(messages_with_system),  # Send full message history
                    # "upload_dir": state.upload_dir,
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Server error: {response.status_code}")
                message_placeholder.error(f"Server error: {response.status_code}")
                return

            # Show initial cursor and process stream
            message_placeholder.markdown("▌")
            response.encoding = 'utf-8'
            
            try:
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                        
                    if not line.startswith('data: '):
                        continue
                        
                    data = line[6:]  # Remove "data: " prefix
                    if data == "[DONE]":
                        break
                        
                    full_response = process_streaming_message(
                        data,
                        message_placeholder,
                        full_response
                    )

            except Exception as e:
                logger.exception("Error reading stream")
                message_placeholder.error("Error reading response stream")
                return

            # Update UI with final response
            if full_response:
                message_placeholder.markdown(full_response)
                state.history.append({
                    "role": "assistant",
                    "content": full_response
                })
            else:
                message_placeholder.warning("No response received from the server.")

        except Exception as e:
            logger.exception("Error in dialog")
            message_placeholder.error("Failed to process server response.") 