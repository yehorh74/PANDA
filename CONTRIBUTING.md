# Contributing to PANDA

First off, thank you for taking the time to contribute!

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

## How to Contribute

### 1. Reporting Bugs / Requesting Features
If you find a bug or have a feature idea, please open an issue on the [GitHub Issues page](https://github.com/yehorh74/PANDA/issues). 
* Provide a clear title and description.
* Include steps to reproduce if it's a bug.
* Mention your Python version and environment details (OS, PsychoPy version).

### 2. Setting Up Your Development Environment

To start developing locally, follow these steps:

```bash
# Clone your fork or the repository
git clone [https://github.com/yehorh74/PANDA.git](https://github.com/yehorh74/PANDA.git)
cd PANDA

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\Activate.ps1

# Install the package in editable mode with development/test dependencies
pip install -e .[dev]
```

### 3. Running Tests
Make sure everything works before submitting your changes:

```bash
pytest
```

### 4. Submitting a Pull Request
Fork the repository and create your branch from main:

```bash
git checkout -b feature/your-feature-name
```

Commit your changes with clear messages.

Push to your fork and open a Pull Request against the main branch of yehorh74/PANDA.