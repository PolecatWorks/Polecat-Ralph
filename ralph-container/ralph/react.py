import click
import os
# We will import create_agent later when it is implemented
# from ralph.agent import create_agent

from ralph.config import ralphConfig

def run_react(instruction: str, directory: Path, config: ralphConfig):
    """
    Runs the ralph react.

    Args:
        instruction: The instruction.
        directory: Working directory.
        config: The ralph configuration object.
    """

    # Import locally to avoid circular dependencies

    from ralph.agent import create_react_agent

    # Create a fresh agent for each iteration
    agent = create_react_agent(instruction, directory, config)

    # Run the agent
    result = agent.invoke({"messages": [("user", "Please execute the instruction.")]})

    # Check if the agent signalled 'done'.
    # We look for a ToolMessage with the content "ralph_DONE"
    messages = result.get("messages", [])

    is_done = any(msg.content == "ralph_DONE" for msg in messages)

    if is_done:
        click.echo("Objective met (agent signaled done).")
    else:
        click.echo("Objective not met (agent did not signal done).")
