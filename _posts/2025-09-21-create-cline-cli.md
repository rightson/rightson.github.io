# Cline CLI

Cline CLI brings the power of Cline's AI coding assistant to your terminal, offering the same capabilities as the VSCode extension in a command-line interface.

## Architecture & Design

The CLI version leverages Cline's existing host abstraction layer for minimal code changes while maintaining full feature parity with the VSCode extension.

### Current Implementation Strategy

Instead of complex code extraction, the CLI uses **direct replacement** of VSCode-specific functions with CLI/Ink equivalents:

```
Core Logic → HostProvider → CLI/Ink Implementation
```

This approach ensures:
- **~95% code reuse** from the original Cline codebase
- **Identical AI reasoning** and tool implementations
- **Same feature set** across both interfaces

## Fork-Friendly Structure

Since this is a forked project that syncs regularly with upstream, the structure minimizes impact on original code:

```
cline-cli/
├── src/                        # Original Cline code (unchanged)
│   ├── core/                   # ✅ Keep as-is for sync
│   ├── hosts/vscode/           # ✅ Keep as-is
│   └── ...                     # ✅ All original files unchanged
├── cli/                        # 🆕 CLI-specific code only
│   ├── src/
│   │   ├── index.ts           # CLI entry point
│   │   ├── hosts/             # CLI host implementations
│   │   └── ui/                # Ink React components
│   └── package.json           # CLI dependencies
└── scripts/                   # Migration & sync scripts
```

## Key Features

- **Same AI Models**: Full support for Anthropic, OpenAI, and all other providers
- **All Tools Available**: File operations, command execution, browser automation, MCP servers
- **Interactive Chat**: Real-time conversation with AI assistant powered by Ink
- **Feature Parity**: Identical functionality to VSCode extension
- **Easy Sync**: Regular upstream sync with minimal conflicts

## Technical Implementation

### Host Abstraction Replacement

The CLI replaces VSCode-specific implementations while keeping core logic unchanged:

| VSCode Function | CLI/Ink Equivalent |
|---|---|
| `vscode.window.showMessage()` | `<Text color="red">Error</Text>` |
| `vscode.window.showInputBox()` | `<TextInput>` component |
| `vscode.window.createTerminal()` | `spawn()` / `execa()` |
| `vscode.workspace.fs.*` | `fs.promises.*` |
| `webview.postMessage()` | Direct React state updates |
| `context.globalState` | `~/.cline/config.json` |

### Development Workflow

```bash
# Daily CLI development
cd cli/
npm run dev                    # Develop CLI features

# Sync with upstream Cline
npm run sync                   # Merge upstream changes
cd cli/ && npm run build       # Rebuild with updates
```

## When to Use CLI vs VSCode

**Use CLI when:**
- Working in terminal-heavy environments
- Remote server development
- Scripting and automation
- Lightweight development setups
- Need for headless AI assistance

**Use VSCode extension when:**
- Integrated IDE experience preferred
- Visual diff viewing needed
- Rich UI interactions desired
- Working primarily in VSCode

## Benefits of This Approach

### **Minimal Code Changes**
- Core AI logic remains identical
- Only host/UI implementations differ
- Shared bug fixes and improvements

### **Easy Feature Flow**
```
New Feature → Update core logic → Works in both VSCode & CLI automatically
```

### **Fork Maintenance**
- Original code untouched for clean upstream sync
- Clear separation between original and CLI code
- Independent CLI development and deployment

### **Development Speed**
- Direct 1:1 function replacements
- Leverage existing architecture
- No complex refactoring needed

This design ensures that new features developed in the main Cline project automatically become available in the CLI version with minimal additional work.