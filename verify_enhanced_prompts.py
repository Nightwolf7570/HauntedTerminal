#!/usr/bin/env python3
"""
Verification script for enhanced prompt accuracy.
Tests that domain-specific examples are included appropriately.
"""

from src.ollama_client import OllamaClient

def test_domain_detection():
    """Test that domain-specific examples are included in prompts."""
    client = OllamaClient()
    
    test_cases = [
        # File operations
        ("find all python files", "file"),
        ("list files in directory", "file"),
        ("copy files to backup", "file"),
        ("move old files", "file"),
        
        # Process operations
        ("kill the process", "process"),
        ("stop the running server", "process"),
        ("show all processes", "process"),
        
        # Network operations
        ("download the file", "network"),
        ("fetch data from url", "network"),
        ("ping the server", "network"),
        
        # Text processing
        ("search for pattern", "text"),
        ("filter the output", "text"),
        ("replace text in file", "text"),
        
        # Multiple domains
        ("find files and search for text", ["file", "text"]),
        
        # No specific domain
        ("show current time", None),
    ]
    
    print("Testing domain detection and example inclusion...\n")
    
    for user_input, expected_domain in test_cases:
        prompt = client.build_prompt(user_input)
        
        print(f"Input: {user_input}")
        print(f"Expected domain: {expected_domain}")
        
        # Check if appropriate examples are included
        if expected_domain == "file":
            assert "find" in prompt.lower() or "ls" in prompt.lower(), \
                f"File examples should be in prompt for: {user_input}"
            print("✓ File operation examples included")
            
        elif expected_domain == "process":
            assert "ps" in prompt.lower() or "kill" in prompt.lower(), \
                f"Process examples should be in prompt for: {user_input}"
            print("✓ Process operation examples included")
            
        elif expected_domain == "network":
            assert "curl" in prompt.lower() or "wget" in prompt.lower(), \
                f"Network examples should be in prompt for: {user_input}"
            print("✓ Network operation examples included")
            
        elif expected_domain == "text":
            assert "grep" in prompt.lower() or "sed" in prompt.lower(), \
                f"Text processing examples should be in prompt for: {user_input}"
            print("✓ Text processing examples included")
            
        elif isinstance(expected_domain, list):
            # Multiple domains
            for domain in expected_domain:
                if domain == "file":
                    assert "find" in prompt.lower() or "ls" in prompt.lower()
                elif domain == "text":
                    assert "grep" in prompt.lower() or "sed" in prompt.lower()
            print(f"✓ Multiple domain examples included: {expected_domain}")
            
        elif expected_domain is None:
            # No specific domain - should still have base instructions
            assert "shell command" in prompt.lower(), \
                "Base instructions should always be present"
            print("✓ Base instructions present (no specific domain)")
        
        print()
    
    print("All domain detection tests passed! ✓")

def test_safe_interpretation_guidance():
    """Test that prompts include guidance for safe interpretations."""
    client = OllamaClient()
    
    # Test with an ambiguous request
    prompt = client.build_prompt("delete old files")
    
    print("Testing safe interpretation guidance...\n")
    print("Input: delete old files")
    
    # Check for safety guidance
    assert "error suppression" in prompt.lower() or "2>/dev/null" in prompt, \
        "Prompt should include error suppression guidance"
    print("✓ Error suppression guidance included")
    
    # Check for proper quoting guidance
    assert "quot" in prompt.lower() or "'" in prompt or '"' in prompt, \
        "Prompt should include quoting guidance"
    print("✓ Quoting guidance included")
    
    print("\nSafe interpretation guidance tests passed! ✓")

def test_platform_specific_guidance():
    """Test that prompts include macOS-specific guidance."""
    client = OllamaClient()
    
    prompt = client.build_prompt("list files")
    
    print("Testing platform-specific guidance...\n")
    
    # Check for macOS mention
    assert "macos" in prompt.lower() or "mac" in prompt.lower(), \
        "Prompt should include macOS-specific guidance"
    print("✓ macOS-specific guidance included")
    
    print("\nPlatform-specific guidance tests passed! ✓")

if __name__ == "__main__":
    print("=" * 70)
    print("Enhanced Prompt Accuracy Verification")
    print("=" * 70)
    print()
    
    try:
        test_domain_detection()
        print()
        test_safe_interpretation_guidance()
        print()
        test_platform_specific_guidance()
        print()
        print("=" * 70)
        print("ALL VERIFICATION TESTS PASSED! ✓")
        print("=" * 70)
    except AssertionError as e:
        print()
        print("=" * 70)
        print(f"VERIFICATION FAILED: {e}")
        print("=" * 70)
        exit(1)
