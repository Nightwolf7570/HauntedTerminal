"""
Setup configuration for Haunted Terminal CLI.
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="haunted-terminal-cli",
    version="0.1.0",
    description="A clean, modern command-line interface for natural language shell commands",
    author="Haunted Terminal Team",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "haunted=src.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
