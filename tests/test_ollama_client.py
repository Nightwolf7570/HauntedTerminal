"""
Tests for the Ollama client.
"""

import pytest
from unittest.mock import Mock, patch
import requests
from hypothesis import given, strategies as st

from src.ollama_client import (
    OllamaClient,
    OllamaConfig,
    OllamaConnectionError,
    OllamaInterpretationError
)


@pytest.fixture
def client():
    """Create an Ollama client for testing."""
    return OllamaClient()


@pytest.fixture
def custom_client():
    """Create an Ollama client with custom config."""
    config = OllamaConfig(
        endpoint="http://localhost:11434",
        model="llama3.2",
        timeout=5
    )
    return OllamaClient(config)


def test_client_initialization_with_defaults(client):
    """Test that client initializes with default configuration."""
    assert client.config.endpoint == "http://localhost:11434"
    assert client.config.model == "llama3.2"
    assert client.config.timeout == 10


def test_client_initialization_with_custom_config(custom_client):
    """Test that client initializes with custom configuration."""
    assert custom_client.config.endpoint == "http://localhost:11434"
    assert custom_client.config.model == "llama3.2"
    assert custom_client.config.timeout == 5


def test_build_prompt_includes_user_input(client):
    """Test that build_prompt includes the user input."""
    user_input = "list all python files"
    prompt = client.build_prompt(user_input)
    
    assert user_input in prompt
    assert "shell command" in prompt.lower()
    assert "User:" in prompt


def test_build_prompt_includes_instructions(client):
    """Test that build_prompt includes interpretation instructions."""
    prompt = client.build_prompt("test command")
    
    assert "shell command" in prompt.lower() or "bash" in prompt.lower()
    assert "Response:" in prompt


