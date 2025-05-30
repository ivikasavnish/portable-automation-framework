# Scenario Tree Specification v1.0

## Table of Contents
1. [Overview](#overview)
2. [Tree Structure Specification](#tree-structure-specification)
3. [Node Types](#node-types)
4. [File Format Specification](#file-format-specification)
5. [Execution Engine](#execution-engine)
6. [Variable System](#variable-system)
7. [Conditional Logic](#conditional-logic)
8. [Error Handling](#error-handling)
9. [Integration with CSV Framework](#integration-with-csv-framework)
10. [API Specification](#api-specification)
11. [Examples](#examples)

## Overview

The Scenario Tree extends the Browser Automation Framework to support complex test scenarios with branching logic, conditional execution, parallel flows, and reusable components. It provides a structured way to organize and execute interdependent test cases.

### Core Principles
- **Hierarchical Structure**: Tests organized in tree format
- **Conditional Execution**: Dynamic flow based on runtime conditions
- **Reusability**: Shared components and sub-scenarios
- **Parallel Execution**: Support for concurrent test branches
- **Data-Driven**: Dynamic scenarios based on data sets
- **Backward Compatible**: Seamless integration with existing CSV framework

## Tree Structure Specification

### Basic Tree Concepts

```
Root Scenario
├── Setup Phase
│   ├── Browser Initialization
│   └── Authentication
├── Main Flow
│   ├── User Registration Path
│   │   ├── Valid Registration
│   │   └── Invalid Registration
│   └── User Login Path
│       ├── Successful Login
│       └── Failed Login
└── Cleanup Phase
    └── Logout
```

### Node Relationships

- **Parent-Child**: Hierarchical execution flow
- **Sibling**: Sequential or parallel execution
- **Reference**: Reusable component inclusion
- **Conditional**: Dynamic path selection

## Node Types

### Core Node Types

#### 1. Scenario Node
Top-level container for test scenarios.

```json
{
  "type": "scenario",
  "id": "user-management-tests",
  "name": "User Management Test Suite",
  "description": "Complete user registration and login flow",
  "metadata": {
    "author": "Test Team",
    "version": "1.0",
    "tags": ["authentication", "user-management"]
  },
  "config": {
    "timeout": 30000,
    "retryCount": 2,
    "parallel": false
  },
  "children": []
}
```

#### 2. Phase Node
Logical grouping of related test steps.

```json
{
  "type": "phase",
  "id": "setup-phase",
  "name": "Test Setup",
  "execution": "sequential",
  "required": true,
  "conditions": [],
  "children": []
}
```

#### 3. Step Node
Individual test action (CSV step or inline action).

```json
{
  "type": "step",
  "id": "login-click",
  "name": "Click Login Button",
  "action": "click",
  "target": "#login-button",
  "value": "",
  "options": {"timeout": 5000},
  "conditions": [],
  "onSuccess": "next",
  "onFailure": "retry"
}
```

#### 4. Branch Node
Conditional execution path.

```json
{
  "type": "branch",
  "id": "user-type-branch",
  "name": "User Type Selection",
  "condition": "${userType} === 'admin'",
  "branches": {
    "admin": {
      "condition": "${userType} === 'admin'",
      "children": []
    },
    "regular": {
      "condition": "${userType} === 'regular'",
      "children": []
    },
    "default": {
      "children": []
    }
  }
}
```

#### 5. Loop Node
Iterative execution.

```json
{
  "type": "loop",
  "id": "data-entry-loop",
  "name": "Enter Multiple Records",
  "loopType": "forEach",
  "data": "${testData}",
  "variable": "record",
  "maxIterations": 100,
  "breakCondition": "${record.status} === 'complete'",
  "children": []
}
```

#### 6. Reference Node
Include external scenario or CSV file.

```json
{
  "type": "reference",
  "id": "common-login",
  "name": "Standard Login Flow",
  "source": "./common/login.csv",
  "type": "csv",
  "parameters": {
    "username": "${testUser}",
    "password": "${testPassword}"
  }
}
```

#### 7. Parallel Node
Concurrent execution of child nodes.

```json
{
  "type": "parallel",
  "id": "concurrent-tests",
  "name": "Parallel Test Execution",
  "maxConcurrency": 3,
  "waitForAll": true,
  "continueOnError": false,
  "children": []
}
```

#### 8. Wait Node
Synchronization point.

```json
{
  "type": "wait",
  "id": "sync-point",
  "name": "Wait for Background Process",
  "waitType": "condition",
  "condition": "${backgroundTask.status} === 'complete'",
  "timeout": 30000,
  "pollInterval": 1000
}
```

## File Format Specification

### JSON Format (Primary)

```json
{
  "version": "1.0",
  "metadata": {
    "name": "E-commerce Test Suite",
    "description": "Complete e-commerce workflow testing",
    "author": "QA Team",
    "created": "2024-01-15T10:00:00Z",
    "updated": "2024-01-15T10:00:00Z"
  },
  "variables": {
    "global": {
      "baseUrl": "https://example.com",
      "testUser": "test@example.com"
    },
    "environment": {
      "staging": {
        "baseUrl": "https://staging.example.com"
      },
      "production": {
        "baseUrl": "https://example.com"
      }
    }
  },
  "imports": [
    "./common/auth.tree.json",
    "./common/navigation.csv"
  ],
  "root": {
    "type": "scenario",
    "id": "root",
    "children": []
  }
}
```

### YAML Format (Alternative)

```yaml
version: "1.0"
metadata:
  name: "E-commerce Test Suite"
  description: "Complete e-commerce workflow testing"
  author: "QA Team"

variables:
  global:
    baseUrl: "https://example.com"
    testUser: "test@example.com"

root:
  type: scenario
  id: root
  children:
    - type: phase
      id: setup
      name: "Test Setup"
      children:
        - type: reference
          source: "./common/auth.csv"
```

### Hybrid Format (CSV + Tree)

Support for mixing CSV files with tree structure:

```json
{
  "type": "reference",
  "source": "./login-flow.csv",
  "parameters": {
    "username": "${testUser}",
    "password": "${testPassword}"
  },
  "onComplete": {
    "type": "branch",
    "condition": "${loginResult} === 'success'",
    "branches": {
      "success": {
        "children": [
          {
            "type": "reference",
            "source": "./dashboard-tests.csv"
          }
        ]
      },
      "failure": {
        "children": [
          {
            "type": "step",
            "action": "screenshot",
            "target": "login-failure.png"
          }
        ]
      }
    }
  }
}
```

## Execution Engine

### Execution Context

```typescript
interface ExecutionContext {
  // Current state
  currentNode: TreeNode
  nodeStack: TreeNode[]
  variables: VariableStore
  
  // Execution control
  shouldStop: boolean
  shouldSkip: boolean
  shouldRetry: boolean
  
  // Results
  results: ExecutionResults
  errors: ExecutionError[]
  
  // Runtime info
  startTime: Date
  environment: string
  sessionId: string
}
```

### Execution Flow

```
1. Initialize Context
   ├── Load tree structure
   ├── Validate tree integrity
   ├── Initialize variables
   └── Setup execution environment

2. Pre-execution Phase
   ├── Resolve imports
   ├── Process variable substitutions
   ├── Validate conditions
   └── Create execution plan

3. Execute Tree
   ├── Start from root node
   ├── For each node:
   │   ├── Evaluate conditions
   │   ├── Execute node logic
   │   ├── Handle results
   │   └── Determine next node
   └── Continue until complete

4. Post-execution Phase
   ├── Collect results
   ├── Generate reports
   ├── Cleanup resources
   └── Save execution log
```

### Node Execution Rules

1. **Sequential Execution**: Children executed in order
2. **Parallel Execution**: Children executed concurrently
3. **Conditional Execution**: Based on runtime evaluation
4. **Loop Execution**: Repeated until condition met
5. **Error Handling**: Based on node configuration

## Variable System

### Variable Scopes

1. **Global**: Available throughout entire execution
2. **Scenario**: Available within scenario and children
3. **Phase**: Available within phase and children
4. **Local**: Available within single node
5. **Loop**: Available within loop iteration

### Variable Sources

```typescript
interface VariableStore {
  // Built-in variables
  system: {
    timestamp: string
    random: string
    uuid: string
    environment: string
  }
  
  // Environment variables
  env: Record<string, string>
  
  // Execution context
  execution: {
    nodeId: string
    parentId: string
    depth: number
    iteration?: number
  }
  
  // User-defined variables
  global: Record<string, any>
  scenario: Record<string, any>
  phase: Record<string, any>
  local: Record<string, any>
  
  // Data-driven variables
  data: any[]
  current: any
}
```

### Variable Resolution

```typescript
// Resolution order (highest to lowest priority)
1. Local scope
2. Loop iteration scope
3. Phase scope
4. Scenario scope
5. Global scope
6. Environment variables
7. System variables
```

### Variable Syntax

```javascript
// Simple variable reference
${variableName}

// Nested object access
${user.profile.name}

// Array access
${testData[0].username}

// Expression evaluation
${user.age > 18 ? 'adult' : 'minor'}

// Function calls
${generateRandomEmail()}

// Environment variables
${ENV.API_KEY}

// System variables
${SYSTEM.timestamp}
```

## Conditional Logic

### Condition Types

#### 1. Simple Conditions
```json
{
  "condition": "${userType} === 'admin'"
}
```

#### 2. Complex Conditions
```json
{
  "condition": "${user.age} >= 18 && ${user.verified} === true"
}
```

#### 3. Element-Based Conditions
```json
{
  "condition": "element('#error-message').isVisible()"
}
```

#### 4. Network-Based Conditions
```json
{
  "condition": "response.status === 200"
}
```

#### 5. Custom Function Conditions
```json
{
  "condition": "validateUserPermissions(${currentUser})"
}
```

### Condition Evaluation Context

```typescript
interface ConditionContext {
  // Variable access
  variables: VariableStore
  
  // DOM access
  element(selector: string): ElementHandle
  elements(selector: string): ElementHandle[]
  
  // Network access
  lastRequest: Request
  lastResponse: Response
  
  // Utility functions
  wait(ms: number): Promise<void>
  random(): number
  uuid(): string
  
  // Custom functions
  [key: string]: Function
}
```

## Error Handling

### Error Types

```typescript
enum TreeErrorType {
  PARSE_ERROR = 'PARSE_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  CONDITION_ERROR = 'CONDITION_ERROR',
  EXECUTION_ERROR = 'EXECUTION_ERROR',
  REFERENCE_ERROR = 'REFERENCE_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  DEPENDENCY_ERROR = 'DEPENDENCY_ERROR'
}
```

### Error Handling Strategies

#### Node-Level Error Handling

```json
{
  "type": "step",
  "errorHandling": {
    "strategy": "retry",
    "maxRetries": 3,
    "retryDelay": 1000,
    "onMaxRetriesReached": "continue",
    "captureScreenshot": true,
    "customHandler": "handleLoginError"
  }
}
```

#### Tree-Level Error Handling

```json
{
  "errorHandling": {
    "global": {
      "strategy": "stop",
      "reportPath": "./reports/errors.json",
      "screenshotPath": "./screenshots/errors/"
    },
    "nodeSpecific": {
      "non-critical-step": {
        "strategy": "continue"
      }
    }
  }
}
```

### Recovery Mechanisms

1. **Retry**: Repeat failed node
2. **Skip**: Continue to next node
3. **Fallback**: Execute alternative path
4. **Restart**: Restart from specific node
5. **Abort**: Stop entire execution

## Integration with CSV Framework

### CSV Reference Nodes

```json
{
  "type": "reference",
  "source": "./login-steps.csv",
  "parameters": {
    "username": "${testUser}",
    "password": "${testPassword}"
  },
  "variableMapping": {
    "result": "loginResult"
  }
}
```

### Mixed Execution

```json
{
  "type": "phase",
  "children": [
    {
      "type": "reference",
      "source": "./setup.csv"
    },
    {
      "type": "step",
      "action": "waitfor",
      "target": "#dashboard"
    },
    {
      "type": "branch",
      "condition": "${userRole} === 'admin'",
      "branches": {
        "admin": {
          "children": [
            {
              "type": "reference",
              "source": "./admin-tests.csv"
            }
          ]
        }
      }
    }
  ]
}
```

### Variable Passing

Variables can be passed between CSV files and tree nodes:

```json
{
  "type": "reference",
  "source": "./login.csv",
  "input": {
    "username": "${testUser}",
    "password": "${testPassword}"
  },
  "output": {
    "loginResult": "result",
    "sessionToken": "token"
  }
}
```

## API Specification

### Core Interfaces

```typescript
interface ScenarioTree {
  version: string
  metadata: TreeMetadata
  variables: VariableDefinitions
  imports: string[]
  root: TreeNode
}

interface TreeNode {
  type: NodeType
  id: string
  name?: string
  description?: string
  conditions?: Condition[]
  children?: TreeNode[]
  config?: NodeConfig
}

interface TreeExecutor {
  // Lifecycle
  initialize(tree: ScenarioTree, options: ExecutorOptions): Promise<void>
  execute(): Promise<ExecutionResults>
  pause(): Promise<void>
  resume(): Promise<void>
  stop(): Promise<void>
  
  // Runtime control
  setVariable(name: string, value: any, scope?: string): void
  getVariable(name: string, scope?: string): any
  evaluateCondition(condition: string): Promise<boolean>
  
  // Event handling
  on(event: string, handler: Function): void
  off(event: string, handler: Function): void
  
  // Debugging
  getCurrentNode(): TreeNode
  getExecutionStack(): TreeNode[]
  getExecutionHistory(): ExecutionStep[]
}
```

### Event System

```typescript
interface TreeEvents {
  // Execution events
  'execution.start': (context: ExecutionContext) => void
  'execution.complete': (results: ExecutionResults) => void
  'execution.error': (error: ExecutionError) => void
  
  // Node events
  'node.enter': (node: TreeNode, context: ExecutionContext) => void
  'node.exit': (node: TreeNode, result: NodeResult) => void
  'node.error': (node: TreeNode, error: NodeError) => void
  
  // Variable events
  'variable.set': (name: string, value: any, scope: string) => void
  'variable.get': (name: string, scope: string) => void
  
  // Condition events
  'condition.evaluate': (condition: string, result: boolean) => void
}
```

## Examples

### Example 1: Simple Login Flow

```json
{
  "version": "1.0",
  "metadata": {
    "name": "Login Flow Test"
  },
  "variables": {
    "global": {
      "username": "test@example.com",
      "password": "TestPass123!"
    }
  },
  "root": {
    "type": "scenario",
    "id": "login-test",
    "children": [
      {
        "type": "step",
        "action": "navigate",
        "target": "https://example.com/login"
      },
      {
        "type": "step",
        "action": "type",
        "target": "#username",
        "value": "${username}"
      },
      {
        "type": "step",
        "action": "type",
        "target": "#password",
        "value": "${password}"
      },
      {
        "type": "step",
        "action": "click",
        "target": "#login-button"
      },
      {
        "type": "branch",
        "condition": "element('#error-message').isVisible()",
        "branches": {
          "error": {
            "condition": "element('#error-message').isVisible()",
            "children": [
              {
                "type": "step",
                "action": "screenshot",
                "target": "login-error.png"
              }
            ]
          },
          "success": {
            "children": [
              {
                "type": "step",
                "action": "asserturl",
                "target": "https://example.com/dashboard"
              }
            ]
          }
        }
      }
    ]
  }
}
```

### Example 2: Data-Driven Test

```json
{
  "version": "1.0",
  "metadata": {
    "name": "User Registration Test"
  },
  "variables": {
    "global": {
      "testUsers": [
        {"name": "John Doe", "email": "john@example.com", "valid": true},
        {"name": "", "email": "invalid-email", "valid": false}
      ]
    }
  },
  "root": {
    "type": "scenario",
    "id": "registration-test",
    "children": [
      {
        "type": "loop",
        "loopType": "forEach",
        "data": "${testUsers}",
        "variable": "user",
        "children": [
          {
            "type": "phase",
            "name": "Test User: ${user.name}",
            "children": [
              {
                "type": "step",
                "action": "navigate",
                "target": "https://example.com/register"
              },
              {
                "type": "step",
                "action": "type",
                "target": "#name",
                "value": "${user.name}"
              },
              {
                "type": "step",
                "action": "type",
                "target": "#email",
                "value": "${user.email}"
              },
              {
                "type": "step",
                "action": "click",
                "target": "#submit"
              },
              {
                "type": "branch",
                "condition": "${user.valid}",
                "branches": {
                  "valid": {
                    "condition": "${user.valid} === true",
                    "children": [
                      {
                        "type": "step",
                        "action": "asserttext",
                        "target": ".success-message",
                        "value": "Registration successful"
                      }
                    ]
                  },
                  "invalid": {
                    "children": [
                      {
                        "type": "step",
                        "action": "assertvisible",
                        "target": ".error-message"
                      }
                    ]
                  }
                }
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### Example 3: Complex E-commerce Flow

```json
{
  "version": "1.0",
  "metadata": {
    "name": "E-commerce Checkout Flow"
  },
  "imports": [
    "./common/auth.tree.json",
    "./common/product-search.csv"
  ],
  "variables": {
    "global": {
      "products": ["laptop", "mouse", "keyboard"],
      "paymentMethod": "credit-card"
    }
  },
  "root": {
    "type": "scenario",
    "id": "checkout-flow",
    "children": [
      {
        "type": "phase",
        "id": "setup",
        "name": "Test Setup",
        "children": [
          {
            "type": "reference",
            "source": "./common/auth.tree.json"
          }
        ]
      },
      {
        "type": "phase",
        "id": "shopping",
        "name": "Shopping Phase",
        "children": [
          {
            "type": "loop",
            "loopType": "forEach",
            "data": "${products}",
            "variable": "product",
            "children": [
              {
                "type": "reference",
                "source": "./common/product-search.csv",
                "parameters": {
                  "searchTerm": "${product}"
                }
              },
              {
                "type": "step",
                "action": "click",
                "target": ".add-to-cart"
              }
            ]
          }
        ]
      },
      {
        "type": "phase",
        "id": "checkout",
        "name": "Checkout Phase",
        "children": [
          {
            "type": "step",
            "action": "click",
            "target": "#cart-button"
          },
          {
            "type": "step",
            "action": "click",
            "target": "#checkout-button"
          },
          {
            "type": "branch",
            "condition": "${paymentMethod} === 'credit-card'",
            "branches": {
              "credit-card": {
                "children": [
                  {
                    "type": "reference",
                    "source": "./payment/credit-card.csv"
                  }
                ]
              },
              "paypal": {
                "children": [
                  {
                    "type": "reference",
                    "source": "./payment/paypal.csv"
                  }
                ]
              }
            }
          }
        ]
      }
    ]
  }
}
```

## Version History

- **v1.0** (2024-01-15): Initial specification

## Future Considerations

- Visual tree editor
- Real-time execution monitoring
- Distributed execution across multiple browsers
- AI-powered test generation
- Integration with CI/CD pipelines
- Performance testing capabilities
- Visual regression testing
- API testing integration
- Mobile device support
- Cloud execution support
