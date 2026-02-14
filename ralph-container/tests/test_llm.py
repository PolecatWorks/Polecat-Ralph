from unittest.mock import patch, MagicMock
import pytest
from ralph.llm import get_chain

def test_get_chain_no_api_key():
    # Mock ralphConfig
    mock_config = MagicMock()
    mock_config.aiclient.google_api_key = None

    with pytest.raises(ValueError, match="GOOGLE_API_KEY environment variable is not set"):
        get_chain(mock_config)

def test_get_chain_success():
    # Mock ralphConfig
    mock_config = MagicMock()
    # Configure the mock to return "dummy_key" when get_secret_value is called
    mock_config.aiclient.google_api_key.get_secret_value.return_value = "dummy_key"
    mock_config.aiclient.model = "gemini-pro"

    # We also need to patch ChatGoogleGenerativeAI to verify initialization
    with patch("ralph.llm.ChatGoogleGenerativeAI") as mock_llm_class:
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance

        chain = get_chain(mock_config)

        # Verify that chain is constructed
        assert chain is not None

        # Verify LLM was initialized with the key
        mock_llm_class.assert_called_once_with(
            model="gemini-pro",
            google_api_key="dummy_key"
        )