@patch('requests.get')
def test_check_connection_success(mock_get, client):
    """Test successful connection check."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    result = client.check_connection()
    
    assert result is True
    mock_get.assert_called_once()


@patch('requests.get')
def test_check_connection_failure_connection_error(mock_get, client):
    """Test connection check with connection error."""
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
    
    with pytest.raises(OllamaConnectionError) as exc_info:
        client.check_connection()
    
    assert "Cannot connect" in str(exc_info.value)
    assert "ollama serve" in str(exc_info.value)


@patch('requests.get')
def test_check_connection_failure_timeout(mock_get, client):
    """Test connection check with timeout."""
    mock_get.side_effect = requests.exceptions.Timeout("Timeout")
    
    with pytest.raises(OllamaConnectionError) as exc_info:
        client.check_connection()
    
    assert "timed out" in str(exc_info.value)


@patch('requests.post')
def test_interpret_command_success(mock_post, client):
    """Test successful command interpretation."""
    mock_response = Mock()
    mock_response.json.return_value = {"response": "ls -la"}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    result = client.interpret_command("list all files")
    
    assert result == "ls -la"
    mock_post.assert_called_once()


@patch('requests.post')
def test_interpret_command_empty_input(mock_post, client):
    """Test interpretation with empty input."""
    with pytest.raises(OllamaInterpretationError) as exc_info:
        client.interpret_command("")
    
    assert "empty input" in str(exc_info.value).lower()
    mock_post.assert_not_called()


@patch('requests.post')
def test_interpret_command_connection_error(mock_post, client):
    """Test interpretation with connection error."""
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection lost")
    
    with pytest.raises(OllamaConnectionError) as exc_info:
        client.interpret_command("test command")
    
    assert "Lost connection" in str(exc_info.value)


@patch('requests.post')
def test_interpret_command_timeout(mock_post, client):
    """Test interpretation with timeout."""
    mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
    
    with pytest.raises(OllamaConnectionError) as exc_info:
        client.interpret_command("test command")
    
    assert "timed out" in str(exc_info.value)


@patch('requests.post')
def test_interpret_command_empty_response(mock_post, client):
    """Test interpretation with empty response from Ollama."""
    mock_response = Mock()
    mock_response.json.return_value = {"response": ""}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    with pytest.raises(OllamaInterpretationError) as exc_info:
        client.interpret_command("test command")
    
    assert "empty command" in str(exc_info.value).lower()


@patch('requests.post')
def test_interpret_command_invalid_response_format(mock_post, client):
    """Test interpretation with invalid response format."""
    mock_response = Mock()
    mock_response.json.return_value = {"invalid": "format"}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    with pytest.raises(OllamaInterpretationError) as exc_info:
        client.interpret_command("test command")
    
    assert "Invalid response format" in str(exc_info.value)


def test_clean_command_removes_markdown(client):
    """Test that _clean_command removes markdown code blocks."""
    command_with_markdown = "```bash\nls -la\n```"
    cleaned = client._clean_command(command_with_markdown)
    
    assert cleaned == "ls -la"
    assert "```" not in cleaned


def test_clean_command_removes_backticks(client):
    """Test that _clean_command removes inline backticks."""
    command_with_backticks = "`ls -la`"
    cleaned = client._clean_command(command_with_backticks)
    
    assert cleaned == "ls -la"
    assert "`" not in cleaned


def test_clean_command_removes_shell_prefixes(client):
    """Test that _clean_command removes common shell prefixes."""
    commands = [
        ("$ ls -la", "ls -la"),
        ("# ls -la", "ls -la"),
        ("> ls -la", "ls -la"),
    ]
    
    for input_cmd, expected in commands:
        cleaned = client._clean_command(input_cmd)
        assert cleaned == expected


@patch('requests.post')
def test_interpret_command_cleans_response(mock_post, client):
    """Test that interpret_command cleans the response."""
    mock_response = Mock()
    mock_response.json.return_value = {"response": "```bash\nls -la\n```"}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    result = client.interpret_command("list files")
    
    assert result == "ls -la"
    assert "```" not in result


@patch('requests.post')
def test_interpret_command_timeout_value(mock_post, client):
    """Test that interpret_command uses configured timeout."""
    mock_response = Mock()
    mock_response.json.return_value = {"response": "ls"}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    client.interpret_command("test")
    
    # Verify timeout was passed to requests
    call_kwargs = mock_post.call_args[1]
    assert call_kwargs['timeout'] == 10


# Property-Based Tests

@given(natural_language=st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()))
def test_property_ollama_request_formation(natural_language):
    """
    Feature: haunted-terminal-cli, Property 3: Ollama request formation
    
    Property: For any valid natural language input, the system should construct 
    and send a properly formatted request to the local Ollama endpoint.
    
    Validates: Requirements 2.1
    """
    with patch('requests.post') as mock_post:
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {"response": "echo test"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        
        # Execute
        try:
            client.interpret_command(natural_language)
        except (OllamaConnectionError, OllamaInterpretationError):
            # These exceptions are acceptable for this property test
            # We're testing request formation, not error handling
            pass
        
        # Verify request was made (if no exception occurred before the request)
        if mock_post.called:
            # Check that the request was made to the correct endpoint
            call_args = mock_post.call_args
            assert call_args is not None
            
            # Verify endpoint URL
            endpoint_url = call_args[0][0]
            assert endpoint_url == "http://localhost:11434/api/generate"
            
            # Verify request payload structure
            request_payload = call_args[1]['json']
            assert 'model' in request_payload
            assert 'prompt' in request_payload
            assert 'stream' in request_payload
            
            # Verify model is set correctly
            assert request_payload['model'] == "llama3.2"
            
            # Verify stream is False
            assert request_payload['stream'] is False
            
            # Verify prompt contains the user input
            assert natural_language in request_payload['prompt']
            
            # Verify timeout is set
            assert 'timeout' in call_args[1]
            assert call_args[1]['timeout'] == 10


@given(
    natural_language=st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()),
    timeout_value=st.integers(min_value=1, max_value=30)
)
def test_property_timeout_enforcement(natural_language, timeout_value):
    """
    Feature: haunted-terminal-cli, Property 4: Timeout enforcement
    
    Property: For any Ollama request, if the response time exceeds the configured
    timeout, the system should timeout and display an error message.
    
    Validates: Requirements 2.2
    """
    with patch('requests.post') as mock_post:
        # Setup mock to raise Timeout exception
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Create client with custom timeout
        config = OllamaConfig(timeout=timeout_value)
        client = OllamaClient(config)
        
        # Execute and verify timeout is handled
        with pytest.raises(OllamaConnectionError) as exc_info:
            client.interpret_command(natural_language)
        
        # Verify the error message mentions timeout
        error_message = str(exc_info.value)
        assert "timed out" in error_message.lower()
        
        # Verify the timeout value is mentioned in the error
        assert str(timeout_value) in error_message
        
        # Verify the request was made with the correct timeout
        if mock_post.called:
            call_kwargs = mock_post.call_args[1]
            assert call_kwargs['timeout'] == timeout_value


# Error Handling Tests (Task 9.3)

@patch('requests.get')
def test_ollama_connection_error_includes_troubleshooting(mock_get, client):
    """
    Test that Ollama connection errors include helpful troubleshooting information.
    
    Validates: Requirements 7.2
    """
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
    
    with pytest.raises(OllamaConnectionError) as exc_info:
        client.check_connection()
    
    error_message = str(exc_info.value)
    
    # Verify error message includes troubleshooting steps
    assert "Cannot connect" in error_message
    assert "ollama serve" in error_message
    assert "Ollama" in error_message


@patch('requests.post')
def test_command_interpretation_error_with_malformed_json(mock_post, client):
    """
    Test that command interpretation handles malformed JSON responses gracefully.
    
    Validates: Requirements 7.2
    """
    mock_response = Mock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    with pytest.raises(OllamaInterpretationError) as exc_info:
        client.interpret_command("test command")
    
    error_message = str(exc_info.value)
    assert "parse" in error_message.lower() or "response" in error_message.lower()


@patch('requests.post')
def test_command_interpretation_error_with_missing_response_field(mock_post, client):
    """
    Test that command interpretation handles missing response field gracefully.
    
    Validates: Requirements 7.2
    """
    mock_response = Mock()
    mock_response.json.return_value = {"error": "Model not found"}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    with pytest.raises(OllamaInterpretationError) as exc_info:
        client.interpret_command("test command")
    
    error_message = str(exc_info.value)
    assert "Invalid response format" in error_message


@patch('requests.post')
def test_command_interpretation_error_provides_helpful_message(mock_post, client):
    """
    Test that interpretation errors provide helpful messages to the user.
    
    Validates: Requirements 7.2
    """
    mock_response = Mock()
    mock_response.json.return_value = {"response": ""}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    with pytest.raises(OllamaInterpretationError) as exc_info:
        client.interpret_command("test command")
    
    error_message = str(exc_info.value)
    
    # Verify error message is helpful
    assert "empty" in error_message.lower()
    assert "rephrase" in error_message.lower() or "request" in error_message.lower()


@patch('requests.post')
def test_connection_lost_during_interpretation_provides_troubleshooting(mock_post, client):
    """
    Test that connection errors during interpretation provide troubleshooting info.
    
    Validates: Requirements 7.2
    """
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection lost")
    
    with pytest.raises(OllamaConnectionError) as exc_info:
        client.interpret_command("test command")
    
    error_message = str(exc_info.value)
    
    # Verify error message includes troubleshooting
    assert "Lost connection" in error_message or "connection" in error_message.lower()
    assert "Ollama" in error_message
    assert "running" in error_message.lower()


@patch('requests.post')
def test_timeout_error_provides_helpful_context(mock_post, client):
    """
    Test that timeout errors provide helpful context about what happened.
    
    Validates: Requirements 7.2
    """
    mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
    
    with pytest.raises(OllamaConnectionError) as exc_info:
        client.interpret_command("test command")
    
    error_message = str(exc_info.value)
    
    # Verify error message provides context
    assert "timed out" in error_message.lower()
    assert "seconds" in error_message.lower()
    # Should mention that it might be processing a complex request
    assert "processing" in error_message.lower() or "complex" in error_message.lower()


# Domain Categorization Tests (Task 14.3)

def test_file_operation_detection_find(client):
    """
    Test that file operation keywords like 'find' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("find all python files")
    assert 'file' in domains


