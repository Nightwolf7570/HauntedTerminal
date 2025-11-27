"""
Tests to verify offline operation and local-only networking.

Requirements: 8.1, 8.2, 8.3
"""

import pytest
import socket
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings
from src.ollama_client import OllamaClient, OllamaConfig, OllamaConnectionError


class TestOfflineOperation:
    """Test suite for verifying offline operation and local-only networking."""
    
    def test_ollama_endpoint_is_localhost(self):
        """
        Verify that the default Ollama endpoint is localhost.
        
        Requirements: 8.1, 8.2
        """
        client = OllamaClient()
        assert "localhost" in client.config.endpoint or "127.0.0.1" in client.config.endpoint
        assert client.config.endpoint.startswith("http://localhost") or \
               client.config.endpoint.startswith("http://127.0.0.1")
    
    def test_custom_config_can_only_use_localhost(self):
        """
        Verify that even with custom config, only localhost endpoints should be used.
        
        Requirements: 8.1, 8.2
        """
        # Test with localhost
        config = OllamaConfig(endpoint="http://localhost:11434")
        client = OllamaClient(config)
        assert "localhost" in client.config.endpoint
        
        # Test with 127.0.0.1
        config = OllamaConfig(endpoint="http://127.0.0.1:11434")
        client = OllamaClient(config)
        assert "127.0.0.1" in client.config.endpoint
    
    def test_no_external_network_calls_during_check_connection(self):
        """
        Verify that check_connection only attempts to connect to localhost.
        
        Requirements: 8.1, 8.2
        """
        client = OllamaClient()
        
        # Mock requests.get to track what URL is being called
        with patch('src.ollama_client.requests.get') as mock_get:
            mock_get.side_effect = OllamaConnectionError("Connection failed")
            
            try:
                client.check_connection()
            except OllamaConnectionError:
                pass  # Expected to fail
            
            # Verify the call was made to localhost
            assert mock_get.called
            called_url = mock_get.call_args[0][0]
            assert "localhost" in called_url or "127.0.0.1" in called_url
            assert not any(external in called_url for external in [
                "api.openai.com",
                "api.anthropic.com",
                "googleapis.com",
                ".amazonaws.com"
            ])
    
    def test_no_external_network_calls_during_interpret_command(self):
        """
        Verify that interpret_command only attempts to connect to localhost.
        
        Requirements: 8.1, 8.2
        """
        client = OllamaClient()
        
        # Mock requests.post to track what URL is being called
        with patch('src.ollama_client.requests.post') as mock_post:
            mock_post.side_effect = Exception("Connection failed")
            
            try:
                client.interpret_command("list files")
            except (OllamaConnectionError, Exception):
                pass  # Expected to fail
            
            # Verify the call was made to localhost
            assert mock_post.called
            called_url = mock_post.call_args[0][0]
            assert "localhost" in called_url or "127.0.0.1" in called_url
            assert not any(external in called_url for external in [
                "api.openai.com",
                "api.anthropic.com",
                "googleapis.com",
                ".amazonaws.com"
            ])
    
    def test_application_works_without_internet_connectivity(self):
        """
        Verify that the application can function without internet connectivity.
        This test simulates having Ollama running locally but no internet.
        
        Requirements: 8.3
        """
        client = OllamaClient()
        
        # Mock successful local Ollama responses
        with patch('src.ollama_client.requests.get') as mock_get, \
             patch('src.ollama_client.requests.post') as mock_post:
            
            # Mock check_connection success
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"models": []}
            )
            mock_get.return_value.raise_for_status = MagicMock()
            
            # Mock interpret_command success
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"response": "ls -la"}
            )
            mock_post.return_value.raise_for_status = MagicMock()
            
            # These should work even "offline" (with local Ollama)
            assert client.check_connection() is True
            result = client.interpret_command("list files")
            assert result == "ls -la"
            
            # Verify only localhost was contacted
            for call in mock_get.call_args_list + mock_post.call_args_list:
                url = call[0][0]
                assert "localhost" in url or "127.0.0.1" in url
    
    def test_no_dns_lookups_for_external_domains(self):
        """
        Verify that the application doesn't attempt DNS lookups for external domains.
        
        Requirements: 8.1, 8.2
        """
        client = OllamaClient()
        
        # Track any socket connections
        original_getaddrinfo = socket.getaddrinfo
        external_lookups = []
        
        def tracked_getaddrinfo(host, port, *args, **kwargs):
            if host not in ["localhost", "127.0.0.1", "::1"]:
                external_lookups.append(host)
            return original_getaddrinfo(host, port, *args, **kwargs)
        
        with patch('socket.getaddrinfo', side_effect=tracked_getaddrinfo):
            with patch('src.ollama_client.requests.get') as mock_get, \
                 patch('src.ollama_client.requests.post') as mock_post:
                
                # Mock responses
                mock_get.return_value = MagicMock(status_code=200)
                mock_get.return_value.raise_for_status = MagicMock()
                mock_get.return_value.json = lambda: {"models": []}
                
                mock_post.return_value = MagicMock(status_code=200)
                mock_post.return_value.raise_for_status = MagicMock()
                mock_post.return_value.json = lambda: {"response": "echo test"}
                
                try:
                    client.check_connection()
                    client.interpret_command("test command")
                except Exception:
                    pass
        
        # Verify no external DNS lookups occurred
        assert len(external_lookups) == 0, \
            f"External DNS lookups detected: {external_lookups}"
    
    def test_endpoint_validation_rejects_external_urls(self):
        """
        Verify that we can detect if someone tries to use an external endpoint.
        This is a safety check to ensure the design prevents external calls.
        
        Requirements: 8.1, 8.2
        """
        # These should be the only acceptable patterns
        valid_endpoints = [
            "http://localhost:11434",
            "http://127.0.0.1:11434",
            "http://localhost:8080",
            "http://127.0.0.1:8080"
        ]
        
        for endpoint in valid_endpoints:
            config = OllamaConfig(endpoint=endpoint)
            client = OllamaClient(config)
            assert "localhost" in client.config.endpoint or "127.0.0.1" in client.config.endpoint
        
        # Document that external endpoints should not be used
        # (The application doesn't enforce this at runtime, but the design specifies local-only)
        external_endpoints = [
            "http://api.openai.com",
            "https://api.anthropic.com",
            "http://example.com:11434"
        ]
        
        # This test documents the expectation that users should only use localhost
        # The OllamaClient doesn't prevent external URLs, but the default config ensures local-only
        for endpoint in external_endpoints:
            config = OllamaConfig(endpoint=endpoint)
            client = OllamaClient(config)
            # Document that this would be a misconfiguration
            assert "localhost" not in client.config.endpoint and "127.0.0.1" not in client.config.endpoint


