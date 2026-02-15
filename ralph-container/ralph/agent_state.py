from langchain_core.messages.base import BaseMessage
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    AIMessage,
    FunctionMessage,  # Include all types you use
)


from pydantic import BaseModel, Field
from typing import Union, Annotated




# Define the union of allowed message types with a discriminator for efficiency and correctness
MessageType = Annotated[
    Union[
        ToolMessage,
        FunctionMessage,
        AIMessage,
        HumanMessage,
        SystemMessage,
    ],
    Field(discriminator="type"),
]


class ChatHistory(BaseModel):
    messages: list[MessageType] = []
    current_tool_name: str = ""


@dataclass
class WorkContext:
    working_directory: str


class AgentState(BaseModel):
    """
    Represents the state of our graph.

    Attributes:
        messages: The list of messages that have been exchanged in the conversation.
    """

    messages: Annotated[list[AnyMessage], add_messages]

    @classmethod
    def from_chat_history(cls, chat_history: ChatHistory) -> Self:
        """
        Create an AgentState from a ChatHistory-like object.
        """

        # Pass through items; validation will be performed by pydantic on construction.
        return cls(messages=list(chat_history.messages))
