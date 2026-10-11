from pathlib import Path
from setuptools import setup, find_packages

README_PATH = Path(__file__).parent / "README.md"
long_description = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""

setup(
    name="sub-agent-orchestrator",
    version="0.1.0",
    description="Autonomous 6-SubAgent Orchestrator with Second Brain Integration and Git Worktree Isolation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Antigravity Team",
    license="MIT",
    python_requires=">=3.9",
    packages=find_packages(include=["core*", "contracts*", "agents*"]),
    package_data={
        "contracts": ["role_contracts.json"],
    },
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "sub-agent-orchestrator = core.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
    ],
)
