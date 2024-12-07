# Getting Started Guide - AI-Powered File Explorer

## Prerequisites
Before beginning development, ensure you have the following installed:
1. Python 3.8 or higher
2. Git for version control
3. A code editor with Python support (VS Code recommended)
4. Operating system-specific build tools:
   - Windows: Microsoft Visual C++ Build Tools
   - Linux: gcc and related build essentials
   - macOS: Xcode Command Line Tools

## Step 1: System Setup

### 1.1 Python Environment Setup
1. Verify Python installation:
   ```bash
   python --version  # Should be 3.8+
   pip --version    # Verify pip is installed
   ```

2. Install virtualenv if not already present:
   ```bash
   pip install --user virtualenv
   ```

### 1.2 Project Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-file-explorer.git
   cd ai-file-explorer
   ```

2. Create and activate a virtual environment:
   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

3. Configure pip settings:
   - Create/modify `pip.conf` (Unix) or `pip.ini` (Windows) with provided settings
   - Location: 
     - Unix: `~/.config/pip/pip.conf`
     - Windows: `%APPDATA%\pip\pip.ini`

### 1.3 Dependencies Installation
1. Install base requirements:
   ```bash
   pip install -r requirements-base.txt
   ```

2. Install development requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Platform-specific installations:
   - Windows users: Additional magic binary will be installed automatically
   - Linux users: Install additional system packages:
     ```bash
     # Ubuntu/Debian
     sudo apt-get install libmagic1
     
     # Fedora
     sudo dnf install file-devel
     ```

## Step 2: Configuration Setup

### 2.1 Environment Variables
1. Create a `.env` file in the project root:
   ```bash
   touch .env  # Unix
   # or
   type nul > .env  # Windows
   ```

2. Add required environment variables:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   DEBUG=True
   LOG_LEVEL=DEBUG
   ```

### 2.2 IDE Configuration
1. VS Code Setup (Recommended):
   - Install recommended extensions:
     - Python
     - Pylance
     - Python Test Explorer
     - Git Lens
   
   - Configure settings.json:
     ```json
     {
       "python.linting.enabled": true,
       "python.linting.flake8Enabled": true,
       "python.formatting.provider": "black",
       "editor.formatOnSave": true,
       "python.linting.mypyEnabled": true
     }
     ```

## Step 3: Verification

### 3.1 Run Tests
1. Execute the test suite:
   ```bash
   python -m pytest tests/
   ```

2. Verify all tests pass before proceeding

### 3.2 Run Application
1. Start the application:
   ```bash
   python src/main.py
   ```

2. Verify basic functionality:
   - UI loads correctly
   - File explorer navigation works
   - AI connection is established

## Step 4: Development Tools Setup

### 4.1 Git Configuration
1. Configure Git user information:
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

2. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### 4.2 Documentation Tools
1. Install Sphinx for documentation:
   ```bash
   pip install sphinx sphinx-rtd-theme autodoc
   ```

2. Build documentation locally:
   ```bash
   cd docs
   make html
   ```

## Common Issues and Solutions

### Qt Installation Issues
- Windows: Ensure Microsoft Visual C++ Redistributable is installed
- Linux: Install `libxcb-xinerama0` if Qt fails to start
- macOS: Install Qt dependencies via Homebrew if needed

### Python-Magic Issues
- Windows: If file type detection fails, reinstall python-magic-bin
- Linux: Ensure libmagic is installed via system package manager

### Database Setup Issues
- Verify SQLite3 is installed and accessible
- Check write permissions in the database directory

## Next Steps
1. Review the project README.md for additional details
2. Explore the codebase structure in src/
3. Read through the Architecture Overview section
4. Join the development community channels
5. Start with small bug fixes or documentation improvements

## Support Resources
- Project Wiki: [Link to Wiki]
- Issue Tracker: GitHub Issues
- Development Chat: [Link to Chat]
- Documentation: [Link to Docs]