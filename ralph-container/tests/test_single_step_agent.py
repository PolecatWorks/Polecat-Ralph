
import pytest
from unittest.mock import MagicMock, patch
from ralph.agent import create_single_step_agent
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
import os

class MockConfig:
    class AIClient:
        google_api_key = MagicMock()
        google_api_key.get_secret_value.return_value = "fake_key"
        model = "gemini-pro"
        temperature = 0.0
    aiclient = AIClient()

@patch("ralph.agent.ChatGoogleGenerativeAI")
def test_single_step_agent_no_tool(mock_llm_class):
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm
    mock_llm.invoke.return_value = AIMessage(content="I am done.")
    mock_llm_class.return_value = mock_llm

    config = MockConfig()

    # Create agent
    agent = create_single_step_agent("Say hello", ".", config)

    # Run agent
    result = agent.invoke({"messages": [HumanMessage(content="Start")]})

    # Assertions
    messages = result["messages"]
    # Should have: HumanMessage, AIMessage
    assert len(messages) >= 2
    assert isinstance(messages[-1], AIMessage)
    assert messages[-1].content == "I am done."

    # Ensure it only called invoke once
    assert mock_llm.invoke.call_count == 1

@patch("ralph.agent.ChatGoogleGenerativeAI")
def test_single_step_agent_with_tool(mock_llm_class):
    # Setup mock LLM to return a tool call
    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm

    # Create a mock tool call
    tool_call = {
        "name": "list_files",
        "args": {"path": "."},
        "id": "call_123"
    }

    ai_msg_with_tool = AIMessage(content="Listing files", tool_calls=[tool_call])

    # We want the LLM to be called once, return the tool call,
    # then the graph should execute the tool and STOP.
    # It should NOT loop back to the LLM.
    mock_llm.invoke.return_value = ai_msg_with_tool
    mock_llm_class.return_value = mock_llm

    config = MockConfig()

    # Create agent
    agent = create_single_step_agent("List files", ".", config)

    # Run agent
    result = agent.invoke({"messages": [HumanMessage(content="Start")]})

    # Assertions
    messages = result["messages"]
    # Expect: HumanMessage(Start) -> AIMessage(ToolCall) -> ToolMessage(ToolOutput)

    assert len(messages) >= 3
    assert isinstance(messages[-2], AIMessage)
    assert messages[-2].tool_calls[0]["name"] == "list_files"

    assert isinstance(messages[-1], ToolMessage)
    assert messages[-1].tool_call_id == "call_123"

    # CRITICAL: Verify LLM was invoked ONLY ONCE
    assert mock_llm.invoke.call_count == 1
