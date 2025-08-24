# Contributing to MKD Automation

Thank you for your interest in contributing to MKD Automation! This document provides guidelines and information for contributors to ensure a smooth and productive collaboration.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Release Process](#release-process)
- [Community](#community)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions
- Collaborate openly and transparently

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.9 or higher
- Git version control system
- A GitHub account
- Basic understanding of automation testing concepts

### Ways to Contribute

We welcome contributions in various forms:

1. **Bug Reports**: Help us identify and fix issues
2. **Feature Requests**: Suggest new functionality or improvements
3. **Code Contributions**: Submit bug fixes, features, or optimizations
4. **Documentation**: Improve or expand our documentation
5. **Testing**: Add test cases or improve test coverage
6. **Community Support**: Help other users in discussions and forums

## Development Environment Setup

### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/mkd_automation.git
cd mkd_automation

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/mkd_automation.git
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in development mode
pip install -e .
```

### 4. Platform-Specific Setup

#### Windows
```bash
# Install Windows-specific dependencies
pip install pywin32 pygetwindow

# Ensure you have appropriate permissions for input simulation
# Run as administrator if needed for testing
```

#### macOS
```bash
# Install macOS-specific dependencies
pip install pyobjc-core pyobjc-framework-Quartz

# Grant accessibility permissions:
# System Preferences > Security & Privacy > Privacy > Accessibility
# Add Terminal or your IDE to allowed applications
```

#### Linux
```bash
# Install Linux-specific dependencies
pip install python-xlib pycairo

# Install system dependencies (Ubuntu/Debian):
sudo apt-get install python3-dev libcairo2-dev libgirepository1.0-dev

# For X11 development:
sudo apt-get install libx11-dev libxtst-dev
```

### 5. Verify Installation

```bash
# Run basic tests
python -m pytest tests/unit/core/ -v

# Check code formatting
make format-check

# Run linting
make lint

# Verify the main application starts
python src/main.py --help
```

### 6. IDE Configuration

#### VS Code (Recommended)
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## Project Structure

Understanding the project structure helps you navigate and contribute effectively:

```
mkd_automation/
├── src/                           # Source code
│   ├── main.py                    # Application entry point
│   └── mkd/                       # Main package
│       ├── core/                  # Core business logic
│       ├── data/                  # Data models and storage
│       ├── platform/              # Platform-specific implementations
│       ├── recording/             # Recording engine
│       ├── playback/              # Playback engine
│       ├── ui/                    # User interface components
│       └── utils/                 # Utility functions
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── fixtures/                  # Test fixtures and data
├── docs/                          # Documentation
│   ├── api/                       # API documentation
│   ├── developer/                 # Developer documentation
│   └── user_guide/                # User documentation
├── config/                        # Configuration files
├── scripts/                       # Build and utility scripts
└── examples/                      # Example scripts and tutorials
```

### Key Modules

- **Core**: Configuration management, session handling, script management
- **Platform**: OS-specific implementations for input capture and simulation
- **Recording**: Input capture, event processing, motion analysis
- **Playback**: Action execution, timing control, error handling
- **UI**: Control dialogs, settings, system tray integration
- **Data**: Models, serialization, encryption, storage

## Development Workflow

### 1. Branch Strategy

We use a feature branch workflow:

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes:
git checkout -b fix/issue-description

# Keep your branch up to date
git fetch upstream
git rebase upstream/main
```

### 2. Making Changes

1. **Write Tests First**: Follow TDD when possible
2. **Make Small, Focused Commits**: Each commit should represent a logical change
3. **Write Clear Commit Messages**: Follow conventional commit format
4. **Update Documentation**: Keep docs in sync with code changes

### 3. Commit Message Format

We follow the [Conventional Commits](https://conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

Examples:
```bash
git commit -m "feat(recording): add motion smoothing algorithm"
git commit -m "fix(playback): resolve timing accuracy issue on macOS"
git commit -m "docs(api): update recording engine documentation"
git commit -m "test(core): add unit tests for config manager"
```

## Code Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line Length**: 88 characters (Black formatter default)
- **Import Sorting**: Use isort with Black profile
- **Type Hints**: Required for all public APIs
- **Docstrings**: Google style docstrings for all public functions/classes

### Code Formatting

We use automated code formatting tools:

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/ --profile black

# Or use the Makefile
make format
```

### Linting

We use multiple linters to ensure code quality:

```bash
# Run all linters
make lint

# Individual linters
pylint src/
flake8 src/
mypy src/
bandit -r src/
```

### Type Annotations

All public APIs must include type annotations:

```python
from typing import Optional, List, Dict, Any

def process_events(
    events: List[Event],
    filters: Optional[List[str]] = None,
    config: Dict[str, Any] = None
) -> ProcessingResult:
    """
    Process a list of events with optional filtering.
    
    Args:
        events: List of events to process
        filters: Optional list of filter names to apply
        config: Configuration dictionary
        
    Returns:
        ProcessingResult: Results of event processing
        
    Raises:
        ProcessingError: If event processing fails
    """
    # Implementation here
    pass
```

### Documentation Style

Use Google-style docstrings:

```python
class RecordingEngine:
    """Main recording engine for capturing user interactions.
    
    This class provides the primary interface for recording user input
    events including mouse movements, clicks, keyboard input, and
    display changes.
    
    Attributes:
        is_recording: True if currently recording
        session_id: Current recording session identifier
        
    Example:
        >>> engine = RecordingEngine()
        >>> engine.start_recording('output.mkd')
        >>> # Perform actions...
        >>> engine.stop_recording()
    """
    
    def start_recording(self, output_path: str) -> None:
        """Start recording user interactions.
        
        Args:
            output_path: Path where recording will be saved
            
        Raises:
            RecordingAlreadyActiveError: If recording is already in progress
            FileAccessError: If output path is not writable
        """
        pass
```

## Testing Guidelines

### Test Structure

We use pytest for testing with the following structure:

```
tests/
├── unit/                    # Unit tests (isolated component testing)
│   ├── core/
│   ├── recording/
│   ├── playback/
│   └── platform/
├── integration/             # Integration tests (component interaction)
│   ├── test_recording_flow.py
│   └── test_playback_flow.py
├── fixtures/                # Test data and fixtures
│   ├── sample_scripts.mkd
│   └── mock_events.json
└── conftest.py             # Shared fixtures and configuration
```

### Writing Tests

#### Unit Tests

Test individual functions and classes in isolation:

```python
import pytest
from unittest.mock import Mock, patch

from mkd.core.config_manager import ConfigManager
from mkd.core.exceptions import ConfigValidationError


class TestConfigManager:
    """Test suite for ConfigManager."""
    
    def test_get_default_config_returns_valid_dict(self):
        """Test that default config is a valid dictionary."""
        config = ConfigManager.get_default_config()
        
        assert isinstance(config, dict)
        assert 'recording' in config
        assert 'playback' in config
        
    def test_validate_config_raises_on_invalid_data(self):
        """Test that invalid config raises validation error."""
        invalid_config = {'invalid': 'config'}
        
        with pytest.raises(ConfigValidationError):
            ConfigManager.validate_config(invalid_config)
            
    @patch('mkd.core.config_manager.load_from_file')
    def test_load_config_handles_missing_file(self, mock_load):
        """Test loading config handles missing file gracefully."""
        mock_load.side_effect = FileNotFoundError()
        
        config_manager = ConfigManager()
        config = config_manager.load_config('missing_file.json')
        
        # Should return default config
        assert config == ConfigManager.get_default_config()
```

#### Integration Tests

Test component interactions:

```python
import pytest
import tempfile
from pathlib import Path

from mkd.recording import RecordingEngine
from mkd.playback import PlaybackEngine


class TestRecordingPlaybackFlow:
    """Test recording and playback integration."""
    
    def test_record_and_playback_cycle(self):
        """Test complete record -> save -> load -> playback cycle."""
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = Path(temp_dir) / 'test_script.mkd'
            
            # Record some actions
            recorder = RecordingEngine()
            recorder.start_recording(str(script_path))
            
            # Simulate some actions (using mock events)
            mock_events = self._create_mock_events()
            for event in mock_events:
                recorder._process_event(event)
                
            recorder.stop_recording()
            
            # Verify script was created
            assert script_path.exists()
            
            # Load and playback
            player = PlaybackEngine()
            script_id = player.load_script(str(script_path))
            session_id = player.play(speed=10.0)  # Fast playback for testing
            
            # Wait for completion
            while player.get_status().is_active:
                time.sleep(0.01)
                
            stats = player.stop()
            assert stats.success_rate > 0.9
            
    def _create_mock_events(self):
        """Create mock events for testing."""
        # Implementation details...
        pass
```

### Test Coverage

Maintain high test coverage:

```bash
# Run tests with coverage
pytest --cov=src/mkd --cov-report=html --cov-report=term

# Coverage requirements:
# - Overall coverage: >90%
# - New code coverage: >95%
# - Critical paths: 100%
```

### Platform-Specific Testing

Test platform-specific functionality:

```python
import platform
import pytest

from mkd.platform import get_platform_handler


class TestPlatformSpecific:
    """Platform-specific tests."""
    
    @pytest.mark.skipif(platform.system() != 'Windows', 
                       reason="Windows-specific test")
    def test_windows_input_capture(self):
        """Test Windows-specific input capture."""
        handler = get_platform_handler()
        # Windows-specific tests...
        
    @pytest.mark.skipif(platform.system() != 'Darwin',
                       reason="macOS-specific test")
    def test_macos_accessibility_permissions(self):
        """Test macOS accessibility permission handling."""
        # macOS-specific tests...
```

### Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Scheduled daily runs

Local testing before push:
```bash
# Run full test suite
make test

# Run specific test categories
make test-unit
make test-integration
make test-platform
```

## Documentation Standards

### Code Documentation

- All public APIs must have docstrings
- Complex algorithms should have inline comments
- Architecture decisions should be documented in `docs/developer/`

### User Documentation

- Keep user-facing documentation up to date
- Include practical examples
- Document platform-specific requirements
- Maintain troubleshooting guides

### API Documentation

- Auto-generated from docstrings
- Include usage examples
- Document all parameters and return values
- Note breaking changes and deprecations

## Pull Request Process

### Before Submitting

1. **Run Tests**: Ensure all tests pass
2. **Check Coverage**: Maintain or improve test coverage
3. **Update Documentation**: Keep docs synchronized with code
4. **Format Code**: Run formatters and linters
5. **Rebase Branch**: Keep history clean

```bash
# Pre-submission checklist
make test
make lint
make format
make docs-build
```

### Pull Request Template

When creating a pull request, use this template:

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests passing

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Tests cover new functionality
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linters
2. **Code Review**: Maintainers review code quality and design
3. **Feedback Integration**: Address review comments
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge to main branch

### Review Criteria

Reviewers will assess:
- **Functionality**: Does it work as intended?
- **Code Quality**: Is it readable, maintainable, and well-structured?
- **Testing**: Are there adequate tests?
- **Performance**: Are there performance implications?
- **Security**: Are there security considerations?
- **Documentation**: Is it properly documented?

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
Clear and concise description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- MKD Version: [e.g. 0.2.1]

**Additional Context**
Any additional information, logs, or screenshots.
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Description**
Clear and concise description of the desired feature.

**Use Case**
Describe the problem this feature would solve.

**Proposed Solution**
Describe your preferred solution.

**Alternatives Considered**
Describe alternative solutions or features considered.

**Additional Context**
Any additional context or screenshots.
```

### Issue Labels

We use labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `platform:windows`: Windows-specific
- `platform:macos`: macOS-specific
- `platform:linux`: Linux-specific
- `priority:high`: High priority
- `priority:low`: Low priority

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update Version**: Bump version in `pyproject.toml`
2. **Update Changelog**: Document changes in `CHANGELOG.md`
3. **Run Full Tests**: Ensure all platforms pass
4. **Update Documentation**: Sync with new version
5. **Create Release**: Tag and create GitHub release
6. **Publish Package**: Upload to PyPI

### Alpha/Beta Releases

- **Alpha**: Internal testing (`0.3.0a1`)
- **Beta**: Public testing (`0.3.0b1`)
- **Release Candidate**: Final testing (`0.3.0rc1`)
- **Stable**: Production ready (`0.3.0`)

## Community

### Communication Channels

- **GitHub Discussions**: General discussions and questions
- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions and reviews
- **Wiki**: Community-maintained documentation

### Getting Help

- Check existing documentation first
- Search GitHub issues for similar problems
- Ask questions in GitHub Discussions
- Join our community chat (link in README)

### Recognition

We value all contributions:
- Contributors are listed in `CONTRIBUTORS.md`
- Significant contributors become maintainers
- Regular contributors get special recognition

### Mentorship

New contributors can request mentorship:
- Assign yourself to "good first issue" tickets
- Ask for help in pull request comments
- Request code review feedback
- Join pair programming sessions

Thank you for contributing to MKD Automation! Your efforts help make automation accessible to everyone.