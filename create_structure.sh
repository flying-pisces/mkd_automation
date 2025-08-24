#!/bin/bash

# MKD Automation Tool - Project Structure Creation Script
# This script creates the complete folder and file structure for the MKD automation tool

echo "Creating MKD Automation Tool project structure..."

# Create main source directories
mkdir -p src/mkd/core
mkdir -p src/mkd/recording
mkdir -p src/mkd/playback
mkdir -p src/mkd/ui
mkdir -p src/mkd/platform
mkdir -p src/mkd/data
mkdir -p src/mkd/utils

# Create test directories
mkdir -p tests/unit/core
mkdir -p tests/unit/recording
mkdir -p tests/unit/playback
mkdir -p tests/unit/ui
mkdir -p tests/unit/platform
mkdir -p tests/unit/data
mkdir -p tests/integration
mkdir -p tests/fixtures

# Create documentation directories
mkdir -p docs/api
mkdir -p docs/user_guide
mkdir -p docs/developer

# Create scripts directory
mkdir -p scripts

# Create config directory
mkdir -p config

# Create resources directories
mkdir -p resources/icons
mkdir -p resources/themes
mkdir -p resources/sounds

# Create examples directory
mkdir -p examples/scripts
mkdir -p examples/tutorials

# Create main entry point
touch src/main.py

# Create core module files
touch src/mkd/__init__.py
touch src/mkd/core/__init__.py
touch src/mkd/core/session_manager.py
touch src/mkd/core/script_manager.py
touch src/mkd/core/config_manager.py
touch src/mkd/core/exceptions.py
touch src/mkd/core/constants.py

# Create recording module files
touch src/mkd/recording/__init__.py
touch src/mkd/recording/input_capturer.py
touch src/mkd/recording/motion_analyzer.py
touch src/mkd/recording/event_processor.py
touch src/mkd/recording/recording_engine.py
touch src/mkd/recording/filters.py

# Create playback module files
touch src/mkd/playback/__init__.py
touch src/mkd/playback/action_executor.py
touch src/mkd/playback/timing_engine.py
touch src/mkd/playback/error_handler.py
touch src/mkd/playback/playback_engine.py
touch src/mkd/playback/validators.py

# Create UI module files
touch src/mkd/ui/__init__.py
touch src/mkd/ui/control_dialog.py
touch src/mkd/ui/system_tray.py
touch src/mkd/ui/status_panel.py
touch src/mkd/ui/settings_dialog.py
touch src/mkd/ui/file_manager.py
touch src/mkd/ui/themes.py
touch src/mkd/ui/widgets.py

# Create platform module files
touch src/mkd/platform/__init__.py
touch src/mkd/platform/base.py
touch src/mkd/platform/windows.py
touch src/mkd/platform/macos.py
touch src/mkd/platform/linux.py
touch src/mkd/platform/detector.py

# Create data module files
touch src/mkd/data/__init__.py
touch src/mkd/data/script_storage.py
touch src/mkd/data/config_storage.py
touch src/mkd/data/encryption.py
touch src/mkd/data/models.py
touch src/mkd/data/serializers.py

# Create utils module files
touch src/mkd/utils/__init__.py
touch src/mkd/utils/logging.py
touch src/mkd/utils/validation.py
touch src/mkd/utils/helpers.py
touch src/mkd/utils/decorators.py
touch src/mkd/utils/performance.py

# Create test files
touch tests/__init__.py
touch tests/conftest.py

# Core tests
touch tests/unit/core/__init__.py
touch tests/unit/core/test_session_manager.py
touch tests/unit/core/test_script_manager.py
touch tests/unit/core/test_config_manager.py

# Recording tests
touch tests/unit/recording/__init__.py
touch tests/unit/recording/test_input_capturer.py
touch tests/unit/recording/test_motion_analyzer.py
touch tests/unit/recording/test_event_processor.py
touch tests/unit/recording/test_recording_engine.py

# Playback tests
touch tests/unit/playback/__init__.py
touch tests/unit/playback/test_action_executor.py
touch tests/unit/playback/test_timing_engine.py
touch tests/unit/playback/test_error_handler.py
touch tests/unit/playback/test_playback_engine.py

# UI tests
touch tests/unit/ui/__init__.py
touch tests/unit/ui/test_control_dialog.py
touch tests/unit/ui/test_system_tray.py
touch tests/unit/ui/test_status_panel.py
touch tests/unit/ui/test_settings_dialog.py

# Platform tests
touch tests/unit/platform/__init__.py
touch tests/unit/platform/test_windows.py
touch tests/unit/platform/test_macos.py
touch tests/unit/platform/test_linux.py
touch tests/unit/platform/test_detector.py

# Data tests
touch tests/unit/data/__init__.py
touch tests/unit/data/test_script_storage.py
touch tests/unit/data/test_config_storage.py
touch tests/unit/data/test_encryption.py

# Integration tests
touch tests/integration/__init__.py
touch tests/integration/test_recording_flow.py
touch tests/integration/test_playback_flow.py
touch tests/integration/test_ui_integration.py
touch tests/integration/test_cross_platform.py

# Test fixtures
touch tests/fixtures/sample_events.json
touch tests/fixtures/test_config.json
touch tests/fixtures/mock_scripts.mkd

# Create script files
touch scripts/build.py
touch scripts/package.py
touch scripts/install_deps.py
touch scripts/run_tests.py
touch scripts/lint.py
touch scripts/format.py

# Create configuration files
touch config/default_config.json
touch config/logging_config.yaml
touch config/themes.json
touch config/hotkeys.json

# Create resource placeholder files
touch resources/icons/app_icon.ico
touch resources/icons/start.png
touch resources/icons/stop.png
touch resources/icons/pause.png
touch resources/icons/settings.png
touch resources/themes/default.json
touch resources/themes/dark.json
touch resources/themes/light.json
touch resources/sounds/start_recording.wav
touch resources/sounds/stop_recording.wav
touch resources/sounds/error.wav

# Create example files
touch examples/scripts/basic_automation.mkd
touch examples/scripts/complex_workflow.mkd
touch examples/tutorials/getting_started.md
touch examples/tutorials/advanced_features.md

# Create documentation files
touch docs/README.md
touch docs/INSTALL.md
touch docs/CHANGELOG.md
touch docs/CONTRIBUTING.md
touch docs/LICENSE.md
touch docs/api/core_api.md
touch docs/api/recording_api.md
touch docs/api/playback_api.md
touch docs/user_guide/installation.md
touch docs/user_guide/basic_usage.md
touch docs/user_guide/advanced_features.md
touch docs/user_guide/troubleshooting.md
touch docs/developer/architecture.md
touch docs/developer/contributing.md
touch docs/developer/plugin_development.md

# Create project root files
touch README.md
touch LICENSE
touch CHANGELOG.md
touch .gitignore
touch requirements.txt
touch requirements-dev.txt
touch setup.py
touch pyproject.toml
touch Makefile
touch .env.example
touch .pylintrc
touch .pre-commit-config.yaml

echo "Project structure created successfully!"
echo "Total directories created: $(find . -type d | wc -l)"
echo "Total files created: $(find . -type f | wc -l)"
echo ""
echo "Next steps:"
echo "1. Run 'chmod +x create_structure.sh' to make this script executable"
echo "2. Review the structure and modify as needed"
echo "3. Start implementing core modules"
echo "4. Set up virtual environment and install dependencies"