# AI-Powered File Explorer

A modern file explorer application that combines traditional file management capabilities with AI-powered features using Claude AI. This application enables users to navigate, analyze, and manipulate files while leveraging AI for enhanced productivity.

## 🌟 Features

### File Management
- Hierarchical file/folder navigation
- File preview and editing capabilities
- Multi-file selection and batch operations
- Real-time file system monitoring
- Drag and drop support

### AI Integration
- Context-aware file analysis
- Natural language commands
- Content summarization and enhancement
- Code analysis and documentation
- Intelligent file organization

### User Interface
- Three-panel layout (Explorer, Preview, AI Assistant)
- Command palette for quick actions
- Progress indicators for async operations
- Syntax highlighting for code files
- Customizable layouts

## 🔧 Technical Architecture

### Core Components

1. File System Service
```python
- Real-time file monitoring
- Metadata management
- Content extraction
- File operations
```

2. AI Service
```python
- Claude API integration
- Context management
- Async operations
- Response streaming
```

3. UI Framework
```python
- PyQt6-based interface
- React components for web version
- Event-driven architecture
- Responsive design
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PyQt6
- Anthropic API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-file-explorer.git
cd ai-file-explorer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

5. Run the application:
```bash
python main.py
```

## 📚 Usage

### Basic Operations

1. File Navigation
```
- Click folders to expand/collapse
- Select files to preview
- Double-click to open
- Right-click for context menu
```

2. AI Commands
```
- Use Command Palette (Ctrl+P)
- Type in AI Assistant chat
- Drag files to AI chat
- Use "@" commands for specific actions
```

3. File Preview
```
- View file contents
- Edit in place
- Save changes
- Switch file types
```

### Example Commands

1. File Analysis:
```
"Analyze the structure of this project"
"Summarize selected files"
"Find similar files in this directory"
```

2. Content Operations:
```
"Generate documentation for this code"
"Improve the writing in this document"
"Convert this file to markdown"
```

3. Organization:
```
"Organize files by topic"
"Find duplicate content"
"Suggest folder structure"
```

## 🏗️ Project Structure

```
ai-file-explorer/
├── src/
│   ├── main.py
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── file_explorer.py
│   │   ├── preview.py
│   │   └── ai_assistant.py
│   ├── services/
│   │   ├── file_system.py
│   │   ├── ai_service.py
│   │   └── content_processor.py
│   └── utils/
│       ├── file_utils.py
│       └── ai_utils.py
├── tests/
├── docs/
└── requirements.txt
```

## 🛠️ Development

### Adding New Features

1. File Type Support:
```python
# Create new processor in content_processor.py
class PDFProcessor(DocumentProcessor):
    async def extract_text(self, file_path: Path) -> str:
        # Implementation
```

2. AI Commands:
```python
# Add to ai_service.py
async def process_command(self, command: str, context: List[Path]):
    # Implementation
```

3. UI Components:
```python
# Create in ui/ directory
class CustomWidget(QWidget):
    # Implementation
```

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Anthropic for Claude AI
- PyQt team
- Open source community

## 🚧 Roadmap

### Short-term
- Enhanced file type support
- Improved AI context management
- Better error handling
- Plugin system

### Long-term
- Web interface
- Collaborative features
- Version control integration
- Advanced AI capabilities

## 📞 Support

For support, please:
1. Check existing issues
2. Create a new issue with details
3. Join our community discussions

---

Remember to replace placeholder values (like repository URLs) with actual project information when implementing. For questions or contributions, please open an issue or pull request.