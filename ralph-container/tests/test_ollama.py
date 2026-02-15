from unittest.mock import patch, MagicMock
from ralph.llm import get_chain
from ralph.agent import _initialize_agent_context

def test_get_chain_ollama():
    # Mock ralphConfig
    mock_config = MagicMock()
    mock_config.aiclient.model_provider = "ollama"
    mock_config.aiclient.model = "llama2"
    mock_config.aiclient.ollama_base_url = "http://localhost:11434"
    mock_config.aiclient.temperature = 0.5

    with patch("ralph.llm.ChatOllama") as mock_ollama_class:
        mock_ollama_instance = MagicMock()
        mock_ollama_class.return_value = mock_ollama_instance

        chain = get_chain(mock_config)

        assert chain is not None
        mock_ollama_class.assert_called_once_with(
            model="llama2",
            base_url="http://localhost:11434",
            temperature=0.5
        )

def test_agent_init_ollama():
    # Mock ralphConfig
    mock_config = MagicMock()
    mock_config.aiclient.model_provider = "ollama"
    mock_config.aiclient.model = "gemma2"
    mock_config.aiclient.ollama_base_url = "http://host.docker.internal:11434"
    mock_config.aiclient.temperature = 0.7
    mock_config.aiclient.google_api_key = None # Should not be checked

    with patch("ralph.agent.ChatOllama") as mock_ollama_class:
        mock_ollama_instance = MagicMock()
        mock_ollama_class.return_value = mock_ollama_instance

        # Patch exists to avoid reading prompts for now
        with patch("os.path.exists", return_value=False):
             llm, tools, system_prompt = _initialize_agent_context("instruction", "/tmp", mock_config)

        assert llm == mock_ollama_instance
        mock_ollama_class.assert_called_once_with(
            model="gemma2",
            base_url="http://host.docker.internal:11434",
            temperature=0.7
        )
