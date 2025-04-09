from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from loguru import logger

def init_db_connection(database_url):
    """Initialize database connection."""
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()

def create_chat_history_table(session):
    """Create the chat_history table if it doesn't exist."""
    query = """
    CREATE TABLE IF NOT EXISTS chat_history (
        id SERIAL PRIMARY KEY,
        user_name TEXT NOT NULL,
        persona TEXT NOT NULL,
        title TEXT NOT NULL,
        messages JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    session.execute(text(query))
    session.commit()

class ChatHistoryManager:
    def __init__(self, database_url):
        self.session = init_db_connection(database_url)
        create_chat_history_table(self.session)

    def generate_chat_title(self, text, existing_titles=None):
        """Generate a title for the chat using basic text processing."""
        try:
            # Take first 100 characters or up to first newline
            title = text.split('\n')[0][:100]
            
            # Remove any trailing punctuation
            title = title.rstrip('.,!?')
            
            # Add ellipsis if text was truncated
            if len(text) > 100:
                title += "..."
                
            # If no title generated, use default
            if not title:
                title = "New Chat"
                
            # Handle duplicate titles by adding a number suffix
            if existing_titles and title in existing_titles:
                counter = 1
                while f"{title} ({counter})" in existing_titles:
                    counter += 1
                title = f"{title} ({counter})"
                
            return title
        except Exception as e:
            logger.error(f"Error generating chat title: {str(e)}")
            return "New Chat"

    def save_chat_history(self, user_name, persona, messages, title):
        """Save chat history to database."""
        try:
            # Convert messages to JSON string if it's a list
            if isinstance(messages, list):
                messages_json = json.dumps(messages)
            else:
                messages_json = messages

            query = """
            INSERT INTO chat_history (user_name, persona, title, messages)
            VALUES (:user_name, :persona, :title, :messages)
            RETURNING id;
            """
            result = self.session.execute(
                text(query),
                {
                    "user_name": user_name,
                    "persona": persona,
                    "title": title,
                    "messages": messages_json
                }
            )
            self.session.commit()
            return result.scalar()
        except Exception as e:
            logger.error(f"Error saving chat history: {str(e)}")
            self.session.rollback()
            raise

    def get_chat_histories(self, user_name=None, limit=10):
        """Retrieve chat histories from database."""
        try:
            query = """
            SELECT id, user_name, persona, title, messages, created_at, updated_at
            FROM chat_history
            """
            params = {}
            if user_name:
                query += " WHERE user_name = :user_name"
                params["user_name"] = user_name
            
            query += " ORDER BY created_at DESC LIMIT :limit"
            params["limit"] = limit
            
            result = self.session.execute(text(query), params)
            histories = []
            for row in result:
                # Handle both string and list message formats
                messages = row[4]
                if isinstance(messages, str):
                    messages = json.loads(messages)
                
                histories.append({
                    "id": row[0],
                    "user_name": row[1],
                    "persona": row[2],
                    "title": row[3],
                    "messages": messages,
                    "created_at": row[5],
                    "updated_at": row[6]
                })
            return histories
        except Exception as e:
            logger.error(f"Error retrieving chat histories: {str(e)}")
            raise

    def get_chat_history(self, history_id):
        """Retrieve a specific chat history by ID."""
        try:
            query = """
            SELECT id, user_name, persona, title, messages, created_at, updated_at
            FROM chat_history
            WHERE id = :history_id
            """
            result = self.session.execute(text(query), {"history_id": history_id})
            row = result.first()
            if row:
                # Handle both string and list message formats
                messages = row[4]
                if isinstance(messages, str):
                    messages = json.loads(messages)
                    
                return {
                    "id": row[0],
                    "user_name": row[1],
                    "persona": row[2],
                    "title": row[3],
                    "messages": messages,
                    "created_at": row[5],
                    "updated_at": row[6]
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving chat history: {str(e)}")
            raise

    def close(self):
        """Close the database session."""
        try:
            self.session.close()
        except Exception as e:
            logger.error(f"Error closing chat history session: {str(e)}") 