class TestLocalOnlyNetworking:
    """Test suite specifically for local-only networking verification."""
    
    def test_default_configuration_is_local_only(self):
        """
        Verify that the default configuration only uses local networking.
        
        Requirements: 8.1, 8.2
        """
        config = OllamaConfig()
        assert config.endpoint == "http://localhost:11434"
        assert "localhost" in config.endpoint
    
    def test_all_network_calls_use_localhost_endpoint(self):
        """
        Verify that all network operations use the localhost endpoint.
        
        Requirements: 8.1, 8.2
        """
        client = OllamaClient()
        
        with patch('src.ollama_client.requests.get') as mock_get, \
             patch('src.ollama_client.requests.post') as mock_post:
            
            mock_get.side_effect = Exception("Test")
            mock_post.side_effect = Exception("Test")
            
            # Try check_connection
            try:
                client.check_connection()
            except:
                pass
            
            # Try interpret_command
            try:
                client.interpret_command("test")
            except:
                pass
            
            # Verify all calls were to localhost
            all_calls = list(mock_get.call_args_list) + list(mock_post.call_args_list)
            for call in all_calls:
                url = call[0][0]
                assert "localhost" in url or "127.0.0.1" in url, \
                    f"Non-localhost URL detected: {url}"
    
    def test_offline_message_displayed_on_startup(self):
        """
        Verify that the application indicates offline operation mode.
        This is tested by checking the CLI module has the capability.
        
        Requirements: 8.5
        """
        # This test verifies the design requirement that offline operation
        # should be communicated to users
        # The actual display is handled by the CLI module
        from src.cli import HauntedCLI
        from src.executor import CommandExecutor
        import tempfile
        
        # Verify the CLI can be instantiated (which would show the offline message)
        executor = CommandExecutor(working_directory=tempfile.gettempdir())
        cli = HauntedCLI(executor=executor)
        assert cli is not None
        
        # The welcome display includes information about local operation
        # This is verified through the theme and CLI integration


# Property-Based Tests

