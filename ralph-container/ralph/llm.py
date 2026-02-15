from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ralph.config import RalphConfig

def get_chain(config: RalphConfig):
    """
    Creates and returns a simple LangChain chain for answering questions.
    """
    # Initialize the LLM based on provider
    if config.aiclient.model_provider == "ollama":
        llm = ChatOllama(
            model=config.aiclient.model or "llama2", # Default to llama2 if not specified? Or maybe gemma as user mentioned
            base_url=config.aiclient.ollama_base_url,
            temperature=config.aiclient.temperature
        )
    else:
        if not config.aiclient.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set.")

        # Initialize the Google Gemini model
        llm = ChatGoogleGenerativeAI(
            model=config.aiclient.model or "gemini-pro",
            google_api_key=config.aiclient.google_api_key.get_secret_value()
        )

    # Create a simple prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("user", "{question}")
    ])

    # Create the chain
    chain = prompt | llm | StrOutputParser()

    return chain
