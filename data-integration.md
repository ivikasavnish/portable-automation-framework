# Dynamic Data & External Integration Specification v1.0

## Table of Contents
1. [Overview](#overview)
2. [Data Provider Specification](#data-provider-specification)
3. [Database Integration](#database-integration)
4. [API Integration](#api-integration)
5. [RPC Call Specification](#rpc-call-specification)
6. [CSV Action Extensions](#csv-action-extensions)
7. [Scenario Tree Integration](#scenario-tree-integration)
8. [Data Transformation](#data-transformation)
9. [Caching and Performance](#caching-and-performance)
10. [Security and Authentication](#security-and-authentication)
11. [Error Handling](#error-handling)
12. [Configuration Management](#configuration-management)
13. [Examples](#examples)

## Overview

This specification extends the Browser Automation Framework to support dynamic data retrieval, database operations, and external service integration through APIs and RPC calls. It provides a unified interface for managing external data sources and real-time data interactions during test execution.

### Core Principles
- **Unified Interface**: Consistent API for all data sources
- **Real-time Data**: Dynamic data retrieval during test execution
- **Multiple Protocols**: Support for REST, GraphQL, gRPC, and custom RPC
- **Database Agnostic**: Support for SQL and NoSQL databases
- **Caching Strategy**: Intelligent caching for performance
- **Security First**: Built-in authentication and data protection
- **Extensible**: Plugin architecture for custom integrations

## Data Provider Specification

### Core Data Provider Interface

```typescript
interface DataProvider {
  // Identification
  id: string
  type: DataProviderType
  name: string
  
  // Lifecycle
  initialize(config: DataProviderConfig): Promise<void>
  connect(): Promise<void>
  disconnect(): Promise<void>
  healthCheck(): Promise<HealthStatus>
  
  // Data operations
  get(query: DataQuery): Promise<DataResult>
  set(mutation: DataMutation): Promise<DataResult>
  delete(query: DataQuery): Promise<DataResult>
  
  // Advanced operations
  subscribe(query: DataQuery, callback: DataCallback): Promise<Subscription>
  batch(operations: DataOperation[]): Promise<DataResult[]>
  transaction(operations: DataOperation[]): Promise<DataResult[]>
  
  // Metadata
  getSchema(): Promise<DataSchema>
  getCapabilities(): DataCapabilities
}
```

### Data Provider Types

```typescript
enum DataProviderType {
  DATABASE = 'database',
  REST_API = 'rest-api',
  GRAPHQL = 'graphql',
  GRPC = 'grpc',
  WEBSOCKET = 'websocket',
  FILE_SYSTEM = 'file-system',
  REDIS = 'redis',
  ELASTICSEARCH = 'elasticsearch',
  CUSTOM = 'custom'
}
```

### Data Query Interface

```typescript
interface DataQuery {
  // Basic query info
  id?: string
  provider: string
  operation: 'select' | 'insert' | 'update' | 'delete' | 'call'
  
  // Query specification
  resource: string
  parameters?: Record<string, any>
  filters?: QueryFilter[]
  sorting?: SortOption[]
  pagination?: PaginationOptions
  
  // Options
  timeout?: number
  retries?: number
  cache?: CacheOptions
  authentication?: AuthConfig
  
  // Post-processing
  transform?: DataTransform[]
  validation?: ValidationRule[]
}
```

## Database Integration

### SQL Database Provider

```typescript
interface SQLDatabaseConfig extends DataProviderConfig {
  type: 'sql'
  driver: 'mysql' | 'postgresql' | 'sqlite' | 'mssql' | 'oracle'
  connection: {
    host: string
    port: number
    database: string
    username: string
    password: string
    ssl?: SSLConfig
    pool?: PoolConfig
  }
  options?: {
    charset?: string
    timezone?: string
    acquireTimeout?: number
    timeout?: number
  }
}
```

#### SQL Query Examples

```csv
# CSV Format
action,target,value,options,description
dbquery,users,"SELECT * FROM users WHERE status = 'active'","{"provider": "main-db", "cache": true}",Get active users
dbset,user_sessions,"INSERT INTO user_sessions (user_id, token) VALUES (${userId}, ${sessionToken})","{"provider": "main-db"}",Create session
dbcall,update_user_stats,"CALL update_user_stats(${userId})","{"provider": "main-db"}",Update user statistics
```

```json
// Scenario Tree Format
{
  "type": "data",
  "operation": "query",
  "provider": "main-db",
  "query": {
    "sql": "SELECT * FROM products WHERE category = ? AND price < ?",
    "parameters": ["${category}", "${maxPrice}"]
  },
  "output": "availableProducts"
}
```

### NoSQL Database Provider

```typescript
interface NoSQLDatabaseConfig extends DataProviderConfig {
  type: 'nosql'
  driver: 'mongodb' | 'dynamodb' | 'cosmosdb' | 'couchdb'
  connection: {
    uri: string
    database: string
    collection?: string
    options?: ConnectionOptions
  }
}
```

#### NoSQL Query Examples

```json
// MongoDB Query
{
  "type": "data",
  "operation": "query",
  "provider": "mongo-db",
  "query": {
    "collection": "users",
    "filter": {"status": "active", "age": {"$gte": 18}},
    "projection": {"name": 1, "email": 1},
    "sort": {"created_at": -1},
    "limit": 50
  },
  "output": "activeUsers"
}

// DynamoDB Query
{
  "type": "data",
  "operation": "query",
  "provider": "dynamo-db",
  "query": {
    "table": "UserSessions",
    "keyCondition": "userId = :userId",
    "expressionAttributeValues": {
      ":userId": "${currentUserId}"
    }
  },
  "output": "userSessions"
}
```

## API Integration

### REST API Provider

```typescript
interface RestApiConfig extends DataProviderConfig {
  type: 'rest-api'
  baseUrl: string
  authentication?: {
    type: 'bearer' | 'basic' | 'apikey' | 'oauth2'
    config: AuthenticationConfig
  }
  defaultHeaders?: Record<string, string>
  timeout?: number
  retries?: RetryConfig
}
```

#### REST API Examples

```csv
# CSV Format
action,target,value,options,description
apiget,/api/users,,"{"provider": "user-api", "headers": {"X-Custom": "value"}}",Get users
apipost,/api/users,"{"name": "${userName}", "email": "${userEmail}"}","{"provider": "user-api"}",Create user
apiput,/api/users/${userId},"{"status": "active"}","{"provider": "user-api"}",Update user
apidelete,/api/users/${userId},,"{"provider": "user-api"}",Delete user
```

```json
// Scenario Tree Format
{
  "type": "api",
  "operation": "request",
  "provider": "user-api",
  "request": {
    "method": "POST",
    "endpoint": "/api/authenticate",
    "body": {
      "username": "${testUser}",
      "password": "${testPassword}"
    },
    "headers": {
      "Content-Type": "application/json"
    }
  },
  "response": {
    "extract": {
      "authToken": "$.data.token",
      "userId": "$.data.user.id"
    },
    "validate": {
      "status": 200,
      "schema": "./schemas/auth-response.json"
    }
  }
}
```

### GraphQL Provider

```typescript
interface GraphQLConfig extends DataProviderConfig {
  type: 'graphql'
  endpoint: string
  authentication?: AuthenticationConfig
  defaultVariables?: Record<string, any>
  introspection?: boolean
}
```

#### GraphQL Examples

```json
// Query
{
  "type": "graphql",
  "operation": "query",
  "provider": "main-graphql",
  "query": {
    "query": `
      query GetUserProfile($userId: ID!) {
        user(id: $userId) {
          id
          name
          email
          profile {
            avatar
            preferences
          }
        }
      }
    `,
    "variables": {
      "userId": "${currentUserId}"
    }
  },
  "output": "userProfile"
}

// Mutation
{
  "type": "graphql",
  "operation": "mutation",
  "provider": "main-graphql",
  "query": {
    "query": `
      mutation UpdateUserProfile($userId: ID!, $profile: ProfileInput!) {
        updateUserProfile(userId: $userId, profile: $profile) {
          success
          user {
            id
            profile {
              avatar
              preferences
            }
          }
        }
      }
    `,
    "variables": {
      "userId": "${currentUserId}",
      "profile": "${updatedProfile}"
    }
  },
  "output": "updateResult"
}
```

## RPC Call Specification

### gRPC Provider

```typescript
interface GRPCConfig extends DataProviderConfig {
  type: 'grpc'
  address: string
  protoFile: string
  packageName: string
  serviceName: string
  authentication?: {
    type: 'ssl' | 'token' | 'mutual-tls'
    config: GRPCAuthConfig
  }
  options?: {
    keepalive?: boolean
    compression?: 'gzip' | 'deflate'
    maxMessageSize?: number
  }
}
```

#### gRPC Examples

```json
// Unary Call
{
  "type": "grpc",
  "operation": "call",
  "provider": "user-service",
  "call": {
    "method": "GetUser",
    "request": {
      "userId": "${targetUserId}",
      "includeProfile": true
    }
  },
  "output": "userDetails"
}

// Streaming Call
{
  "type": "grpc",
  "operation": "stream",
  "provider": "notification-service",
  "call": {
    "method": "SubscribeToNotifications",
    "request": {
      "userId": "${currentUserId}",
      "types": ["email", "push"]
    }
  },
  "streaming": {
    "timeout": 30000,
    "onMessage": "handleNotification",
    "onEnd": "completeNotificationTest"
  }
}
```

### Custom RPC Provider

```typescript
interface CustomRPCConfig extends DataProviderConfig {
  type: 'custom-rpc'
  protocol: 'tcp' | 'udp' | 'ws' | 'http'
  endpoint: string
  serialization: 'json' | 'protobuf' | 'msgpack' | 'xml'
  authentication?: AuthenticationConfig
  customOptions?: Record<string, any>
}
```

## CSV Action Extensions

### New CSV Actions for Data Operations

| Action | Target | Value | Options | Description |
|--------|--------|-------|---------|-------------|
| dbquery | table/query | SQL/query | provider, timeout | Execute database query |
| dbset | table | data | provider, timeout | Insert/update database record |
| dbdelete | table | condition | provider, timeout | Delete database records |
| dbcall | procedure | parameters | provider, timeout | Call stored procedure |
| apiget | endpoint | - | provider, headers | HTTP GET request |
| apipost | endpoint | body | provider, headers | HTTP POST request |
| apiput | endpoint | body | provider, headers | HTTP PUT request |
| apidelete | endpoint | - | provider, headers | HTTP DELETE request |
| gqlquery | query | variables | provider, timeout | GraphQL query |
| gqlmutation | mutation | variables | provider, timeout | GraphQL mutation |
| rpcall | method | parameters | provider, timeout | RPC method call |
| datastore | key | value | scope, ttl | Store data in memory |
| dataget | key | - | scope, default | Retrieve stored data |
| dataclear | pattern | - | scope | Clear stored data |
| datawait | condition | - | timeout, interval | Wait for data condition |

### Enhanced CSV Examples

```csv
# Database operations
action,target,value,options,description
dbquery,users,"SELECT id, name FROM users WHERE role = 'admin'","{"provider": "main-db", "output": "adminUsers"}",Get admin users
datastore,currentAdmins,${adminUsers},"{"scope": "global"}",Store admin list
dbset,audit_log,"INSERT INTO audit_log (action, user_id) VALUES ('login_test', ${adminUsers[0].id})","{"provider": "main-db"}",Log test action

# API operations  
action,target,value,options,description
apipost,/api/auth/login,"{"username": "${testUser}", "password": "${testPass}"}","{"provider": "api", "output": "authResponse"}",Login via API
datastore,authToken,${authResponse.token},"{"scope": "session"}",Store auth token
apiget,/api/profile,,"{"provider": "api", "headers": {"Authorization": "Bearer ${authToken}"}, "output": "userProfile"}",Get user profile
assertvalue,${userProfile.name},John Doe,,Verify profile name

# RPC operations
action,target,value,options,description
rpcall,getUserPermissions,"{"userId": "${userProfile.id}"}","{"provider": "auth-service", "output": "permissions"}",Get user permissions
datawait,${permissions.loaded},true,"{"timeout": 5000}",Wait for permissions to load
gqlquery,"query { user(id: \"${userProfile.id}\") { posts { title } } }",,"{"provider": "graphql", "output": "userPosts"}",Get user posts
```

## Scenario Tree Integration

### Data Nodes in Scenario Tree

```json
{
  "type": "data",
  "id": "fetch-test-data",
  "name": "Fetch Test Data",
  "provider": "test-db",
  "operation": "query",
  "query": {
    "sql": "SELECT * FROM test_scenarios WHERE environment = ?",
    "parameters": ["${environment}"]
  },
  "output": "testScenarios",
  "cache": {
    "enabled": true,
    "ttl": 300000,
    "key": "test-scenarios-${environment}"
  },
  "errorHandling": {
    "strategy": "retry",
    "maxRetries": 3,
    "fallback": {
      "type": "file",
      "source": "./fallback-data/scenarios.json"
    }
  }
}
```

### Data-Driven Loop with External Data

```json
{
  "type": "loop",
  "id": "test-all-users",
  "name": "Test All Active Users",
  "loopType": "forEach",
  "dataSource": {
    "type": "data",
    "provider": "user-db",
    "query": {
      "sql": "SELECT id, email, role FROM users WHERE status = 'active' LIMIT 10"
    }
  },
  "variable": "testUser",
  "children": [
    {
      "type": "phase",
      "name": "Test User: ${testUser.email}",
      "children": [
        {
          "type": "data",
          "provider": "api",
          "operation": "request",
          "request": {
            "method": "POST",
            "endpoint": "/api/impersonate",
            "body": {"userId": "${testUser.id}"}
          },
          "output": "impersonationToken"
        },
        {
          "type": "reference",
          "source": "./user-workflows.csv",
          "parameters": {
            "authToken": "${impersonationToken}",
            "userRole": "${testUser.role}"
          }
        }
      ]
    }
  ]
}
```

### Conditional Execution Based on External Data

```json
{
  "type": "branch",
  "id": "feature-flag-branch",
  "name": "Feature Flag Conditional",
  "condition": {
    "type": "data",
    "provider": "config-service",
    "query": {
      "method": "GET",
      "endpoint": "/api/features/${featureName}/enabled"
    },
    "expression": "response.enabled === true"
  },
  "branches": {
    "enabled": {
      "children": [
        {
          "type": "reference",
          "source": "./new-feature-tests.csv"
        }
      ]
    },
    "disabled": {
      "children": [
        {
          "type": "step",
          "action": "echo",
          "value": "Feature ${featureName} is disabled, skipping tests"
        }
      ]
    }
  }
}
```

## Data Transformation

### Transformation Pipeline

```typescript
interface DataTransform {
  type: TransformType
  config: TransformConfig
  
  // Transform function
  transform(input: any): any
}

enum TransformType {
  MAP = 'map',
  FILTER = 'filter',
  REDUCE = 'reduce',
  SORT = 'sort',
  GROUP = 'group',
  JOIN = 'join',
  EXTRACT = 'extract',
  VALIDATE = 'validate',
  CUSTOM = 'custom'
}
```

### Transformation Examples

```json
// Map transformation
{
  "type": "map",
  "config": {
    "expression": "item => ({ id: item.user_id, name: item.full_name, email: item.email_address })"
  }
}

// Filter transformation
{
  "type": "filter",
  "config": {
    "condition": "item.age >= 18 && item.verified === true"
  }
}

// JSONPath extraction
{
  "type": "extract",
  "config": {
    "paths": {
      "userIds": "$.data[*].id",
      "totalCount": "$.meta.total",
      "nextPage": "$.meta.pagination.next"
    }
  }
}

// Schema validation
{
  "type": "validate",
  "config": {
    "schema": {
      "type": "object",
      "required": ["id", "name", "email"],
      "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
      }
    }
  }
}
```

### Chain Transformations

```json
{
  "type": "data",
  "provider": "user-api",
  "query": {
    "endpoint": "/api/users",
    "method": "GET"
  },
  "transforms": [
    {
      "type": "extract",
      "config": {
        "path": "$.data"
      }
    },
    {
      "type": "filter",
      "config": {
        "condition": "item.status === 'active'"
      }
    },
    {
      "type": "map",
      "config": {
        "expression": "item => ({ ...item, fullName: `${item.firstName} ${item.lastName}` })"
      }
    },
    {
      "type": "sort",
      "config": {
        "field": "created_at",
        "order": "desc"
      }
    }
  ],
  "output": "processedUsers"
}
```

## Caching and Performance

### Cache Configuration

```typescript
interface CacheConfig {
  enabled: boolean
  provider: 'memory' | 'redis' | 'file' | 'custom'
  ttl?: number
  maxSize?: number
  key?: string | KeyGenerator
  tags?: string[]
  invalidation?: InvalidationStrategy
}

interface KeyGenerator {
  template: string
  parameters: string[]
}
```

### Cache Examples

```json
// Simple TTL cache
{
  "cache": {
    "enabled": true,
    "ttl": 300000,
    "key": "user-list-${environment}"
  }
}

// Redis cache with tags
{
  "cache": {
    "enabled": true,
    "provider": "redis",
    "ttl": 600000,
    "key": "product-${category}-${page}",
    "tags": ["products", "catalog"],
    "invalidation": {
      "strategy": "tag-based",
      "triggers": ["product-update", "catalog-refresh"]
    }
  }
}

// Smart cache with dependencies
{
  "cache": {
    "enabled": true,
    "key": {
      "template": "user-permissions-${userId}-${roleVersion}",
      "parameters": ["userId", "roleVersion"]
    },
    "dependencies": [
      "user-${userId}",
      "role-definitions"
    ]
  }
}
```

### Performance Optimization

```json
{
  "type": "parallel",
  "id": "fetch-user-data",
  "name": "Fetch User Data in Parallel",
  "children": [
    {
      "type": "data",
      "provider": "user-db",
      "query": {
        "sql": "SELECT * FROM users WHERE id = ?",
        "parameters": ["${userId}"]
      },
      "output": "userData",
      "cache": {"enabled": true, "ttl": 60000}
    },
    {
      "type": "data",
      "provider": "permission-service",
      "query": {
        "method": "getUserPermissions",
        "parameters": {"userId": "${userId}"}
      },
      "output": "userPermissions",
      "cache": {"enabled": true, "ttl": 300000}
    },
    {
      "type": "data",
      "provider": "audit-service",
      "query": {
        "endpoint": "/api/audit/recent/${userId}",
        "method": "GET"
      },
      "output": "recentActivity"
    }
  ]
}
```

## Security and Authentication

### Authentication Providers

```typescript
interface AuthenticationProvider {
  type: AuthType
  config: AuthConfig
  
  // Methods
  authenticate(): Promise<AuthToken>
  refresh(token: AuthToken): Promise<AuthToken>
  validate(token: AuthToken): Promise<boolean>
  revoke(token: AuthToken): Promise<void>
}

enum AuthType {
  BASIC = 'basic',
  BEARER = 'bearer',
  API_KEY = 'api-key',
  OAUTH2 = 'oauth2',
  JWT = 'jwt',
  MUTUAL_TLS = 'mutual-tls',
  CUSTOM = 'custom'
}
```

### Authentication Examples

```json
// OAuth2 Configuration
{
  "authentication": {
    "type": "oauth2",
    "config": {
      "clientId": "${CLIENT_ID}",
      "clientSecret": "${CLIENT_SECRET}",
      "tokenUrl": "https://auth.example.com/oauth/token",
      "scopes": ["read:users", "write:users"],
      "grantType": "client_credentials"
    }
  }
}

// JWT Token Configuration
{
  "authentication": {
    "type": "jwt",
    "config": {
      "token": "${JWT_TOKEN}",
      "header": "Authorization",
      "prefix": "Bearer",
      "refresh": {
        "enabled": true,
        "endpoint": "/auth/refresh",
        "threshold": 300000
      }
    }
  }
}

// API Key Configuration
{
  "authentication": {
    "type": "api-key",
    "config": {
      "key": "${API_KEY}",
      "location": "header",
      "name": "X-API-Key"
    }
  }
}
```

### Data Encryption and Security

```json
{
  "type": "data",
  "provider": "secure-db",
  "query": {
    "sql": "SELECT * FROM sensitive_data WHERE user_id = ?",
    "parameters": ["${userId}"]
  },
  "security": {
    "encryption": {
      "enabled": true,
      "fields": ["ssn", "credit_card"],
      "algorithm": "AES-256-GCM"
    },
    "masking": {
      "enabled": true,
      "rules": {
        "email": "keep-domain",
        "phone": "last-4-digits"
      }
    },
    "audit": {
      "enabled": true,
      "logSensitiveAccess": true
    }
  }
}
```

## Error Handling

### Error Types for Data Operations

```typescript
enum DataErrorType {
  CONNECTION_ERROR = 'CONNECTION_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  QUERY_ERROR = 'QUERY_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  TRANSFORMATION_ERROR = 'TRANSFORMATION_ERROR',
  CACHE_ERROR = 'CACHE_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR'
}
```

### Comprehensive Error Handling

```json
{
  "type": "data",
  "provider": "external-api",
  "query": {
    "endpoint": "/api/critical-data",
    "method": "GET"
  },
  "errorHandling": {
    "retries": {
      "maxAttempts": 3,
      "backoff": "exponential",
      "baseDelay": 1000,
      "maxDelay": 10000
    },
    "fallback": {
      "strategy": "cascade",
      "options": [
        {
          "type": "cache",
          "maxAge": 3600000
        },
        {
          "type": "provider",
          "provider": "backup-api"
        },
        {
          "type": "static",
          "data": "./fallback-data.json"
        }
      ]
    },
    "circuit-breaker": {
      "enabled": true,
      "failureThreshold": 5,
      "timeout": 60000,
      "halfOpenRetries": 3
    }
  }
}
```

## Configuration Management

### Provider Configuration

```json
{
  "providers": {
    "main-db": {
      "type": "sql",
      "driver": "postgresql",
      "connection": {
        "host": "${DB_HOST}",
        "port": 5432,
        "database": "${DB_NAME}",
        "username": "${DB_USER}",
        "password": "${DB_PASSWORD}",
        "ssl": true
      },
      "pool": {
        "min": 2,
        "max": 10,
        "acquireTimeout": 30000
      }
    },
    "user-api": {
      "type": "rest-api",
      "baseUrl": "${API_BASE_URL}",
      "authentication": {
        "type": "bearer",
        "token": "${API_TOKEN}"
      },
      "defaultHeaders": {
        "Content-Type": "application/json",
        "User-Agent": "Test-Framework/1.0"
      },
      "timeout": 10000
    },
    "notification-service": {
      "type": "grpc",
      "address": "${GRPC_HOST}:${GRPC_PORT}",
      "protoFile": "./protos/notification.proto",
      "packageName": "notification",
      "serviceName": "NotificationService",
      "authentication": {
        "type": "ssl",
        "certFile": "./certs/client.crt",
        "keyFile": "./certs/client.key"
      }
    }
  },
  "cache": {
    "default": {
      "provider": "memory",
      "maxSize": 1000,
      "ttl": 300000
    },
    "redis": {
      "provider": "redis",
      "host": "${REDIS_HOST}",
      "port": 6379,
      "password": "${REDIS_PASSWORD}",
      "db": 0
    }
  }
}
```

## Examples

### Example 1: Complete E-commerce Test with External Data

```csv
# Setup test data
action,target,value,options,description
dbquery,products,"SELECT id, name, price FROM products WHERE featured = true LIMIT 5","{"provider": "shop-db", "output": "featuredProducts"}",Get featured products
datastore,testProducts,${featuredProducts},"{"scope": "scenario"}",Store products for test
apipost,/api/test/user,"{"email": ""test@example.com"", ""role"": ""customer""}","{"provider": "user-api", "output": "testUser"}",Create test user

# Main test flow
navigate,${baseUrl}/shop,,,Navigate to shop
waitfor,.product-grid,,"{"timeout": 10000}",Wait for products to load

# Loop through each product
dataloop,testProducts,product,,Start product loop
click,"[data-product-id='${product.id}']",,,Click on product
waitfor,.product-details,,,Wait for product details
asserttext,.product-name,${product.name},,Verify product name
asserttext,.product-price,$${product.price},,Verify product price
click,.add-to-cart,,,Add to cart
waitfor,.cart-notification,,,Wait for cart confirmation
dataendloop,,,End product loop

# Checkout process
click,.cart-icon,,,Open cart
assertcount,.cart-item,${testProducts.length},,Verify cart item count
click,.checkout-button,,,Start checkout

# Use API to verify order
apiget,/api/orders/cart/${testUser.id},,"{"provider": "order-api", "output": "cartData"}",Get cart via API
assertvalue,${cartData.items.length},${testProducts.length},,Verify API cart data

# Cleanup
apidelete,/api/test/user/${testUser.id},,"{"provider": "user-api"}",Delete test user
```

### Example 2: Data-Driven User Permission Testing

```json
{
  "version": "1.0",
  "metadata": {
    "name": "User Permission Matrix Test"
  },
  "providers": {
    "user-db": {
      "type": "sql",
      "connection": "postgresql://user:pass@localhost/testdb"
    },
    "auth-api": {
      "type": "rest-api",
      "baseUrl": "https://api.example.com"
    }
  },
  "root": {
    "type": "scenario",
    "children": [
      {
        "type": "data",
        "id": "fetch-test-matrix",
        "provider": "user-db",
        "query": {
          "sql": `
            SELECT u.id, u.email, r.name as role, p.resource, p.action, p.allowed
            FROM users u
            JOIN user_roles ur ON u.id = ur.user_id
            JOIN roles r ON ur.role_id = r.id
            JOIN role_permissions rp ON r.id = rp.role_id
            JOIN permissions p ON rp.permission_id = p.id
            WHERE u.status = 'active'
            ORDER BY u.id, p.resource, p.action
          `
        },
        "transforms": [
          {
            "type": "group",
            "config": {
              "groupBy": "id",
              "aggregate": {
                "email": "first",
                "role": "first",
                "permissions": "collect"
              }
            }
          }
        ],
        "output": "userPermissionMatrix"
      },
      {
        "type": "loop",
        "loopType": "forEach",
        "data": "${userPermissionMatrix}",
        "variable": "userTest",
        "children": [
          {
            "type": "phase",
            "name": "Test User: ${userTest.email}",
            "children": [
              {
                "type": "data",
                "provider": "auth-api",
                "operation": "request",
                "request": {
                  "method": "POST",
                  "endpoint": "/api/auth/impersonate",
                  "body": {
                    "userId": "${userTest.id}",
                    "reason": "permission_testing"
                  }
                },
                "output": "impersonationToken"
              },
              {
                "type": "loop",
                "loopType": "forEach",
                "data": "${userTest.permissions}",
                "variable": "permission",
                "children": [
                  {
                    "type": "step",
                    "action": "navigate",
                    "target": "${baseUrl}${permission.resource}"
                  },
                  {
                    "type": "data",
                    "provider": "auth-api",
                    "operation": "request",
                    "request": {
                      "method": "GET",
                      "endpoint": "/api/permissions/check",
                      "headers": {
                        "Authorization": "Bearer ${impersonationToken}"
                      },
                      "query": {
                        "resource": "${permission.resource}",
                        "action": "${permission.action}"
                      }
                    },
                    "output": "permissionCheck"
                  },
                  {
                    "type": "branch",
                    "condition": "${permission.allowed}",
                    "branches": {
                      "allowed": {
                        "condition": "${permission.allowed} === true",
                        "children": [
                          {
                            "type": "step",
                            "action": "assertvisible",
                            "target": "[data-action='${permission.action}']",
                            "description": "Verify ${permission.action} button is visible"
                          },
                          {
                            "type": "step",
                            "action": "assertvalue",
                            "target": "${permissionCheck.allowed}",
                            "value": "true",
                            "description": "Verify API reports permission as allowed"
                          }
                        ]
                      },
                      "denied": {
                        "children": [
                          {
                            "type": "step",
                            "action": "asserthidden",
                            "target": "[data-action='${permission.action}']",
                            "description": "Verify ${permission.action} button is hidden"
                          },
                          {
                            "type": "step",
                            "action": "assertvalue",
                            "target": "${permissionCheck.allowed}",
                            "value": "false",
                            "description": "Verify API reports permission as denied"
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
    ]
  }
}
```

### Example 3: Real-time Data Monitoring Test

```json
{
  "version": "1.0",
  "metadata": {
    "name": "Real-time Dashboard Test"
  },
  "providers": {
    "metrics-db": {
      "type": "sql",
      "driver": "mysql",
      "connection": "mysql://user:pass@localhost/metrics"
    },
    "websocket-api": {
      "type": "websocket",
      "endpoint": "wss://api.example.com/live-metrics",
      "authentication": {
        "type": "bearer",
        "token": "${WS_TOKEN}"
      }
    },
    "notification-service": {
      "type": "grpc",
      "address": "localhost:50051",
      "protoFile": "./protos/notifications.proto"
    }
  },
  "root": {
    "type": "scenario",
    "children": [
      {
        "type": "parallel",
        "id": "setup-monitoring",
        "children": [
          {
            "type": "data",
            "provider": "websocket-api",
            "operation": "subscribe",
            "subscription": {
              "channel": "system-metrics",
              "filter": {
                "type": "cpu_usage"
              }
            },
            "output": "liveMetrics",
            "streaming": {
              "bufferSize": 100,
              "timeout": 60000
            }
          },
          {
            "type": "data",
            "provider": "notification-service",
            "operation": "call",
            "call": {
              "method": "SubscribeToAlerts",
              "request": {
                "userId": "${testUserId}",
                "alertTypes": ["CRITICAL", "WARNING"]
              }
            },
            "output": "alertStream",
            "streaming": {
              "timeout": 60000,
              "onMessage": "handleAlert"
            }
          }
        ]
      },
      {
        "type": "step",
        "action": "navigate",
        "target": "${baseUrl}/dashboard/live"
      },
      {
        "type": "step",
        "action": "waitfor",
        "target": ".metrics-chart",
        "options": {"timeout": 10000}
      },
      {
        "type": "data",
        "provider": "metrics-db",
        "operation": "query",
        "query": {
          "sql": "INSERT INTO synthetic_load (cpu_percent, timestamp) VALUES (85, NOW())"
        }
      },
      {
        "type": "wait",
        "waitType": "condition",
        "condition": "${liveMetrics.latest.cpu_usage} >= 80",
        "timeout": 30000,
        "pollInterval": 1000
      },
      {
        "type": "step",
        "action": "asserttext",
        "target": ".cpu-metric .value",
        "value": "${liveMetrics.latest.cpu_usage}%",
        "description": "Verify dashboard shows live CPU usage"
      },
      {
        "type": "branch",
        "condition": "${alertStream.hasAlert}",
        "branches": {
          "alert_received": {
            "condition": "${alertStream.hasAlert} === true",
            "children": [
              {
                "type": "step",
                "action": "assertvisible",
                "target": ".alert-notification",
                "description": "Verify alert notification appears"
              },
              {
                "type": "step",
                "action": "asserttext",
                "target": ".alert-notification .message",
                "value": "${alertStream.latestAlert.message}",
                "description": "Verify alert message matches"
              }
            ]
          },
          "no_alert": {
            "children": [
              {
                "type": "step",
                "action": "echo",
                "value": "No alert received within timeout period"
              }
            ]
          }
        }
      }
    ]
  }
}
```

### Example 4: Complex Multi-System Integration Test

```csv
# Multi-system order processing test
action,target,value,options,description

# Setup test data across multiple systems
dbquery,inventory,"SELECT product_id, quantity FROM inventory WHERE quantity > 10 LIMIT 3","{"provider": "inventory-db", "output": "availableProducts"}",Get available products
apipost,/api/customers,"{"name": "Test Customer", "email": "test@example.com"}","{"provider": "crm-api", "output": "testCustomer"}",Create test customer
rpcall,createAccount,"{"customerId": "${testCustomer.id}", "accountType": "premium"}","{"provider": "billing-service", "output": "customerAccount"}",Create billing account

# Navigate and create order
navigate,${baseUrl}/admin/orders,,,Navigate to order management
click,#new-order,,,Start new order
type,#customer-search,${testCustomer.email},,Search for customer
click,.customer-result:first-child,,,Select customer

# Add products to order
dataloop,availableProducts,product,,Loop through products
type,#product-search,${product.product_id},,Search for product
click,.product-result:first-child,,,Select product
type,#quantity,2,,Set quantity
click,#add-to-order,,,Add to order
dataendloop,,,End product loop

# Submit order and verify across systems
click,#submit-order,,,Submit order
waitfor,.order-confirmation,,"{"timeout": 10000}",Wait for confirmation
datastore,orderId,${document.querySelector('.order-id').textContent},,Store order ID

# Verify order in database
dbquery,orders,"SELECT * FROM orders WHERE id = ?","{"provider": "order-db", "parameters": ["${orderId}"], "output": "orderRecord"}",Verify order in DB
assertvalue,${orderRecord.customer_id},${testCustomer.id},,Verify customer ID matches

# Verify inventory was updated
dbquery,inventory,"SELECT quantity FROM inventory WHERE product_id = ?","{"provider": "inventory-db", "parameters": ["${availableProducts[0].product_id}"], "output": "updatedInventory"}",Check inventory update
assertvalue,${updatedInventory.quantity},${availableProducts[0].quantity - 2},,Verify inventory decreased

# Verify billing system was notified
rpcall,getCustomerOrders,"{"customerId": "${testCustomer.id}"}","{"provider": "billing-service", "output": "billingOrders"}",Get orders from billing
assertvalue,${billingOrders.length},1,,Verify billing has the order

# Verify notification was sent
apiget,/api/notifications/customer/${testCustomer.id},,"{"provider": "notification-api", "output": "notifications"}",Get customer notifications
assertvalue,${notifications[0].type},order_confirmation,,Verify notification type
assertvalue,${notifications[0].orderId},${orderId},,Verify notification order ID

# Cleanup test data
apidelete,/api/customers/${testCustomer.id},,"{"provider": "crm-api"}",Delete test customer
dbdelete,orders,"id = ?","{"provider": "order-db", "parameters": ["${orderId}"]}",Delete test order
rpcall,deleteAccount,"{"customerId": "${testCustomer.id}"}","{"provider": "billing-service"}",Delete billing account
```

### Example 5: Performance and Load Testing with Dynamic Data

```json
{
  "version": "1.0",
  "metadata": {
    "name": "Performance Test with Dynamic User Generation"
  },
  "providers": {
    "user-generator": {
      "type": "custom-rpc",
      "protocol": "http",
      "endpoint": "http://data-generator:8080",
      "serialization": "json"
    },
    "metrics-collector": {
      "type": "rest-api",
      "baseUrl": "http://metrics:9090"
    }
  },
  "variables": {
    "global": {
      "testDuration": 300000,
      "concurrentUsers": 50,
      "rampUpTime": 60000
    }
  },
  "root": {
    "type": "scenario",
    "children": [
      {
        "type": "data",
        "provider": "user-generator",
        "operation": "request",
        "request": {
          "method": "POST",
          "endpoint": "/generate/users",
          "body": {
            "count": "${concurrentUsers}",
            "profile": "realistic",
            "includePayment": true
          }
        },
        "output": "generatedUsers"
      },
      {
        "type": "data",
        "provider": "metrics-collector",
        "operation": "request",
        "request": {
          "method": "POST",
          "endpoint": "/test/start",
          "body": {
            "testId": "${SYSTEM.uuid}",
            "name": "User Journey Performance Test"
          }
        },
        "output": "testSession"
      },
      {
        "type": "parallel",
        "maxConcurrency": "${concurrentUsers}",
        "rampUp": "${rampUpTime}",
        "children": [
          {
            "type": "loop",
            "loopType": "forEach",
            "data": "${generatedUsers}",
            "variable": "user",
            "children": [
              {
                "type": "phase",
                "name": "User Journey: ${user.email}",
                "timing": {
                  "startTime": "now",
                  "maxDuration": "${testDuration}"
                },
                "children": [
                  {
                    "type": "data",
                    "provider": "metrics-collector",
                    "operation": "request",
                    "request": {
                      "method": "POST",
                      "endpoint": "/metrics/timer/start",
                      "body": {
                        "testId": "${testSession.id}",
                        "userId": "${user.id}",
                        "operation": "login"
                      }
                    },
                    "output": "loginTimer"
                  },
                  {
                    "type": "step",
                    "action": "navigate",
                    "target": "${baseUrl}/login"
                  },
                  {
                    "type": "step",
                    "action": "type",
                    "target": "#email",
                    "value": "${user.email}"
                  },
                  {
                    "type": "step",
                    "action": "type",
                    "target": "#password",
                    "value": "${user.password}"
                  },
                  {
                    "type": "step",
                    "action": "click",
                    "target": "#login-button"
                  },
                  {
                    "type": "step",
                    "action": "waitfor",
                    "target": ".dashboard",
                    "options": {"timeout": 10000}
                  },
                  {
                    "type": "data",
                    "provider": "metrics-collector",
                    "operation": "request",
                    "request": {
                      "method": "POST",
                      "endpoint": "/metrics/timer/end",
                      "body": {
                        "timerId": "${loginTimer.id}",
                        "success": true
                      }
                    }
                  },
                  {
                    "type": "loop",
                    "loopType": "duration",
                    "duration": "${testDuration}",
                    "children": [
                      {
                        "type": "data",
                        "provider": "user-generator",
                        "operation": "request",
                        "request": {
                          "method": "GET",
                          "endpoint": "/user/${user.id}/next-action"
                        },
                        "output": "nextAction"
                      },
                      {
                        "type": "branch",
                        "condition": "${nextAction.type}",
                        "branches": {
                          "browse": {
                            "condition": "${nextAction.type} === 'browse'",
                            "children": [
                              {
                                "type": "reference",
                                "source": "./actions/browse-products.csv",
                                "parameters": {
                                  "category": "${nextAction.category}",
                                  "userId": "${user.id}"
                                }
                              }
                            ]
                          },
                          "purchase": {
                            "condition": "${nextAction.type} === 'purchase'",
                            "children": [
                              {
                                "type": "reference",
                                "source": "./actions/complete-purchase.csv",
                                "parameters": {
                                  "productId": "${nextAction.productId}",
                                  "paymentMethod": "${user.paymentMethod}"
                                }
                              }
                            ]
                          },
                          "wait": {
                            "condition": "${nextAction.type} === 'wait'",
                            "children": [
                              {
                                "type": "step",
                                "action": "wait",
                                "target": "${nextAction.duration}"
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
        ]
      },
      {
        "type": "data",
        "provider": "metrics-collector",
        "operation": "request",
        "request": {
          "method": "POST",
          "endpoint": "/test/complete",
          "body": {
            "testId": "${testSession.id}"
          }
        },
        "output": "testResults"
      },
      {
        "type": "step",
        "action": "echo",
        "value": "Performance test completed. Results: ${testResults.summary}"
      }
    ]
  }
}
```

## Advanced Features

### Custom Data Providers

```typescript
// Custom provider implementation
class CustomDataProvider implements DataProvider {
  async initialize(config: CustomProviderConfig): Promise<void> {
    // Initialize custom connection
    this.connection = await createCustomConnection(config);
  }
  
  async get(query: DataQuery): Promise<DataResult> {
    // Implement custom data retrieval logic
    const result = await this.connection.executeQuery(query);
    return {
      data: result.data,
      metadata: result.metadata,
      success: true
    };
  }
  
  async set(mutation: DataMutation): Promise<DataResult> {
    // Implement custom data modification logic
    const result = await this.connection.executeMutation(mutation);
    return {
      data: result.data,
      success: true
    };
  }
}

// Register custom provider
dataProviderRegistry.register('custom-provider', CustomDataProvider);
```

### Data Validation and Schema Management

```json
{
  "type": "data",
  "provider": "api",
  "query": {
    "endpoint": "/api/users",
    "method": "GET"
  },
  "validation": {
    "schema": {
      "type": "object",
      "properties": {
        "data": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "email", "status"],
            "properties": {
              "id": {"type": "integer", "minimum": 1},
              "email": {"type": "string", "format": "email"},
              "status": {"type": "string", "enum": ["active", "inactive"]},
              "profile": {
                "type": "object",
                "properties": {
                  "firstName": {"type": "string", "minLength": 1},
                  "lastName": {"type": "string", "minLength": 1}
                }
              }
            }
          }
        },
        "meta": {
          "type": "object",
          "required": ["total", "page"],
          "properties": {
            "total": {"type": "integer", "minimum": 0},
            "page": {"type": "integer", "minimum": 1}
          }
        }
      }
    },
    "onValidationFailure": "fail-test",
    "customValidators": [
      {
        "name": "uniqueEmails",
        "function": "validateUniqueEmails"
      }
    ]
  }
}
```

### Data Mocking and Test Doubles

```json
{
  "type": "data",
  "provider": "mock-api",
  "operation": "mock",
  "mock": {
    "endpoint": "/api/users/${userId}",
    "method": "GET",
    "responses": [
      {
        "condition": "${userId} === '123'",
        "status": 200,
        "body": {
          "id": 123,
          "name": "John Doe",
          "email": "john@example.com"
        },
        "delay": 100
      },
      {
        "condition": "${userId} === '404'",
        "status": 404,
        "body": {
          "error": "User not found"
        }
      },
      {
        "default": true,
        "status": 200,
        "body": {
          "id": "${userId}",
          "name": "Generated User ${userId}",
          "email": "user${userId}@example.com"
        }
      }
    ]
  }
}
```

## Integration Guidelines

### Framework Integration

1. **Backward Compatibility**: All existing CSV actions remain functional
2. **Progressive Enhancement**: Data operations can be gradually introduced
3. **Performance Optimization**: Intelligent caching and connection pooling
4. **Error Resilience**: Comprehensive fallback and retry mechanisms
5. **Security First**: Built-in encryption and authentication support

### Best Practices

1. **Connection Management**: Use connection pooling for database providers
2. **Cache Strategy**: Implement intelligent caching based on data volatility
3. **Error Handling**: Always provide fallback mechanisms for critical data
4. **Security**: Never log sensitive data; use masking and encryption
5. **Performance**: Use parallel execution for independent data operations
6. **Monitoring**: Implement comprehensive logging and metrics collection

## Version History

- **v1.0** (2024-01-15): Initial specification for dynamic data integration

## Future Considerations

- **Machine Learning Integration**: AI-powered test data generation
- **Time Series Data**: Specialized support for time-based data analysis
- **Blockchain Integration**: Support for smart contract interactions
- **Event Sourcing**: Integration with event-driven architectures
- **Data Lineage**: Track data flow and dependencies across tests
- **Distributed Transactions**: Support for multi-system transactions
- **Real-time Analytics**: Live test execution analytics and insights
