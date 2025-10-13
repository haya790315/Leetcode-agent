"""
AI Agent with Gemini using LangChain and Conversation Memory.

Setup for an AI agent that:
- Uses Google Gemini via LangChain's ChatGoogleGenerativeAI
- Maintains conversation history using LangChain's ConversationBufferMemory
- Supports basic file operations as tools (create, read, list files)
- Provides conversation export and summary functionalities
"""

import os
import json
from datetime import datetime
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from leetcode_agent.utils import setup_logging
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Define tools as Pydantic models for LangChain
class CreateFile(BaseModel):
    """Create a new file with specified content."""

    file_path: str = Field(
        description="Path where the file should be created. Use relative paths (e.g., 'solutions/two_sum.py') or absolute paths (e.g., '/Users/name/Desktop/file.py')"
    )
    content: str = Field(default="", description="Content to write to the file")
    overwrite: bool = Field(
        default=False, description="Whether to overwrite if file exists"
    )


class ReadFile(BaseModel):
    """Read content from a file."""

    file_path: str = Field(description="Path to the file to read")


class ListFiles(BaseModel):
    """List files in a directory with optional pattern matching."""

    directory: str = Field(default=".", description="Directory to list")
    pattern: str = Field(default="*", description="Glob pattern to match files")


class ConversationTemplate:
    """Template for structuring conversations."""

    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt or self.default_system_prompt()

    def default_system_prompt(self) -> str:
        return """
                You are a helpful AI assistant. You are knowledgeable, friendly, and concise.

                Guidelines:
                - You need to help me to solve the leetcode problems.
                - when I ask for code , do not give me any explanation. I just need the code only , so please return the code only.
                - If there is any wrong case provided , please fix the code and return the fixed code only.
              """

    def format_message(self, role: str, content: str) -> Dict[str, str]:
        """Format a message with role and content."""
        return {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }


class AiAgent:
    """Simple AI Agent using Google Gemini via LangChain with conversation memory."""

    def __init__(
        self,
        api_key: str = None,
        model_name: str = "gemini-pro",
        template: ConversationTemplate = None,
        temperature: float = 0.7,
    ):
        """
        Initialize the Gemini Agent using LangChain.

        Args:
            api_key: Google AI API key (or from GOOGLE_API_KEY env var)
            model_name: Gemini model name
            template: Conversation template
            temperature: Model temperature (0.0-1.0)
        """
        # Set up API key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter."
            )

        # Initialize LangChain's ChatGoogleGenerativeAI
        self.model_name = model_name
        self.base_llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=temperature,
            convert_system_message_to_human=True,  # Gemini doesn't support system messages
        )

        # Bind tools to the LLM
        self.tools = [CreateFile, ReadFile, ListFiles]
        self.llm = self.base_llm.bind_tools(self.tools)

        # Set up template and conversation
        self.template = template or ConversationTemplate()

        # Initialize LangChain memory (using new approach)
        self.chat_history = InMemoryChatMessageHistory()

        # Add system message to memory
        self.chat_history.add_message(
            SystemMessage(content=self.template.system_prompt)
        )

        # Keep conversation history for export functionality
        self.conversation_history = [
            self.template.format_message("system", self.template.system_prompt)
        ]

        self.logger = setup_logging("INFO")

        self.used_tokens = 0

    def execute_tool_call(self, tool_call) -> str:
        """Execute a single tool call and return the result."""
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        try:
            if tool_name == "CreateFile":
                return self.create_file(**tool_args)
            elif tool_name == "ReadFile":
                return self.read_file(**tool_args)
            elif tool_name == "ListFiles":
                return self.list_files(**tool_args)
            else:
                return f"❌ Unknown tool: {tool_name}"
        except Exception as e:
            return f"❌ Error executing {tool_name}: {str(e)}"

    def add_message(self, role: str, content: str):
        """Add a message to conversation history and LangChain memory."""
        # Add to our custom history for export functionality
        message = self.template.format_message(role, content)
        self.conversation_history.append(message)

        # Add to LangChain memory
        if role == "user":
            self.chat_history.add_user_message(content)
        elif role == "assistant":
            self.chat_history.add_ai_message(content)

    def chat(self, user_message: str) -> str:
        """Send a message to the agent and get a response using LangChain."""
        try:
            # Get conversation history as LangChain messages
            messages = list(self.chat_history.messages)

            # Add current user message
            messages.append(HumanMessage(content=user_message))

            # Generate response using LangChain with tools
            response = self.llm.invoke(messages)

            assistant_message = response.content
            token_usage = response.usage_metadata.get("total_tokens", 0)

            self.logger.info(f"📈 Token used: {token_usage}")

            self.used_tokens += token_usage

            # Check if the response contains tool calls
            response_text = assistant_message

            if hasattr(response, "tool_calls") and response.tool_calls:
                self.logger.info(
                    f"🔧 Agent wants to use {len(response.tool_calls)} tools:"
                )
                tool_results = []

                for tool_call in response.tool_calls:
                    self.logger.info(f"🪚 Agent use - {tool_call['name']}")
                    result = self.execute_tool_call(tool_call)
                    tool_results.append(result)

                if tool_results:
                    for result in tool_results:
                        self.logger.info(f"💡 Tool report: {result}")

            # Add both messages to history
            self.add_message("user", user_message)
            self.add_message("assistant", assistant_message)

            return response_text

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.logger.info(f"❌ {error_msg}")
            return error_msg

    def clear_conversation(self):
        """Clear conversation history and LangChain memory."""
        # Clear LangChain memory
        self.chat_history.clear()

        # Re-add system message to memory
        self.chat_history.add_message(
            SystemMessage(content=self.template.system_prompt)
        )

        # Clear our custom history
        self.conversation_history = [
            self.template.format_message("system", self.template.system_prompt)
        ]
        self.logger.info("🧹 Conversation history cleared")

    def get_conversation_summary(self) -> Dict:
        """Get a summary of the conversation."""
        user_messages = [
            msg for msg in self.conversation_history if msg["role"] == "user"
        ]
        assistant_messages = [
            msg for msg in self.conversation_history if msg["role"] == "assistant"
        ]

        # Helper function to format timestamp
        def format_timestamp(iso_timestamp):
            if iso_timestamp:
                dt = datetime.fromisoformat(iso_timestamp)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return None

        return {
            "📮 total_messages": len(self.conversation_history),
            "📤 user_messages": len(user_messages),
            "📥 assistant_messages": len(assistant_messages),
            "💰 total_tokens_used": self.used_tokens,
            "🕒 first_message_time": format_timestamp(
                self.conversation_history[1]["timestamp"]
                if len(self.conversation_history) > 1
                else None
            ),
            "🕒 last_message_time": format_timestamp(
                self.conversation_history[-1]["timestamp"]
                if self.conversation_history
                else None
            ),
            "🧠 model": self.model_name,
        }

    def export_conversation(self, format_type: str = "text") -> str:
        """Export conversation in different formats."""
        if format_type == "text":
            lines = []
            for msg in self.conversation_history:
                if msg["role"] != "system":
                    role = msg["role"].upper()
                    content = msg["content"]
                    timestamp = msg["timestamp"]
                    lines.append(f"[{timestamp}] {role}: {content}\n")
            return "\n".join(lines)

        elif format_type == "json":
            return json.dumps(self.conversation_history, indent=2, ensure_ascii=False)

        else:
            return "Unsupported format. Use 'text' or 'json'."

    def create_file(
        self, file_path: str, content: str = "", overwrite: bool = True
    ) -> str:
        """
        Create a new file with the specified content.

        Args:
            file_path: Path where the file should be created
            content: Content to write to the file (default: empty)
            overwrite: Whether to overwrite if file exists (default: True)

        Returns:
            Success/error message
        """
        try:
            # Check if file exists and overwrite is False
            if os.path.exists(file_path) and not overwrite:
                return f"❌ File already exists: {file_path}. Use overwrite=True to replace it."

            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                self.logger.info(f"📁 Created directory: {directory}")

            action = "Created" if not os.path.exists(file_path) else "Overwritten"

            # Create and write file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return f"✅ {action} file: {file_path} ({len(content)} characters)"

        except Exception as e:
            return f"❌ Error creating file {file_path}: {str(e)}"

    def read_file(self, file_path: str) -> str:
        """
        Read content from a file.

        Args:
            file_path: Path to the file to read

        Returns:
            File content or error message
        """
        try:
            if not os.path.exists(file_path):
                return f"❌ File not found: {file_path}"

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return f"📄 File content ({len(content)} characters):\n{content}"

        except Exception as e:
            return f"❌ Error reading file {file_path}: {str(e)}"

    def list_files(self, directory: str = ".", pattern: str = "*") -> str:
        """
        List files in a directory with optional pattern matching.

        Args:
            directory: Directory to list (default: current directory)
            pattern: Glob pattern to match files (default: all files)

        Returns:
            List of files or error message
        """
        try:
            import glob

            if not os.path.exists(directory):
                return f"❌ Directory not found: {directory}"

            search_pattern = os.path.join(directory, pattern)
            files = glob.glob(search_pattern)

            if not files:
                return f"📂 No files found matching '{pattern}' in {directory}"

            file_list = []
            for file in sorted(files):
                if os.path.isfile(file):
                    size = os.path.getsize(file)
                    file_list.append(f"  📄 {os.path.basename(file)} ({size} bytes)")
                elif os.path.isdir(file):
                    file_list.append(f"  📁 {os.path.basename(file)}/")

            return f"📂 Files in {directory}:\n" + "\n".join(file_list)

        except Exception as e:
            return f"❌ Error listing files in {directory}: {str(e)}"