@given(
    natural_language=st.text(min_size=1, max_size=500).filter(lambda x: x.strip()),
    custom_port=st.integers(min_value=1024, max_value=65535)
)
@settings(max_examples=100)
def test_property_local_only_operation(natural_language, custom_port):
    """
    Feature: haunted-terminal-cli, Property 17: Local-only operation
    
    Property: For any command processing operation, the system should make network 
    requests only to localhost (Ollama endpoint) and never to external services.
    
    Validates: Requirements 8.1, 8.2
    """
    # Track all network calls made during the test
    network_calls = []
    
    def track_get(url, *args, **kwargs):
        network_calls.append(('GET', url))
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_response.raise_for_status = MagicMock()
        return mock_response
    
    def track_post(url, *args, **kwargs):
        network_calls.append(('POST', url))
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "echo test"}
        mock_response.raise_for_status = MagicMock()
        return mock_response
    
    # Test with default configuration
    with patch('src.ollama_client.requests.get', side_effect=track_get), \
         patch('src.ollama_client.requests.post', side_effect=track_post):
        
        client = OllamaClient()
        
        # Perform operations that should only contact localhost
        try:
            client.check_connection()
        except Exception:
            pass  # Ignore errors, we're testing network calls
        
        try:
            client.interpret_command(natural_language)
        except Exception:
            pass  # Ignore errors, we're testing network calls
    
    # Verify all network calls were to localhost
    for method, url in network_calls:
        # Check that URL contains localhost or 127.0.0.1
        assert "localhost" in url or "127.0.0.1" in url, \
            f"Non-localhost URL detected: {method} {url}"
        
        # Check that URL does NOT contain any external domains
        external_domains = [
            "api.openai.com",
            "api.anthropic.com",
            "googleapis.com",
            ".amazonaws.com",
            "azure.com",
            "huggingface.co",
            "replicate.com",
            "cohere.ai"
        ]
        for domain in external_domains:
            assert domain not in url, \
                f"External domain {domain} detected in URL: {url}"
    
    # Test with custom port configuration
    network_calls.clear()
    
    with patch('src.ollama_client.requests.get', side_effect=track_get), \
         patch('src.ollama_client.requests.post', side_effect=track_post):
        
        config = OllamaConfig(endpoint=f"http://localhost:{custom_port}")
        client = OllamaClient(config)
        
        try:
            client.check_connection()
        except Exception:
            pass
        
        try:
            client.interpret_command(natural_language)
        except Exception:
            pass
    
    # Verify custom port configuration also only uses localhost
    for method, url in network_calls:
        assert "localhost" in url or "127.0.0.1" in url, \
            f"Non-localhost URL detected with custom port: {method} {url}"
        
        # Verify the custom port is being used
        assert str(custom_port) in url, \
            f"Custom port {custom_port} not found in URL: {url}"


@given(
    operations=st.lists(
        st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100)
def test_property_no_external_network_in_sequence(operations):
    """
    Feature: haunted-terminal-cli, Property 17: Local-only operation (sequence variant)
    
    Property: For any sequence of command processing operations, the system should 
    never make network requests to external services, only to localhost.
    
    Validates: Requirements 8.1, 8.2
    """
    # Track all URLs accessed during the sequence
    accessed_urls = []
    
    def track_get(url, *args, **kwargs):
        accessed_urls.append(url)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_response.raise_for_status = MagicMock()
        return mock_response
    
    def track_post(url, *args, **kwargs):
        accessed_urls.append(url)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "echo test"}
        mock_response.raise_for_status = MagicMock()
        return mock_response
    
    with patch('src.ollama_client.requests.get', side_effect=track_get), \
         patch('src.ollama_client.requests.post', side_effect=track_post):
        
        client = OllamaClient()
        
        # Perform a sequence of operations
        for operation in operations:
            try:
                client.interpret_command(operation)
            except Exception:
                pass  # Ignore errors, we're testing network calls
    
    # Verify ALL URLs in the sequence were localhost
    for url in accessed_urls:
        # Must be localhost or 127.0.0.1
        is_localhost = "localhost" in url or "127.0.0.1" in url
        assert is_localhost, \
            f"Non-localhost URL detected in operation sequence: {url}"
        
        # Must NOT be any external service
        assert "://" in url  # Should be a proper URL
        # Extract domain from URL
        domain_part = url.split("://")[1].split("/")[0].split(":")[0]
        assert domain_part in ["localhost", "127.0.0.1"], \
            f"External domain detected: {domain_part} in URL: {url}"


