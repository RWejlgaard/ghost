# Ghost 👻

**An AI-powered CLI assistant that converts natural language into executable shell commands**

Ghost bridges the gap between what you want to do and knowing the exact commands to do it. Simply describe your task in plain English, and Ghost will generate, execute, and chain the appropriate shell commands to accomplish your goal.

## What Ghost Does

Ghost is an intelligent command-line interface that:

1. **Translates natural language to shell commands** - Turn "show me the largest files" into `find . -type f -exec ls -la {} + | sort -k5 -nr | head -10`
2. **Executes commands intelligently** - Runs the generated commands on your system with proper error handling
3. **Chains commands automatically** - Analyzes command outputs and runs follow-up commands as needed (up to 5 commands per session)
4. **Provides safety guardrails** - Identifies dangerous commands and asks for confirmation before execution
5. **Offers interactive file editing** - Detects when you want to create/edit files and provides AI-assisted editing

## Perfect Use Cases

### 📁 **File & Directory Operations**
```bash
ghost "find all Python files modified in the last week"
ghost "show me the largest files taking up space in my downloads folder"
ghost "organize these photos by date into separate folders"
ghost "backup all my documents to a zip file"
```

### 🔍 **System Investigation & Monitoring**
```bash
ghost "what processes are using the most memory right now"
ghost "check disk usage and show what's taking up space"
ghost "find all files containing the word 'password'"
ghost "show me network connections and which programs are making them"
```

### 🛠️ **Development & Configuration**
```bash
ghost "set up a new Python project with virtual environment and requirements.txt"
ghost "find all TODO comments in my codebase"
ghost "check git status and show me what files have changed"
ghost "install dependencies for this Node.js project"
```

### 📊 **Data Analysis & Text Processing**
```bash
ghost "analyze this CSV file and show me the top 10 entries by sales"
ghost "count how many times each word appears in this text file"
ghost "extract all email addresses from these log files"
ghost "convert all PNG images in this folder to JPEG"
```

### 🔧 **Quick System Tasks**
```bash
ghost "kill all Chrome processes"
ghost "check if port 8080 is being used by anything"
ghost "compress this folder and send it to my desktop"
ghost "update all my Homebrew packages"
```

## Key Features

### 🧠 **Smart Command Generation**
- Uses OpenAI GPT models to understand context and intent
- Generates appropriate commands for your specific operating system
- Learns from command history to make better subsequent decisions

### 🔄 **Automatic Command Chaining**
- Analyzes command outputs to determine if more commands are needed
- Chains up to 5 related commands automatically
- Stops when the original request is fully satisfied

### 🛡️ **Built-in Safety**
- Detects potentially dangerous commands (file deletion, system changes, etc.)
- Requires explicit confirmation for risky operations
- Provides `--force` flag to bypass confirmations when needed

### 📝 **Interactive File Editing**
- Detects when you want to create or edit files
- Offers AI-assisted file creation and editing
- Handles code generation, configuration files, and documentation

### 🎨 **Rich Output & User Experience**
- Beautiful terminal UI with colors and spinners
- Verbose mode shows detailed command execution
- Dry-run mode shows commands without executing them
- Clear error handling and retry mechanisms

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ghost
   ```

2. **Build the application**
   ```bash
   make
   ```

3. **Set your OpenAI API key**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file in the project directory:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

## Usage

### Basic Usage
```bash
# Simple command generation and execution
ghost "show me all running processes"

# Complex multi-step operations
ghost "find all large video files and move them to an archive folder"
```

### Command Options
```bash
# See detailed command outputs and AI reasoning
ghost "analyze system performance" --verbose

# Preview commands without executing them
ghost "delete old log files" --dry-run

# Execute potentially dangerous commands without confirmation
ghost "clean up temp files" --force

# Disable automatic retries on command failure
ghost "attempt risky operation" --no-retry

# Limit the number of chained commands
ghost "complex system analysis" --max-commands 3
```

### Example Sessions

**File Management:**
```bash
$ ghost "organize my desktop by file type"
👻 AI Generated Command 1: find ~/Desktop -type f -name "*.pdf" -exec mkdir -p ~/Desktop/PDFs \; -exec mv {} ~/Desktop/PDFs/ \;
✅ Command executed successfully
👻 AI Generated Command 2: find ~/Desktop -type f -name "*.jpg" -o -name "*.png" -exec mkdir -p ~/Desktop/Images \; -exec mv {} ~/Desktop/Images/ \;
✅ Command executed successfully
📋 Summary: Organized desktop files by type - moved PDFs to PDFs folder and images to Images folder
```

**System Analysis:**
```bash
$ ghost "what's slowing down my computer" --verbose
👻 AI Generated Command 1: top -l 1 -o cpu -n 5
✅ Command executed successfully
👻 AI Generated Command 2: ps aux --sort=-%cpu | head -10
✅ Command executed successfully
📋 Summary: Found Chrome and VS Code consuming most CPU. Consider closing unnecessary tabs or restarting applications.
```

## When Ghost Excels

### ✅ **Perfect For:**
- **Learning new commands** - See how tasks translate to shell commands
- **Complex file operations** - Multi-step file organization and processing
- **System administration** - Process management, disk usage analysis
- **Quick prototyping** - Setting up projects and environments
- **Data exploration** - Text processing and basic data analysis
- **Automation of repetitive tasks** - One-time complex operations

### ⚠️ **Not Ideal For:**
- **Ongoing production systems** - Use proper automation tools
- **Highly sensitive operations** - Review commands carefully
- **Performance-critical tasks** - Direct commands are faster
- **Complex programming logic** - Use appropriate development tools

## Safety & Security

Ghost includes multiple safety layers:

- **Command Analysis**: Scans for dangerous patterns before execution
- **User Confirmation**: Prompts for approval on risky operations
- **Safe Defaults**: Conservative approach to system modifications
- **Dry Run Mode**: Preview commands without execution
- **Command History**: Track all executed commands for review

**Always review generated commands before approving dangerous operations.**

## Requirements

- **Python 3.7+**
- **OpenAI API key** - [Get one here](https://platform.openai.com/api-keys)
- **Internet connection** - For AI command generation

## Contributing

Ghost is designed to make the command line more accessible and powerful. Contributions welcome for:
- New safety patterns
- Enhanced command generation
- Better error handling
- Additional use case examples

---

*Transform your command line experience - describe what you want, and let Ghost figure out how to do it.*