def test_file_operation_detection_list(client):
    """
    Test that file operation keywords like 'list' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("list all files in directory")
    assert 'file' in domains


def test_file_operation_detection_copy(client):
    """
    Test that file operation keywords like 'copy' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("copy files to backup")
    assert 'file' in domains


def test_file_operation_detection_move(client):
    """
    Test that file operation keywords like 'move' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("move old logs to archive")
    assert 'file' in domains


def test_file_operation_detection_multiple_keywords(client):
    """
    Test that multiple file operation keywords are detected.
    
    Validates: Requirements 12.1
    """
    test_cases = [
        "search for files",
        "locate the directory",
        "remove old files",
        "show disk space",
        "check folder size"
    ]
    
    for test_input in test_cases:
        domains = client._categorize_domain(test_input)
        assert 'file' in domains, f"Failed to detect file domain in: {test_input}"


def test_process_operation_detection_kill(client):
    """
    Test that process operation keywords like 'kill' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("kill process 1234")
    assert 'process' in domains


def test_process_operation_detection_stop(client):
    """
    Test that process operation keywords like 'stop' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("stop the running process")
    assert 'process' in domains


def test_process_operation_detection_process(client):
    """
    Test that process operation keywords like 'process' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("show all running processes")
    assert 'process' in domains


