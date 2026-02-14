import pytest
from unittest.mock import MagicMock, patch
from ralph.graph import run_graph
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
import os

# Mock the agent's behavior
def test_run_loop_iterations():
    # Patch create_single_step_agent because that is what run_graph calls
    with patch("ralph.agent.create_single_step_agent") as mock_create_agent:
        mock_agent = MagicMock()

        # Setup mock return value for invoke
        # We want to simulate state updates.
        # First call: returns messages with AIMessage.
        # Second call: returns messages with another AIMessage.

        # The agent returns a dict with "messages".
        # run_graph uses result.get("messages", []) to update its local state.

        # First iteration:
        # Input: [UserMessage]
        # Output: [UserMessage, AIMessage1]

        # Second iteration:
        # Input: [UserMessage, AIMessage1]
        # Output: [UserMessage, AIMessage1, AIMessage2]

        msg1 = AIMessage(content="I am working step 1")
        msg2 = AIMessage(content="I am working step 2")

        user_msg = ("user", "Please execute the instruction.") # This matches what's in graph.py

        # We can simulate the side effect of invoke to return accumulated messages
        # But since run_graph passes the *entire* history to invoke,
        # and invoke returns the *entire* history (conceptually in StateGraph),
        # we can just return the input + new message.

        def side_effect(state):
            current_messages = state["messages"]
            # If length is 1 (just user), return user + msg1
            if len(current_messages) == 1:
                return {"messages": current_messages + [msg1]}
            # If length is 2 (user + msg1), return user + msg1 + msg2
            elif len(current_messages) == 2:
                return {"messages": current_messages + [msg2]}
            return {"messages": current_messages}

        mock_agent.invoke.side_effect = side_effect
        mock_create_agent.return_value = mock_agent

        # Mock ralphConfig
        mock_config = MagicMock()

        # Create a dummy instruction file
        instruction_file = "test_instruction.txt"
        with open(instruction_file, "w") as f:
            f.write("Do something")

        try:
            # Run loop for 2 iterations
            run_graph(instruction_file, ".", 2, mock_config)

            # Verify create_agent was called ONLY ONCE
            assert mock_create_agent.call_count == 1

            # Verify create_agent was called with correct args
            mock_create_agent.assert_called_with(instruction_file, ".", mock_config)

            # Verify invoke was called twice
            assert mock_agent.invoke.call_count == 2

            # Verify the calls passed the correct history
            # Call 1: {"messages": [("user", ...)]}
            args1, _ = mock_agent.invoke.call_args_list[0]
            assert len(args1[0]["messages"]) == 1

            # Call 2: {"messages": [("user", ...), msg1]}
            args2, _ = mock_agent.invoke.call_args_list[1]
            assert len(args2[0]["messages"]) == 2
            assert args2[0]["messages"][1] == msg1

        finally:
            if os.path.exists(instruction_file):
                os.remove(instruction_file)

def test_run_loop_done_signal():
    with patch("ralph.agent.create_single_step_agent") as mock_create_agent:
        mock_agent = MagicMock()

        # Setup mock return value to simulate done signal in first iteration
        # The loop checks for ToolMessage with content "ralph_DONE"
        done_message = ToolMessage(content="ralph_DONE", tool_call_id="1", name="done_tool")

        # We need to return a structure that looks like messages.
        # graph.py looks at messages[-2:]

        def side_effect(state):
            current_messages = state["messages"]
            return {"messages": current_messages + [AIMessage(content="Calling done"), done_message]}

        mock_agent.invoke.side_effect = side_effect
        mock_create_agent.return_value = mock_agent

        # Mock ralphConfig
        mock_config = MagicMock()

        # Create a dummy instruction file
        instruction_file = "test_instruction_done.txt"
        with open(instruction_file, "w") as f:
            f.write("Do something")

        try:
            # Run loop with limit 5, but should stop after 1
            run_graph(instruction_file, ".", 5, mock_config)

            # Verify create_agent was called only once
            assert mock_create_agent.call_count == 1

            # Verify invoke called only once because it breaks on done
            assert mock_agent.invoke.call_count == 1

        finally:
            if os.path.exists(instruction_file):
                os.remove(instruction_file)