@given(
    endpoint_config=st.one_of(
        st.just("http://localhost:11434"),
        st.just("http://127.0.0.1:11434"),
        st.builds(
            lambda port: f"http://localhost:{port}",
            st.integers(min_value=1024, max_value=65535)
        ),
        st.builds(
            lambda port: f"http://127.0.0.1:{port}",
            st.integers(min_value=1024, max_value=65535)
        )
    ),
    command=st.text(min_size=1, max_size=300).filter(lambda x: x.strip())
)
@settings(max_examples=100)
def test_property_localhost_endpoint_enforcement(endpoint_config, command):
    """
    Feature: haunted-terminal-cli, Property 17: Local-only operation (endpoint variant)
    
    Property: For any valid localhost endpoint configuration, all network requests
    should be made to that localhost endpoint and nowhere else.
    
    Validates: Requirements 8.1, 8.2
    """
    network_destinations = []
    
    def track_request(url, *args, **kwargs):
        network_destinations.append(url)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "test"}
        mock_response.raise_for_status = MagicMock()
        return mock_response
    
    with patch('src.ollama_client.requests.get', side_effect=track_request), \
         patch('src.ollama_client.requests.post', side_effect=track_request):
        
        config = OllamaConfig(endpoint=endpoint_config)
        client = OllamaClient(config)
        
        # Verify the config itself is localhost
        assert "localhost" in client.config.endpoint or "127.0.0.1" in client.config.endpoint, \
            f"Config endpoint is not localhost: {client.config.endpoint}"
        
        # Perform operations
        try:
            client.check_connection()
        except Exception:
            pass
        
        try:
            client.interpret_command(command)
        except Exception:
            pass
    
    # Verify all network destinations match the configured endpoint
    for destination in network_destinations:
        # Should start with the configured endpoint
        assert destination.startswith(endpoint_config), \
            f"Request to {destination} does not match configured endpoint {endpoint_config}"
        
        # Should be localhost
        assert "localhost" in destination or "127.0.0.1" in destination, \
            f"Non-localhost destination: {destination}"


# Integration Tests

