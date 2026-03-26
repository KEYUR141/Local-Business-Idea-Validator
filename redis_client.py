import redis 
import json
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RedisConversationManager:

    def __init__(self, redis_url:str = "redis://localhost:6379/0"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            logger.info(f"Connected to Redis at {redis_url}")
        
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Failed to connect to Redis: {e}")
        
    def create_conversation(self, conversation_id:str) -> bool:
        try:
            key = f"Conversation:{conversation_id}"
            metadata = {
                "created_at": datetime.now().isoformat(),
                "message_count": 0
            }
            
            self.redis_client.hset(key, mapping=metadata)
            self.redis_client.expire(key, 86400)
            logger.info(f"Created new conversation with ID: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            return False
            
    def add_message(self, conversation_id:str, role:str, context:str) -> bool:
        try:
            key = f"Conversation:{conversation_id}"
            message = {
                "role": role,
                'content': context,
                "timestamp": datetime.now().isoformat()
            }
            self.redis_client.lpush(key, json.dumps(message))
            self.redis_client.expire(key, 86400)
            logger.info(f"Added {role} message to {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            return False
        
    def get_last_messages(self, conversation_id:str, count: int = 8) -> List[Dict]:
        try:
            key = f"Conversation:{conversation_id}"
            messages_json = self.redis_client.lrange(key, 0, count-1)
            messages = [json.loads(msg) for msg in messages_json]
            messages.reverse()
            return messages
        
        except Exception as e:
            logger.error(f"Failed to retrieve messages: {e}")
            return []
            
    def conversation_exists(self, conversation_id:str) -> bool:
        try:
            key = f"Conversation:{conversation_id}"
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check conversation existence: {e}")
            return False
    
    def delete_conversation(self, conversation_id:str) -> bool:
        try:
            key = f"Conversation:{conversation_id}"
            result = self.redis_client.delete(key)
            if result > 0:
                logger.info(f"Deleted conversation with ID: {conversation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False

    def get_all_conversations(self) -> List[str]:
        try:
            keys = self.redis_client.keys("Conversation:*")
            conversation_ids = [key.replace("Conversation:", "") for key in keys]
            return sorted(conversation_ids, reverse=True)
        except Exception as e:
            logger.error(f"Failed to retrieve all conversations: {e}")
            return []
        
    def get_full_history(self, conversation_id:str) -> List[Dict]:
        try:
            key = f"Conversation:{conversation_id}"
            messages_json = self.redis_client.lrange(key, 0,-1)
            messages = [json.loads(msg) for msg in messages_json]
            messages.reverse()
            return messages
        
        except Exception as e:
            logger.error(f"Failed to retrieve full history: {e}")
            return []