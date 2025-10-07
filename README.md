# 🤖 LeetCode Agent

An intelligent AI-powered assistant that automatically solves LeetCode problems using Google Gemini, LangChain, and browser automation.

## ✨ Features

- � **AI-Powered Problem Solving** - Uses Google Gemini via LangChain for intelligent code generation
- 🌐 **Web Automation** - Playwright-based browser automation for seamless LeetCode interaction
- 💬 **Conversation Memory** - Maintains context across multiple problem-solving sessions
- 📁 **File Management Tools** - Built-in tools for creating, reading, and managing solution files
- 🎯 **Auto-Submission** - Automatically submits solutions and handles test cases
- 🔄 **Iterative Problem Solving** - Learns from failed test cases to improve solutions
- 📊 **Token Usage Tracking** - Monitors API usage and costs
- �️ **Multiple Languages** - Supports Python, JavaScript, Java, and more

## 📁 Project Structure

```
leetcode-agent/
├── src/
│   └── leetcode_agent/
│       ├── __init__.py          # 📦 Package initialization
│       ├── __main__.py          # 🚀 Module execution entry
│       ├── main.py              # 🎛️ CLI interface and argument parsing
│       ├── core.py              # 🧠 Main LeetCode agent logic
│       ├── agent.py             # 🤖 AI agent with Gemini integration
│       ├── browser.py           # 🌐 Playwright browser automation
│       └── utils.py             # 🔧 Logging and utility functions
├── solutions/                   # 💾 Generated solution files
├── config/                      # ⚙️ Configuration files
├── tests/                       # 🧪 Test files
├── .env.example                 # 📝 Environment template
└── pyproject.toml              # 📋 Project configuration
```

## 🚀 Quick Start

### 📋 Prerequisites

- 🐍 **Python 3.9+**
- 📦 **uv package manager** (recommended) or pip
- 🌐 **Google AI API Key** (for Gemini access)

### ⚡ Installation

1. **📥 Clone the repository**
   ```bash
   git clone <repository-url>
   cd leetcode-agent
   ```

2. **📦 Install dependencies with uv** (recommended)
   ```bash
   uv sync
   ```
   
   **Or with pip:**
   ```bash
   pip install -e .
   ```

3. **🔑 Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   **Edit `.env` and add your Google AI API key:**
   ```bash
   GOOGLE_API_KEY=your_google_ai_api_key_here
   ```

4. **🌐 Install Playwright browsers**
   ```bash
   uv run playwright install
   # or with pip:
   playwright install
   ```

### 🔑 Getting Your Google AI API Key

1. 🌐 Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 🔑 Create a new API key
3. 📋 Copy the key to your `.env` file

## 🎮 Usage

### 🚀 Basic Usage

```bash
# Run with default settings
uv run leetcode-agent

# Run in headless mode
uv run leetcode-agent --headless

# Use specific programming language
uv run leetcode-agent --lang python3

# Enable debug logging
uv run leetcode-agent --log-level DEBUG

# Specify the url of leetcode problem
uv run leetcode-agent --url https://leetcode.com/problems/two-sum/
```

### 🎛️ Command Line Options

```bash
leetcode-agent [OPTIONS]

Options:
  --headless              🕶️  Run browser in headless mode (no GUI)
  --log-level LEVEL       📊  Set logging level (DEBUG, INFO, WARNING, ERROR)
  --lang LANGUAGE         💻  Programming language (python3, java, javascript, etc.)
  --url URL              🌐  LeetCode base URL (default: https://leetcode.com)
  --help                 ❓  Show help message
```

### 🔧 Available Programming Languages

- `python3`, `python` 🐍
- `java` ☕
- `javascript`, `typescript` 🟨
- `csharp` #️⃣
- `c`, `golang` 🔧
- `kotlin`, `swift` 📱
- `rust`, `ruby`, `php` 💎
- And more!

## ⚙️ Configuration

### 📝 Environment Variables (.env)

```bash
# 🔑 Required: Google AI API Key
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# 🌐 Optional: Browser Settings
HEADLESS_BROWSER=True

# 📊 Optional: Logging
LOG_LEVEL=INFO
```

### 🎯 Advanced Configuration

The agent automatically:
- 🎯 Navigates to LeetCode's daily problem
- 📖 Extracts problem description and code template
- 🧠 Uses AI to generate solutions
- ✅ Submits solutions and checks results
- 🔄 Iterates on failed test cases
- 💾 Saves successful solutions to files

## 🛠️ Development

### 🧪 Running Tests

```bash
uv run pytest
# or
python -m pytest
```

### 🔄 Development Workflow

```bash
# 📦 Add new dependencies
uv add package-name

# 🔄 Update dependencies
uv sync

# 🚀 Run in development mode
uv run -m leetcode_agent
```

### 🏗️ Architecture Overview

1. **🤖 AiAgent** (`agent.py`)
   - Google Gemini integration via LangChain
   - Conversation memory and token tracking
   - File management tools (create, read, list files)

2. **🧠 LeetCodeAgent** (`core.py`)
   - Main problem-solving orchestration
   - Browser automation coordination
   - Iterative solution improvement

3. **🌐 PlaywrightManager** (`browser.py`)
   - Browser context management
   - Element interaction and automation
   - Cross-platform keyboard shortcuts

4. **🎛️ CLI Interface** (`main.py`)
   - Command-line argument parsing
   - Logging setup and configuration

⭐ **Star this repo if you find it helpful!** ⭐
