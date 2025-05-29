# Browser Automation Framework Specification v1.0

## Table of Contents
1. [Overview](#overview)
2. [CSV Format Specification](#csv-format-specification)
3. [Action Specification](#action-specification)
4. [Runner Interface Specification](#runner-interface-specification)
5. [Network Interception Specification](#network-interception-specification)
6. [Error Handling Specification](#error-handling-specification)
7. [Logging Specification](#logging-specification)
8. [Extension Points](#extension-points)
9. [Implementation Guidelines](#implementation-guidelines)

## Overview

This specification defines a browser automation framework that uses CSV files to describe test steps. Any implementation following this specification should be compatible with CSV files written for other implementations.

### Core Principles
- **Language Agnostic**: Can be implemented in any programming language
- **Tool Agnostic**: Supports multiple browser automation tools
- **Extensible**: Easy to add new actions and features
- **Simple**: CSV format is human-readable and easy to edit

## CSV Format Specification

### File Format
- **Encoding**: UTF-8
- **Delimiter**: Comma (,)
- **Quote Character**: Double quote (")
- **Escape Character**: Backslash (\)
- **Line Ending**: LF or CRLF
- **Comment Character**: # (lines starting with # are ignored)

### Required Columns

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| action | string | Yes | The action to perform |
| target | string | No | The target element selector or URL |
| value | string | No | Additional value for the action |
| options | string/JSON | No | Additional options as JSON or key=value pairs |
| description | string | No | Human-readable description |

### Column Order
Columns must appear in the order: `action,target,value,options,description`

### Options Format
Options can be specified in two formats:
1. **JSON Format**: `{"timeout": 5000, "waitUntil": "load"}`
2. **Key-Value Format**: `timeout=5000;waitUntil=load`

### Example CSV
```csv
# Login test example
action,target,value,options,description
navigate,https://example.com,,,Navigate to homepage
waitfor,#login-button,,"{"timeout": 5000}",Wait for login button
click,#login-button,,,Click login
type,#username,testuser@example.com,,Enter username
type,#password,TestPass123!,{"delay": 50},Enter password
click,#submit,,,Submit form
asserttext,h1,Welcome,,Verify welcome message
screenshot,login-success.png,,"{"fullPage": true}",Capture screenshot
```

## Action Specification

### Core Actions

Every implementation MUST support these core actions:

#### Navigation Actions

| Action | Target | Value | Options | Description |
|--------|--------|-------|---------|-------------|
| navigate | URL | - | timeout, waitUntil | Navigate to URL |
| goto | URL | - | timeout, waitUntil | Alias for navigate |
| back | - | - | timeout | Go back in history |
| forward | - | - | timeout | Go forward in history |
| refresh | - | - | timeout | Refresh page |

#### Wait Actions

| Action | Target | Value | Options | Description |
|--------|--------|-------|---------|-------------|
| wait | milliseconds | - | - | Wait for specified time |
| waitfor | selector | - | timeout, state | Wait for element |
| waitforurl | URL/pattern | - | timeout | Wait for URL to match |

#### Interaction Actions

| Action | Target | Value | Options | Description |
|--------|--------|-------|---------|-------------|
| click | selector | - | timeout, force, button | Click element |
| doubleclick | selector | - | timeout | Double-click element |
| rightclick | selector | - | timeout | Right-click element |
| hover | selector | - | timeout | Hover over element |
| type | selector | text | delay, clear | Type text |
| clear | selector | - | timeout | Clear input field |
| select | selector | option value | timeout | Select dropdown option |
| check | selector | - | timeout | Check checkbox |
| uncheck | selector | - | timeout | Uncheck checkbox |
| focus | selector | - | timeout | Focus element |
| blur | selector | - | timeout | Blur element |

#### Keyboard Actions

| Action | Target | Value | Options | Description |
|--------|--------|-------|---------|-------------|
| press | key | - | timeout | Press keyboard key |
| keydown | key | - | timeout | Key down event |
| keyup | key | - | timeout | Key up event |

#### Mouse Actions

| Action | Target | Value | Options | Description |
|--------|--------|-------|---------|-------------|
| scroll | selector/window | pixels/position | direction | Scroll element or window |
| drag | selector | target selector | timeout | Drag and drop |
| mousemove | x,y | - | - | Move mouse to coordinates |

#### Assertion Actions

| Action | Target | Value | Options | Description |
|--------|--------|-------|---------|-------------|
| asserttext | selector | expected text | timeout, exact | Assert element text |
| assertvalue | selector | expected value | timeout | Assert input value |
| assertvisible | selector | - | timeout | Assert element visible |
| asserthidden | selector | - | timeout | Assert element hidden |
| assertexists | selector | - | timeout | Assert element exists |
| asserturl | URL/pattern | - | - | Assert current URL |
| asserttitle | expected title | - | - | Assert page title |
| assertcount | selector | count | timeout | Assert element count |

#### Utility Actions

| Action | Target | Value | Options | Description |
|--------|--------|-------|---------|-------------|
| screenshot | filename | - | fullPage, clip | Take screenshot |
| execute | script | args | - | Execute JavaScript |
| store | variable name | value | - | Store value in variable |
| echo | message | - | - | Log message |
| pause | - | - | - | Pause execution |

#### Network Actions

| Action | Target | Value | Options | Description |
|--------|--------|-------|---------|-------------|
| interceptrequest | URL pattern | handler | - | Intercept requests |
| interceptresponse | URL pattern | handler | - | Intercept responses |
| mockresponse | URL pattern | response data | status, headers | Mock response |
| waitfornetwork | URL pattern | - | timeout | Wait for network request |

### Selector Format

Selectors MUST support these formats:
- **CSS Selectors**: `#id`, `.class`, `div > p`
- **XPath**: `//div[@id='test']` (if selector starts with //)
- **Text**: `text=Submit` (for text-based selection)
- **Special Values**: `window`, `document`, `body`

### Key Names

Standard key names for keyboard actions:
- Modifier keys: `Control`, `Alt`, `Shift`, `Meta`
- Special keys: `Enter`, `Tab`, `Escape`, `Space`, `Backspace`, `Delete`
- Arrow keys: `ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight`
- Function keys: `F1` through `F12`
- Navigation: `Home`, `End`, `PageUp`, `PageDown`

## Runner Interface Specification

### Runner Lifecycle

```
1. Initialize
   ├── Create browser instance
   ├── Setup logging
   ├── Register actions
   └── Configure options

2. Parse CSV
   ├── Read file
   ├── Parse rows
   ├── Validate format
   └── Process variables

3. Execute Steps
   ├── For each step:
   │   ├── Validate action
   │   ├── Interpolate variables
   │   ├── Execute action
   │   ├── Handle errors
   │   └── Log result
   └── Continue or stop on error

4. Cleanup
   ├── Close browser
   ├── Save reports
   └── Clean temporary files
```

### Required Methods

Every runner implementation MUST provide these methods:

```typescript
interface Runner {
  // Lifecycle methods
  initialize(options: RunnerOptions): Promise<void>
  cleanup(): Promise<void>
  
  // Execution methods
  runSteps(steps: Step[]): Promise<void>
  executeStep(step: Step): Promise<void>
  
  // Browser methods
  navigate(url: string, options?: NavigateOptions): Promise<void>
  click(selector: string, options?: ClickOptions): Promise<void>
  type(selector: string, text: string, options?: TypeOptions): Promise<void>
  
  // Utility methods
  wait(timeout: number): Promise<void>
  waitFor(selector: string, options?: WaitOptions): Promise<void>
  screenshot(filename: string, options?: ScreenshotOptions): Promise<void>
  executeScript(script: string, args?: any[]): Promise<any>
  
  // Action registration
  registerAction(name: string, handler: ActionHandler): void
}
```

### Configuration Options

```typescript
interface RunnerOptions {
  // Browser options
  browser?: 'chrome' | 'firefox' | 'safari' | 'edge'
  headless?: boolean
  viewport?: { width: number, height: number }
  userAgent?: string
  
  // Execution options
  timeout?: number
  slowMo?: number
  continueOnError?: boolean
  retryCount?: number
  retryDelay?: number
  
  // Logging options
  logLevel?: 'debug' | 'info' | 'warn' | 'error'
  logFile?: string
  
  // Network options
  proxy?: string
  extraHeaders?: Record<string, string>
  
  // Custom options
  [key: string]: any
}
```

## Network Interception Specification

### Request Interception

```typescript
interface RequestInterceptor {
  pattern: string | RegExp
  handler: (request: Request) => Promise<Request | false>
}

interface Request {
  url: string
  method: string
  headers: Record<string, string>
  body?: any
  
  // Methods
  continue(overrides?: Partial<Request>): Promise<void>
  abort(reason?: string): Promise<void>
  respond(response: Response): Promise<void>
}
```

### Response Interception

```typescript
interface ResponseInterceptor {
  pattern: string | RegExp
  handler: (response: Response) => Promise<Response>
}

interface Response {
  url: string
  status: number
  headers: Record<string, string>
  body: any
  
  // Methods
  text(): Promise<string>
  json(): Promise<any>
  buffer(): Promise<Buffer>
}
```

## Error Handling Specification

### Error Types

```typescript
enum ErrorType {
  PARSE_ERROR = 'PARSE_ERROR',
  ACTION_NOT_FOUND = 'ACTION_NOT_FOUND',
  ELEMENT_NOT_FOUND = 'ELEMENT_NOT_FOUND',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  ASSERTION_ERROR = 'ASSERTION_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  SCRIPT_ERROR = 'SCRIPT_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}
```

### Error Response

```typescript
interface StepError {
  type: ErrorType
  message: string
  step: Step
  stack?: string
  screenshot?: string
}
```

### Error Handling Strategy

1. **Immediate Stop**: Default behavior, stop on first error
2. **Continue on Error**: Log error and continue with next step
3. **Retry on Error**: Retry failed step based on retry configuration
4. **Custom Handler**: Call user-defined error handler

## Logging Specification

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about execution
- **WARN**: Warning messages
- **ERROR**: Error messages

### Log Format

```
[TIMESTAMP] [LEVEL] [STEP_ID] [ACTION] Message
```

Example:
```
[2024-01-15T10:30:45.123Z] [INFO] [1] [navigate] Navigating to https://example.com
[2024-01-15T10:30:46.456Z] [INFO] [2] [click] Clicking element #login-button
[2024-01-15T10:30:47.789Z] [ERROR] [3] [type] Element not found: #username
```

### Required Log Events

- Step execution start
- Step execution complete
- Step execution failed
- Network requests (if intercepted)
- Screenshots taken
- Assertions performed

## Extension Points

### Custom Actions

Implementations MUST provide a way to register custom actions:

```typescript
runner.registerAction('customAction', async (runner, target, value, options) => {
  // Custom implementation
})
```

### Plugins

Implementations SHOULD support a plugin system:

```typescript
interface Plugin {
  name: string
  version: string
  
  // Lifecycle hooks
  beforeRun?(runner: Runner): Promise<void>
  afterRun?(runner: Runner, results: Results): Promise<void>
  beforeStep?(step: Step): Promise<void>
  afterStep?(step: Step, result: StepResult): Promise<void>
  
  // Custom actions
  actions?: Record<string, ActionHandler>
}
```

### Variable System

Support for variables in CSV files:

```csv
action,target,value,options,description
store,username,testuser@example.com,,Store username
type,#email,${username},,Use stored username
```

Variable sources:
1. Environment variables: `${ENV.VARIABLE_NAME}`
2. Stored variables: `${variableName}`
3. System variables: `${TIMESTAMP}`, `${RANDOM}`, `${UUID}`

## Implementation Guidelines

### Performance Requirements

- Step execution overhead: < 50ms
- CSV parsing: < 100ms for 1000 steps
- Screenshot capture: < 500ms
- Network interception overhead: < 10ms per request

### Compatibility Requirements

- Support latest stable versions of Chrome, Firefox, Safari, Edge
- Support viewport sizes from 320x568 to 3840x2160
- Handle both HTTP and HTTPS protocols
- Support frames and iframes
- Handle popups and new windows

### Security Considerations

- Sanitize file paths for screenshots
- Validate JavaScript code before execution
- Limit resource consumption
- Secure storage of sensitive data (passwords, tokens)
- Prevent directory traversal attacks

### Best Practices

1. **Implement retry logic** for flaky operations
2. **Use explicit waits** instead of hard-coded delays
3. **Provide detailed error messages** with context
4. **Take screenshots on failures** for debugging
5. **Log all significant events** for troubleshooting
6. **Validate selectors** before use
7. **Handle stale element references** gracefully
8. **Implement proper cleanup** in all error paths

### Testing Requirements

Implementations should include tests for:
- All core actions
- CSV parsing edge cases
- Error handling scenarios
- Network interception
- Variable interpolation
- Plugin system
- Performance benchmarks

## Version History

- **v1.0** (2024-01-15): Initial specification

## Future Considerations

- Mobile device emulation
- Geolocation mocking
- File upload/download handling
- WebSocket support
- Service Worker manipulation
- Multi-tab coordination
- Distributed execution
- Visual regression testing
