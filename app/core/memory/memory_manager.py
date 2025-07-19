from typing import Dict
from langchain.schema import BaseChatMessageHistory  # 替代 langchain_core
from langchain.memory.chat_message_histories import ChatMessageHistory  # 替代 langchain_community

_sessions: Dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in _sessions:
        _sessions[session_id] = ChatMessageHistory()
        print(f"--- New session created: {session_id} ---")
    else:
        print(f"--- Loaded existing session: {session_id} ---")
    return _sessions[session_id]
