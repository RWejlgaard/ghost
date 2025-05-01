# Ghost 👻

A CLI tool that uses AI to execute and chain commands on your behalf.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

```bash
# Run ghost with a prompt
ghost "show me the largest files in the current directory"

# Show detailed command outputs
ghost "list files" --verbose

# Execute unsafe commands without confirmation
ghost "delete old files" --force

# Get help
ghost --help
```

## Features

- **Natural Language Processing**: Convert your prompts into shell commands
- **Command Chaining**: Automatically chain multiple commands based on previous outputs
- **Safety Checks**: Identifies potentially unsafe commands and requests confirmation
- **Verbose Mode**: View detailed command outputs and execution steps
- **Force Mode**: Bypass safety confirmations (use with caution)

## How it works

Ghost uses OpenAI's API to:
1. Convert your natural language prompt into a shell command
2. Execute the command on your system
3. Analyze the output
4. Potentially run additional commands based on the output (up to 3 iterations)
5. Provide you with a final, human-friendly response

## Options

- `--verbose, -v`: Show detailed command outputs
- `--force, -f`: Execute unsafe commands without confirmation
- `--help`: Show help message and exit

## Security Note

Ghost will ask for confirmation before executing any commands that are deemed potentially unsafe. Always review the commands before approving them. Use the `--force` flag with caution as it bypasses these safety checks.

## Requirements

- Python 3.x
- OpenAI API key
- Required Python packages (see requirements.txt) 
