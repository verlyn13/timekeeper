# Roo Code: Developer Guide & Specification

## Introduction

Roo Code (previously known as Roo Cline) is an AI-powered autonomous coding agent that integrates directly into your code editor. This guide provides detailed information on its configuration, requirements, and advanced features to help you maximize your development experience.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [API Configuration](#api-configuration)
4. [Core Features](#core-features)
5. [Custom Modes](#custom-modes)
6. [Custom Instructions](#custom-instructions)
7. [Model Context Protocol (MCP)](#model-context-protocol-mcp)
8. [Command Automation](#command-automation)
9. [Security Considerations](#security-considerations)
10. [Experimental Features](#experimental-features)
11. [Troubleshooting](#troubleshooting)
12. [Additional Resources](#additional-resources)

---

## System Requirements

### Supported Editors

- VS Code (primary support)
- Any VS Code-compatible editor (including VS Codium)

### System Specifications

- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Disk Space**: 100MB for the extension
- **Operating Systems**: Windows, macOS, Linux
- **Network**: Active internet connection required for API communication

### Dependencies

- Node.js runtime (installed automatically with VS Code)
- Git (recommended for full functionality)

---

## Installation

1. **VS Code Marketplace Installation**:

   - Open VS Code
   - Navigate to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
   - Search for "Roo Code"
   - Click Install

2. **Manual Installation** (for offline or custom deployments):

   - Download the .vsix file from the [GitHub repository](https://github.com/RooVetGit/Roo-Code)
   - In VS Code, select "Install from VSIX" from the Extensions view options menu
   - Navigate to and select the downloaded .vsix file

3. **Verification**:
   - After installation, you should see the Roo Code icon in your VS Code activity bar
   - Click the icon to open the Roo Code panel

---

## API Configuration

Roo Code requires an API key from an AI model provider to function. The extension supports multiple API providers:

### Recommended Providers

- **OpenRouter**: Access to multiple AI models through a single API key (recommended for beginners)
- **Anthropic**: Direct access to Claude models (requires API access approval)
- **Local Models**: Support for running models locally through Ollama and LM Studio

### API Key Setup

1. **Obtain an API Key**:

   - Create an account with your chosen provider
   - Generate an API key from your provider's dashboard
   - Copy the key to your clipboard

2. **Configure Roo Code**:

   - Open the Roo Code panel
   - Click the settings icon
   - Select "API Configuration"
   - Paste your API key
   - Select your provider from the dropdown menu
   - Click "Save"

3. **Multiple Configuration Profiles**:
   - Roo Code supports saving different API configurations
   - Create profiles for different providers or models
   - Switch between profiles based on your current task requirements

### Model Selection Recommendations

- **Claude 3.7 Sonnet**: Best balance of capabilities and performance
- **Claude 3 Opus**: For complex architectural planning and high-quality code
- **Ollama/Local Models**: For offline work or when privacy is paramount

---

## Core Features

### Basic Interaction

- **Chat Interface**: Type natural language requests in the input box
- **Context Awareness**: Roo Code analyzes your open files and workspace
- **@-mention Syntax**: Reference specific files using `@filename.ext`

### Code Generation

- **Full File Creation**: Generate complete files from descriptions
- **Code Completion**: Extend existing code with AI suggestions
- **Refactoring**: Restructure and improve existing code
- **Bug Fixing**: Identify and fix issues in your code

### File Operations

- **Create/Edit/Delete Files**: Manage files through natural language requests
- **Batch Operations**: Apply changes across multiple files
- **Large File Handling**: Efficiently manage large files through structure mapping

### Terminal Integration

- **Command Execution**: Run terminal commands via Roo Code
- **Output Analysis**: Interpret command results and suggest next steps
- **Approval Workflow**: Review commands before execution

---

## Custom Modes

Custom modes allow you to tailor Roo Code's behavior for specific tasks or workflows.

### Built-in Modes

- **Code**: General-purpose coding tasks (default)
- **Architect**: Planning and technical leadership
- **Ask**: Answering questions and providing information
- **Debug**: Systematic problem diagnosis

### Creating Custom Modes

#### Via UI

1. Open the Prompts Tab (click the gear icon in the menu bar)
2. Click the plus button next to the Modes heading
3. Configure your custom mode with:
   - **Name**: A descriptive name for your mode
   - **Slug**: A unique identifier (lowercase, no spaces)
   - **Save Location**: Global or Project-specific
   - **Role Definition**: Define Roo's expertise for this mode
   - **Available Tools**: Select allowed tools
   - **Custom Instructions**: Add behavioral guidelines

#### Via Configuration Files

Create a JSON file with your custom mode definitions:

```json
{
  "customModes": [
    {
      "slug": "docs-writer",
      "name": "Documentation Writer",
      "roleDefinition": "You are a technical writer specializing in clear documentation",
      "groups": [
        "read",
        [
          "edit",
          {
            "fileRegex": "\\.md$",
            "description": "Markdown files only"
          }
        ]
      ],
      "customInstructions": "Focus on clear explanations and examples"
    }
  ]
}
```

- **Global Configuration**: Save as `cline_custom_modes.json` in your user settings
- **Project Configuration**: Save as `.roomodes` in your project root

### Mode-Specific Rules

- Create `.clinerules-[mode]` files in your workspace root (e.g. `.clinerules-code`)
- Define specific behaviors, constraints, or preferences for each mode

---

## Custom Instructions

Custom instructions define specific behaviors beyond Roo's basic role.

### Instruction Types

- **Global Instructions**: Apply to all modes
- **Mode-specific Instructions**: Apply only to a particular mode
- **Project-specific Instructions**: Apply only within a specific workspace

### Creating Instructions

#### Via UI

1. Open the Prompts Tab
2. Select the mode you want to customize
3. Enter your instructions in the Custom Instructions field

#### Via Rule Files

Create a rule file in your workspace root:

- `.clinerules`: Global instructions for all modes
- `.clinerules-[mode]`: Mode-specific instructions
- `.cursorrules`: Compatible with other AI coding assistants
- `.windsurfrules`: Compatible with other AI coding assistants

### Rule File Format

Instructions are simply plain text that can include:

- Coding style preferences
- Documentation standards
- Testing requirements
- Workflow guidelines
- Any other behavioral directives

### Rule Precedence

When multiple rule sources exist, they're applied in this order:

1. `.clinerules-[mode]` (mode-specific project rules)
2. `.clinerules` (global project rules)
3. `.cursorrules` (compatibility rules)
4. `.windsurfrules` (compatibility rules)
5. UI-configured instructions

---

## Model Context Protocol (MCP)

MCP extends Roo Code's capabilities by allowing integration with external tools and data sources.

### MCP Architecture

- **MCP Clients**: Applications that connect to MCP servers (Roo Code is an MCP client)
- **MCP Servers**: Lightweight servers that expose specific functionalities
- **MCP Hosts**: Applications that need access to external data or tools

### Setting Up MCP

1. **MCP Server Management**:

   - Access the MCP server tab via the server icon in the menu bar
   - Enable/disable built-in servers
   - Configure custom servers

2. **Dynamic Server Creation**:

   - Roo Code can create new MCP servers based on user requests
   - Example: "Add a tool that gets the latest npm docs"

3. **Custom Tool Integration**:
   - Connect to external APIs
   - Create specialized development tools
   - Integrate with databases and data sources

### Supported MCP Features

- **Web Browsing**: Access online resources directly
- **GitHub Integration**: Interact with repositories, issues, and pull requests
- **Custom API Connections**: Connect to any REST API
- **File System Access**: Extended file management capabilities
- **Database Connections**: Query and manipulate database data

---

## Command Automation

Roo Code can execute commands with varying levels of automation.

### Execution Modes

- **Manual Approval**: Review and approve every step (default)
- **Autonomous/Auto-Approve**: Allow Roo Code to run tasks without interruption

### Command Configuration

1. **Command Allowlisting**:

   - Configure which commands can run without approval
   - Set up through the settings menu

2. **Wildcard Configuration**:

   - Allow setting a wildcard (\*) to auto-approve all commands
   - Use with extreme caution

3. **Terminal Integration**:
   - Control how many lines of terminal output to pass to the model
   - Configure error handling and retry behavior

### Security Best Practices

- Only auto-approve known safe commands
- Limit auto-approval to non-destructive operations
- Always review commands that modify critical system components
- Use project-specific auto-approval configurations

---

## Security Considerations

### Data Privacy

- API keys are stored securely in your system's credential store
- Code analysis happens on your machine first, with filtered data sent to AI providers
- Consider using local models for sensitive projects

### Permission Model

- File operations require explicit approval
- Command execution requires explicit approval unless configured otherwise
- Browser interactions require explicit approval

### Workspace Isolation

- Project-specific settings remain within your workspace
- Custom modes can be limited to specific projects
- File access can be restricted based on patterns or locations

### Disclaimer

Roo Code is provided "AS IS" and "AS AVAILABLE" without warranties. Users assume all risks associated with usage, including potential:

- Intellectual property concerns
- Cyber vulnerabilities
- Code accuracy issues
- System performance impacts

---

## Experimental Features

Access cutting-edge capabilities that are still under development.

### Enabling Experimental Features

1. Open Roo Code settings
2. Navigate to "Advanced Settings"
3. Find the "Experimental Features" section
4. Toggle features on/off

### Available Experimental Features

- **Power Steering**: Improved adherence to role definitions and custom instructions
- **Alternative Diff Editing**: Advanced algorithm for applying changes to files
- **Checkpoints**: Ability to revert changes made to files
- **Shared Context**: Enhanced context sharing between different modes

### Stability Considerations

- Experimental features may have unexpected behavior
- They could potentially cause data loss or introduce security vulnerabilities
- Use with caution in production environments

---

## Troubleshooting

### Common Issues

#### API Connection Problems

- Verify your API key is correct and hasn't expired
- Check your internet connection
- Confirm your chosen API provider is operational

#### Performance Issues

- Reduce the number of files in context
- Limit the number of open editor tabs
- Use mode-specific API configurations for different tasks

#### File Operation Errors

- Check file permissions
- Verify file paths are correct
- Ensure the file isn't being modified by another process

### Support Resources

- GitHub Issues: Report bugs or request features
- Reddit Community: Discuss with other users
- Discord: Real-time community support

---

## Additional Resources

### Community

- [Reddit Community](https://www.reddit.com/r/RooCode)
- [Discord Server](https://discord.gg/roocode)
- [GitHub Repository](https://github.com/RooVetGit/Roo-Code)

### Documentation

- [Official Documentation](https://docs.roocode.com)
- [Changelog](https://github.com/RooVetGit/Roo-Code/blob/main/CHANGELOG.md)
- [Contributing Guide](https://github.com/RooVetGit/Roo-Code/blob/main/CONTRIBUTING.md)

### Licensing

- Apache 2.0 License
- © 2025 Roo Veterinary, Inc.
