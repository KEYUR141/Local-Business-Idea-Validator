import json
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class InMemoryConversationManager:
    """In-memory conversation manager for Cloud Run (no Redis dependency)"""
    
    def __init__(self):
        self.conversations = {}
        logger.info("In-Memory Conversation Manager initialized")
    
    def create_conversation(self, conversation_id: str, title: str = None) -> bool:
        try:
            self.conversations[conversation_id] = {
                "created_at": datetime.now().isoformat(),
                "title": title or "Untitled",
                "message_count": 0,
                "messages": []
            }
            logger.info(f"Created new conversation with ID: {conversation_id}, Title: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            return False
    
    def add_message(self, conversation_id: str, role: str, context: str) -> bool:
        try:
            if conversation_id not in self.conversations:
                return False
            
            message = {
                "role": role,
                "content": context,
                "timestamp": datetime.now().isoformat()
            }
            self.conversations[conversation_id]["messages"].append(message)
            self.conversations[conversation_id]["message_count"] += 1
            logger.info(f"Added {role} message to {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            return False
    
    def get_last_messages(self, conversation_id: str, count: int = 8) -> List[Dict]:
        try:
            if conversation_id not in self.conversations:
                return []
            
            messages = self.conversations[conversation_id]["messages"]
            return messages[-count:] if len(messages) > count else messages
        except Exception as e:
            logger.error(f"Failed to retrieve messages: {e}")
            return []
    
    def conversation_exists(self, conversation_id: str) -> bool:
        try:
            return conversation_id in self.conversations
        except Exception as e:
            logger.error(f"Failed to check conversation existence: {e}")
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        try:
            if conversation_id in self.conversations:
                del self.conversations[conversation_id]
                logger.info(f"Deleted conversation with ID: {conversation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False

    def get_all_conversations(self) -> List[str]:
        try:
            conversation_ids = list(self.conversations.keys())
            return sorted(conversation_ids, reverse=True)
        except Exception as e:
            logger.error(f"Failed to retrieve all conversations: {e}")
            return []
    
    def get_conversations_with_titles(self) -> List[Dict]:
        try:
            conversations = []
            for conv_id in sorted(self.conversations.keys(), reverse=True):
                conv_data = self.conversations[conv_id]
                conversations.append({
                    "id": conv_id,
                    "title": conv_data.get("title", "Untitled"),
                    "created_at": conv_data.get("created_at")
                })
            return conversations
        except Exception as e:
            logger.error(f"Failed to retrieve conversations with titles: {e}")
            return []
    
    def get_full_history(self, conversation_id: str) -> List[Dict]:
        try:
            if conversation_id not in self.conversations:
                return []
            
            return self.conversations[conversation_id]["messages"]
        except Exception as e:
            logger.error(f"Failed to retrieve full history: {e}")
            return []
