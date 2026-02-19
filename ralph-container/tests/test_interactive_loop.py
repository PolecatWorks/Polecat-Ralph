import os
import click
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from ralph.cli import cli
from langchain_core.messages import AIMessage

def test_interactive_loop_flow():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Setup config and files
        with open("config.yaml", "w") as f:
            f.write("logging:\n  version: 1\n")
        os.makedirs("secrets", exist_ok=True)
        with open("instructions.txt", "w") as f:
            f.write("Original Instruction")
        os.makedirs("workdir", exist_ok=True)

        # Mock Config
        with patch("ralph.config.RalphConfig.from_yaml_and_secrets_dir") as mock_config_cls:
            mock_config_obj = MagicMock()
            mock_config_obj.aiclient.model_provider = "google_genai"
            # Ensure model is a string to pass validation if real class is used (though we mock it)
            mock_config_obj.aiclient.model = "gemini-pro"

            # Return a valid fake key object
            mock_key = MagicMock()
            mock_key.get_secret_value.return_value = "fake"
            mock_config_obj.aiclient.google_api_key = mock_key
            mock_config_cls.return_value = mock_config_obj

            # Mock LLM
            # Important: llm_model in agent.py performs a local import of ChatGoogleGenerativeAI.
            # So we must patch the class in the source module, not ralph.agent.
            with patch("langchain_google_genai.ChatGoogleGenerativeAI") as MockLLMClass:
                mock_llm = MagicMock()
                MockLLMClass.return_value = mock_llm

                mock_llm_with_tools = MagicMock()
                mock_llm.bind_tools.return_value = mock_llm_with_tools

                # Define side effect for LLM invoke
                state = {"calls": 0}

                def llm_invoke_side_effect(messages, config):
                    state["calls"] += 1
                    count = state["calls"]

                    if count == 1:
                        # First call: Agent decides to ask user
                        return AIMessage(content="Thinking...", tool_calls=[
                            {"name": "ask_user", "args": {"question": "Should I update?"}, "id": "call1"}
                        ])
                    elif count == 2:
                        # Second call: Agent decides to update instruction
                        # Previous step was tool execution.
                        return AIMessage(content="Updating...", tool_calls=[
                            {"name": "update_instruction", "args": {"new_instruction": "Updated Instruction"}, "id": "call2"}
                        ])
                    elif count == 3:
                        # Third call: Agent decides to finish
                        return AIMessage(content="Done.", tool_calls=[
                            {"name": "done", "args": {}, "id": "call3"}
                        ])
                    else:
                        return AIMessage(content="Stop")

                mock_llm_with_tools.invoke.side_effect = llm_invoke_side_effect

                # Mock click.prompt to simulate user typing "Yes"
                with patch("click.prompt", return_value="Yes"):
                    # Run the loop command
                    result = runner.invoke(cli, ["loop", "--config", "config.yaml", "--secrets", "secrets", "--limit", "3", "workdir", "instructions.txt"])

                    # Verification inside context manager
                    assert result.exit_code == 0, f"Output: {result.output}"
                    assert "Objective met" in result.output
                    assert "[AGENT ASKS]: Should I update?" in result.output
                    assert "Successfully updated instruction file." in result.output

                    # Check the instruction file in the target directory
                    # Note: run_loop changes CWD to workdir.
                    # Since we are in same process, CWD is now workdir (if run_loop didn't revert it, which it doesn't).
                    # So we should look for prompts/instructions/instructions.txt relative to current CWD.

                    target_file = "prompts/instructions/instructions.txt"

                    # Debug output
                    if not os.path.exists(target_file):
                        # Try finding it relative to original CWD?
                        # But we don't know where we are.
                        print(f"CWD: {os.getcwd()}")
                        print(f"Files: {os.listdir('.')}")
                        if os.path.exists("prompts"):
                             print(f"Prompts: {os.listdir('prompts')}")
                             if os.path.exists("prompts/instructions"):
                                 print(f"Instructions: {os.listdir('prompts/instructions')}")

                    assert os.path.exists(target_file)
                    with open(target_file, "r") as f:
                        content = f.read()
                    assert content == "Updated Instruction"