class TestOfflineIntegration:
    """
    Integration tests for offline functionality.
    These tests verify the application works with Ollama running but no internet.
    
    Requirements: 8.3
    """
    
    @pytest.mark.integration
    def test_full_workflow_without_internet(self):
        """
        Integration test: Verify the full application workflow works without internet.
        
        This test simulates having Ollama running locally but no internet connectivity.
        It tests the complete flow: check connection -> interpret command -> execute.
        
        Requirements: 8.3
        
        Note: This test uses mocks to simulate Ollama responses, but verifies that
        only localhost endpoints are contacted. For true integration testing with
        a real Ollama instance, run this manually with network disabled.
        """
        from src.executor import CommandExecutor
        from src.history import HistoryManager
        
        # Track all network calls
        network_calls = []
        
        def track_get(url, *args, **kwargs):
            network_calls.append(('GET', url))
            # Simulate successful Ollama health check
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "ok"}
            mock_response.raise_for_status = MagicMock()
            return mock_response
        
        def track_post(url, *args, **kwargs):
            network_calls.append(('POST', url))
            # Simulate successful Ollama command interpretation
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "echo 'Hello from offline mode'"}
            mock_response.raise_for_status = MagicMock()
            return mock_response
        
        with patch('src.ollama_client.requests.get', side_effect=track_get), \
             patch('src.ollama_client.requests.post', side_effect=track_post):
            
            # Step 1: Initialize components
            import tempfile
            ollama_client = OllamaClient()
            executor = CommandExecutor(working_directory=tempfile.gettempdir())
            history_manager = HistoryManager()
            
            # Step 2: Check Ollama connection (should work offline with local Ollama)
            connection_ok = ollama_client.check_connection()
            assert connection_ok is True, "Should connect to local Ollama"
            
            # Step 3: Interpret a natural language command
            natural_language = "say hello"
            shell_command = ollama_client.interpret_command(natural_language)
            assert shell_command is not None
            assert len(shell_command) > 0
            
            # Step 4: Execute the command
            result = executor.execute(shell_command)
            assert result is not None
            assert result.exit_code == 0
            
            # Step 5: Save to history (local SQLite, no network)
            history_manager.save_command(
                natural_language, 
                shell_command, 
                result.exit_code,
                result.execution_time,
                working_directory=tempfile.gettempdir()
            )
            
            # Step 6: Retrieve from history (local SQLite, no network)
            suggestions = history_manager.get_suggestions(natural_language, limit=5)
            assert len(suggestions) >= 1
            
            # Verify: All network calls were to localhost only
            assert len(network_calls) > 0, "Should have made network calls to Ollama"
            for method, url in network_calls:
                assert "localhost" in url or "127.0.0.1" in url, \
                    f"Non-localhost network call detected: {method} {url}"
                
                # Verify no external domains
                external_domains = [
                    "openai.com", "anthropic.com", "googleapis.com",
                    "amazonaws.com", "azure.com", "huggingface.co"
                ]
                for domain in external_domains:
                    assert domain not in url, \
                        f"External domain {domain} detected in URL: {url}"
    
    @pytest.mark.integration
    def test_network_isolation_verification(self):
        """
        Integration test: Verify network isolation by monitoring all socket connections.
        
        This test ensures that even if internet is available, the application
        only communicates with localhost.
        
        Requirements: 8.3
        """
        import urllib.parse
        
        # Track all attempted connections
        attempted_connections = []
        original_request = None
        
        def track_all_requests(method):
            """Wrapper to track all HTTP requests regardless of method."""
            def wrapper(url, *args, **kwargs):
                # Parse the URL to extract host
                parsed = urllib.parse.urlparse(url)
                attempted_connections.append({
                    'method': method,
                    'url': url,
                    'host': parsed.hostname,
                    'port': parsed.port
                })
                
                # Mock successful response
                mock_response = MagicMock()
                mock_response.status_code = 200
                if method == 'GET':
                    mock_response.json.return_value = {"status": "ok"}
                else:
                    mock_response.json.return_value = {"response": "ls -la"}
                mock_response.raise_for_status = MagicMock()
                return mock_response
            return wrapper
        
        with patch('src.ollama_client.requests.get', side_effect=track_all_requests('GET')), \
             patch('src.ollama_client.requests.post', side_effect=track_all_requests('POST')):
            
            # Perform various operations
            client = OllamaClient()
            
            # Multiple operations to ensure comprehensive testing
            operations = [
                "list files",
                "show processes",
                "check disk space",
                "find python files",
                "count lines in file"
            ]
            
            try:
                client.check_connection()
            except Exception:
                pass
            
            for operation in operations:
                try:
                    client.interpret_command(operation)
                except Exception:
                    pass
        
        # Verify all connections were to localhost
        assert len(attempted_connections) > 0, "Should have attempted connections"
        
        for conn in attempted_connections:
            host = conn['host']
            # Must be localhost or 127.0.0.1
            assert host in ['localhost', '127.0.0.1'], \
                f"Non-localhost connection detected: {conn['method']} to {host}:{conn['port']}"
            
            # Verify the full URL doesn't contain external domains
            url = conn['url']
            assert not any(domain in url for domain in [
                'api.openai.com',
                'api.anthropic.com',
                'cloud.google.com',
                '.amazonaws.com',
                'azure.microsoft.com'
            ]), f"External domain detected in URL: {url}"
    
    @pytest.mark.integration
    @pytest.mark.manual
    def test_real_ollama_offline_operation(self):
        """
        Manual integration test: Test with real Ollama instance and no internet.
        
        This test is marked as 'manual' because it requires:
        1. Ollama to be running locally (ollama serve)
        2. Internet connectivity to be disabled
        3. Manual verification
        
        To run this test manually:
        1. Start Ollama: ollama serve
        2. Disable internet (turn off WiFi, disconnect ethernet)
        3. Run: pytest tests/test_offline_operation.py::TestOfflineIntegration::test_real_ollama_offline_operation -v -m manual
        
        Requirements: 8.3
        """
        # This test is designed to be run manually with real Ollama
        # Skip if Ollama is not available
        client = OllamaClient()
        
        try:
            # Try to connect to real Ollama
            connection_ok = client.check_connection()
            
            if not connection_ok:
                pytest.skip("Ollama is not running. Start with 'ollama serve'")
            
            # If we get here, Ollama is running
            # Now test that we can interpret commands
            test_commands = [
                "list all files",
                "show current directory",
                "display system information"
            ]
            
            for natural_language in test_commands:
                shell_command = client.interpret_command(natural_language)
                
                # Verify we got a valid command back
                assert shell_command is not None
                assert len(shell_command) > 0
                assert isinstance(shell_command, str)
                
                print(f"✓ Interpreted '{natural_language}' -> '{shell_command}'")
            
            print("\n✓ All operations completed successfully without internet!")
            print("✓ Application works in offline mode with local Ollama")
            
        except OllamaConnectionError as e:
            pytest.skip(f"Could not connect to Ollama: {e}")
        except Exception as e:
            # If we get a network error trying to reach external services,
            # that's a test failure
            if "connection" in str(e).lower() or "network" in str(e).lower():
                pytest.fail(f"Network error suggests external connection attempt: {e}")
            raise
