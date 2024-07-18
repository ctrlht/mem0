import pytest
from unittest.mock import Mock, patch
from mem0.llms.openai import OpenAILLM

@pytest.fixture
def mock_openai_client():
    with patch('mem0.llms.openai.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        yield mock_client


def test_generate_response_without_tools(mock_openai_client):
    llm = OpenAILLM()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="I'm doing well, thank you for asking!"))]
    mock_openai_client.chat.completions.create.return_value = mock_response

    response = llm.generate_response(messages)

    mock_openai_client.chat.completions.create.assert_called_once_with(
        model="gpt-4o",
        messages=messages
    )
    assert response == "I'm doing well, thank you for asking!"
    

def test_generate_response_with_tools(mock_openai_client):
    llm = OpenAILLM()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Add a new memory: Today is a sunny day."}
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_memory",
                "description": "Add a memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "Data to add to memory"}
                    },
                    "required": ["data"],
                },
            },
        }
    ]
    
    mock_response = Mock()
    mock_message = Mock()
    mock_message.content = "I've added the memory for you."
    
    mock_tool_call = Mock()
    mock_tool_call.function.name = "add_memory"
    mock_tool_call.function.arguments = '{"data": "Today is a sunny day."}'
    
    mock_message.tool_calls = [mock_tool_call]
    mock_response.choices = [Mock(message=mock_message)]
    mock_openai_client.chat.completions.create.return_value = mock_response

    response = llm.generate_response(messages, tools=tools)

    mock_openai_client.chat.completions.create.assert_called_once_with(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    assert response["content"] == "I've added the memory for you."
    assert len(response["tool_calls"]) == 1
    assert response["tool_calls"][0]["name"] == "add_memory"
    assert response["tool_calls"][0]["arguments"] == {'data': 'Today is a sunny day.'}
    