def test_process_operation_detection_multiple_keywords(client):
    """
    Test that multiple process operation keywords are detected.
    
    Validates: Requirements 12.1
    """
    test_cases = [
        "terminate the job",
        "show top cpu processes",
        "list background jobs",
        "monitor memory usage",
        "check running programs"
    ]
    
    for test_input in test_cases:
        domains = client._categorize_domain(test_input)
        assert 'process' in domains, f"Failed to detect process domain in: {test_input}"


def test_network_operation_detection_download(client):
    """
    Test that network operation keywords like 'download' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("download file from url")
    assert 'network' in domains


def test_network_operation_detection_fetch(client):
    """
    Test that network operation keywords like 'fetch' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("fetch data from api")
    assert 'network' in domains


def test_network_operation_detection_ping(client):
    """
    Test that network operation keywords like 'ping' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("ping google.com")
    assert 'network' in domains


def test_network_operation_detection_multiple_keywords(client):
    """
    Test that multiple network operation keywords are detected.
    
    Validates: Requirements 12.1
    """
    test_cases = [
        "curl the endpoint",
        "wget the file",
        "check network connection",
        "test http request",
        "show open ports"
    ]
    
    for test_input in test_cases:
        domains = client._categorize_domain(test_input)
        assert 'network' in domains, f"Failed to detect network domain in: {test_input}"


def test_text_processing_detection_search(client):
    """
    Test that text processing keywords like 'search' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("search for pattern in files")
    assert 'text' in domains


def test_text_processing_detection_filter(client):
    """
    Test that text processing keywords like 'filter' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("filter lines containing error")
    assert 'text' in domains


def test_text_processing_detection_replace(client):
    """
    Test that text processing keywords like 'replace' are detected.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("replace old text with new")
    assert 'text' in domains


def test_text_processing_detection_multiple_keywords(client):
    """
    Test that multiple text processing keywords are detected.
    
    Validates: Requirements 12.1
    """
    test_cases = [
        "grep for errors in logs",
        "sort the output",
        "count unique lines",
        "extract first column",
        "find matching patterns"
    ]
    
    for test_input in test_cases:
        domains = client._categorize_domain(test_input)
        assert 'text' in domains, f"Failed to detect text domain in: {test_input}"


def test_multiple_domain_detection(client):
    """
    Test that multiple domains can be detected in a single input.
    
    Validates: Requirements 12.1
    """
    # Input that involves both file and text operations
    domains = client._categorize_domain("search for pattern in all python files")
    assert 'file' in domains
    assert 'text' in domains
    
    # Input that involves network and file operations
    domains = client._categorize_domain("download file and save to directory")
    assert 'network' in domains
    assert 'file' in domains


def test_no_domain_detection(client):
    """
    Test that inputs with no specific domain keywords return empty list.
    
    Validates: Requirements 12.1
    """
    domains = client._categorize_domain("show current time")
    # This should not match any specific domain
    assert len(domains) == 0


def test_case_insensitive_domain_detection(client):
    """
    Test that domain detection is case-insensitive.
    
    Validates: Requirements 12.1
    """
    test_cases = [
        ("FIND all files", 'file'),
        ("Kill Process", 'process'),
        ("DOWNLOAD from URL", 'network'),
        ("SEARCH for pattern", 'text')
    ]
    
    for test_input, expected_domain in test_cases:
        domains = client._categorize_domain(test_input)
        assert expected_domain in domains, f"Failed to detect {expected_domain} in: {test_input}"
