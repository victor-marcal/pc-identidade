import pytest
from datetime import datetime
from app.api.v1.schemas.gemini_schema import ChatRequest, ChatResponse, MessageItem, ChatHistoryResponse

HELLO = "Hello!"

def test_chat_request_valid():
    data = {"text": "Hello, how are you?"}
    chat_request = ChatRequest(**data)
    assert chat_request.text == "Hello, how are you?"


def test_chat_request_invalid():
    with pytest.raises(ValueError):
        ChatRequest(text="")


def test_chat_response():
    data = {"response": "I'm fine, thank you!", "timestamp": datetime.now()}
    chat_response = ChatResponse(**data)
    assert chat_response.response == "I'm fine, thank you!"
    assert isinstance(chat_response.timestamp, datetime)


def test_message_item():
    data = {
        "message_type": "user",
        "content": HELLO,
        "timestamp": datetime.now()
    }
    message_item = MessageItem(**data)
    assert message_item.message_type == "user"
    assert message_item.content == HELLO
    assert isinstance(message_item.timestamp, datetime)


def test_chat_history_response():
    messages = [
        MessageItem(message_type="user", content="Hi!", timestamp=datetime.now()),
        MessageItem(message_type="assistant", content=HELLO, timestamp=datetime.now())
    ]
    data = {"messages": messages, "total": 2}
    chat_history = ChatHistoryResponse(**data)
    assert len(chat_history.messages) == 2
    assert chat_history.total == 2
