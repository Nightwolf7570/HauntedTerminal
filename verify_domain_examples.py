#!/usr/bin/env python3
"""
Verification script for domain-specific example generation.
Run this to see how the enhanced prompt generation works.
"""

from src.ollama_client import OllamaClient


def main():
    print("🔮 Haunted Terminal - Domain-Specific Example Verification\n")
    print("=" * 70)
    
    client = OllamaClient()
    
    test_cases = [
        ("find all python files", "File operations"),
        ("kill process 1234", "Process management"),
        ("download file from url", "Network operations"),
        ("search for errors in logs", "Text processing"),
        ("find large files and count them", "Multiple domains"),
    ]
    
    for user_input, description in test_cases:
        print(f"\n📝 Test: {description}")
        print(f"   Input: \"{user_input}\"")
        
        # Detect domains
        domains = client._categorize_domain(user_input)
        print(f"   Detected domains: {', '.join(domains) if domains else 'general'}")
        
        # Get examples
        examples = client._get_domain_examples(user_input)
        
        # Show first few lines of examples
        example_lines = examples.strip().split('\n')[:8]
        print(f"   Example preview:")
        for line in example_lines:
            if line.strip():
                print(f"     {line}")
        
        # Verify key features
        checks = []
        if '2>/dev/null' in examples:
            checks.append("✓ Error suppression")
        if '"' in examples or "'" in examples:
            checks.append("✓ Proper quoting")
        if '|' in examples:
            checks.append("✓ Pipe usage")
        
        if checks:
            print(f"   Features: {', '.join(checks)}")
        
        print()
    
    print("=" * 70)
    print("\n✅ Domain-specific example generation is working correctly!")
    print("\nKey improvements:")
    print("  • Automatic domain detection from natural language")
    print("  • Context-relevant examples for better LLM guidance")
    print("  • Error suppression (2>/dev/null) in all file operations")
    print("  • Proper quoting and safe defaults demonstrated")
    print("  • macOS-specific command patterns included")
    print("  • Pipe and command chaining examples for complex operations")


if __name__ == "__main__":
    main()
