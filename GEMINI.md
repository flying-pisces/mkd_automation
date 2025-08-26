# Project: MKD Automation

## Project Overview

MKD Automation is a cross-platform desktop application for recording and replaying user interactions. It is written in Python and designed to be a comprehensive tool for automation engineers and developers. The project is well-structured, with a clear separation of concerns between the core logic, platform-specific implementations, and user interface. It uses a variety of modern Python libraries for everything from data validation to encryption.

The project is configured with a `pyproject.toml` file, which defines the project's metadata, dependencies, and build process. It also uses a `Makefile` to automate common development tasks, such as installing dependencies, running tests, and building the project.

## Building and Running

### Prerequisites

*   Python 3.9+
*   `make`

### Installation

To set up the development environment, run the following command:

```bash
make install-dev
```

This will create a virtual environment, install all the necessary dependencies, and install the project in editable mode.

### Running the Application

To run the application, use the following command:

```bash
make run
```

### Running Tests

To run the test suite, use the following command:

```bash
make test
```

This will run all the unit, integration, and platform-specific tests.

### Building the Project

To build the project, use the following command:

```bash
make build
```

This will create a source distribution and a wheel.

## Development Conventions

### Code Style

The project uses `black` for code formatting and `isort` for import sorting. These tools are configured in the `pyproject.toml` file and are run automatically by the `pre-commit` hooks.

### Linting

The project uses `pylint`, `flake8`, `mypy`, and `bandit` for linting and security analysis. These tools are also configured in the `pyproject.toml` file and are run automatically by the `pre-commit` hooks.

### Commit Messages

The project follows the "Conventional Commits" specification for commit messages. This is enforced by the `commit-msg` `pre-commit` hook.

### Testing

The project uses `pytest` for testing. The tests are organized into three categories: unit, integration, and platform-specific. The tests are located in the `tests` directory.

### Automation

The project uses a `Makefile` to automate common development tasks. The `Makefile` is well-documented and provides a variety of targets for everything from installing dependencies to building the project.
