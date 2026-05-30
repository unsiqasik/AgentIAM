# YAML Policy Schema Reference

This document provides a comprehensive reference for the AgentIAM YAML policy schema. Policies define what actions an AI agent is allowed (or denied) to perform on specific resources.

## Table of Contents

- [Overview](#overview)
- [Schema Structure](#schema-structure)
- [Top-Level Fields](#top-level-fields)
- [Permissions](#permissions)
  - [Resource Definitions](#resource-definitions)
  - [Action Definitions](#action-definitions)
  - [Wildcard Support](#wildcard-support)
- [Evaluation Logic](#evaluation-logic)
- [Complete Examples](#complete-examples)
- [Validation Rules](#validation-rules)
- [API Usage](#api-usage)

---

## Overview

AgentIAM uses YAML-based policies to control what an AI agent can do. Each policy is attached to exactly one agent and is evaluated by the authorization service (`authz_service`) before any action is executed.

A policy is a YAML document stored as a string in the `policy_yaml` field. When an agent attempts to perform an action, the policy engine loads the YAML, evaluates the permissions, and returns an **allow** or **deny** decision along with a human-readable reason.

### Design Principles

- **Default deny** — if a resource or action is not explicitly granted, it is denied.
- **Explicit deny wins** — an explicit `false` on a specific action takes precedence over a wildcard `true`.
- **One policy per agent** — each agent has exactly one policy document.

---

## Schema Structure

```yaml
permissions:
  <resource>:
    <action>: <boolean>
  <resource>: <boolean>
```

The top-level (and only required) key is `permissions`. Under it, you define resources and the actions allowed on those resources.

---

## Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `permissions` | object | **Yes** | Map of resource names to their permission definitions. Must contain at least one entry. |

### Example (minimal)

```yaml
permissions:
  github:
    read: true
```

---

## Permissions

The `permissions` field is a dictionary where:

- **Keys** are resource names (strings).
- **Values** are either a boolean or a dictionary of actions.

### Resource Definitions

Each resource is identified by a string name. Resource names should be descriptive identifiers for the tools, APIs, or services the agent interacts with.

**Common resource naming conventions:**

| Resource Name | Represents |
|---------------|------------|
| `github` | GitHub API access |
| `database` | Database operations |
| `filesystem` | File system access |
| `payment_api` | Payment processing |
| `admin_panel` | Administrative interface |
| `s3` | Cloud storage |
| `*` | Wildcard — matches **all** resources |

#### Boolean shorthand

Setting a resource to `true` grants **full access** (all actions) on that resource:

```yaml
permissions:
  github: true   # Agent can do anything with GitHub
```

Setting a resource to `false` is technically valid YAML but has no effect — the default is already deny.

#### Fine-grained control

Use a dictionary to specify individual actions:

```yaml
permissions:
  github:
    read: true
    write: true
    delete: false
```

### Action Definitions

Under each resource (when using the dictionary form), actions are defined as string keys mapped to boolean values:

| Value | Meaning |
|-------|---------|
| `true` | The action is **allowed**. |
| `false` | The action is **explicitly denied**. |

#### Valid action names

Action names are free-form strings. Use names that match your tooling or API operations. Common conventions:

| Action | Typical Meaning |
|--------|-----------------|
| `read` | Read-only access (GET, SELECT) |
| `write` | Create or update (POST, PUT, PATCH) |
| `delete` | Remove resources (DELETE) |
| `execute` | Run commands or functions |
| `admin` | Administrative operations |
| `*` | Wildcard — matches **all** actions on this resource |

### Wildcard Support

AgentIAM supports wildcards at two levels:

#### 1. Resource-level wildcard (`"*"`)

Grants permissions across **all** resources:

```yaml
permissions:
  "*": true   # Full access to everything
```

This is the broadest possible policy and should be used with extreme caution.

#### 2. Action-level wildcard (`"*"` within a resource)

Grants all actions on a specific resource:

```yaml
permissions:
  github:
    "*": true   # All actions on GitHub are allowed
```

#### Combining wildcards with explicit rules

You can use a wildcard as a default and then override specific actions:

```yaml
permissions:
  github:
    "*": true       # Allow everything by default
    delete: false   # But explicitly deny delete
```

**Rule:** Explicit action entries always take precedence over the wildcard. In the example above, `delete` is denied even though `"*"` is `true`.

---

## Evaluation Logic

When the authorization service evaluates a permission check, it follows this logic:

```
1. Load the agent's policy YAML.
2. Extract the `permissions` dict.
3. Check for resource-level wildcard:
   a. If permissions["*"] is True → ALLOW (with reason "Wildcard resource permission granted")
4. Check if the exact resource exists in permissions:
   a. If the resource value is True → ALLOW (with reason "Full access granted to resource: {resource}")
   b. If the resource value is a dict:
      i.   Check for exact action match:
           - If action is True → ALLOW
           - If action is False → DENY (explicit deny takes precedence)
      ii.  Check for action-level wildcard:
           - If "*" is True → ALLOW (with reason "Wildcard action permission granted")
      iii. Otherwise → DENY (no matching permission)
5. If resource not found → DENY (with reason "Permission not granted")
6. If no policy exists → DENY (with reason "No policy found for this agent")
```

### Decision Priority

| Priority | Condition | Result |
|----------|-----------|--------|
| 1 (highest) | Explicit action set to `false` | **DENY** |
| 2 | Explicit action set to `true` | **ALLOW** |
| 3 | Action-level wildcard `"*": true` | **ALLOW** |
| 4 | Resource set to `true` (boolean) | **ALLOW** |
| 5 | Resource-level wildcard `"*": true` | **ALLOW** |
| 6 (lowest) | No matching rule found | **DENY** |

Every decision — whether allowed or denied — is recorded in the audit log with the agent ID, resource, action, decision, and human-readable reason.

---

## Complete Examples

### Example 1: Read-only GitHub access

```yaml
permissions:
  github:
    read: true
    write: false
    delete: false
```

**Result:** Agent can read GitHub resources but cannot write or delete.

### Example 2: Full access to one resource, limited access to another

```yaml
permissions:
  github: true
  database:
    read: true
    write: false
    delete: false
```

**Result:** Agent has full GitHub access but can only read from the database.

### Example 3: Wildcard with explicit deny

```yaml
permissions:
  github:
    "*": true
    delete: false
    admin: false
```

**Result:** Agent can perform any GitHub action except `delete` and `admin`.

### Example 4: Multiple resources with fine-grained control

```yaml
permissions:
  github:
    read: true
    write: true
    delete: false
  database:
    read: true
    write: false
    delete: false
    execute: false
  payment_api:
    read: true
    write: true
    delete: false
  filesystem:
    read: true
    write: true
    delete: true
    execute: false
```

**Result:** Agent can read/write GitHub, read-only database access, read/write payments, and full filesystem access (except execute).

### Example 5: Super-admin agent (full wildcard)

```yaml
permissions:
  "*": true
```

**Result:** Agent has unrestricted access to all resources and all actions. Use only for trusted system-level agents.

### Example 6: Minimal read-only agent

```yaml
permissions:
  github:
    read: true
  database:
    read: true
```

**Result:** Agent can read from GitHub and the database but nothing else.

### Example 7: CI/CD pipeline agent

```yaml
permissions:
  github:
    read: true
    write: true
    delete: false
  filesystem:
    read: true
    write: true
    delete: false
    execute: true
  docker:
    read: true
    write: true
    execute: true
```

**Result:** Agent can read/write GitHub and filesystem, execute builds, and manage Docker containers — but cannot delete anything.

### Example 8: Monitoring agent (read-only everything)

```yaml
permissions:
  github:
    read: true
  database:
    read: true
  metrics:
    read: true
  logs:
    read: true
```

**Result:** Read-only access across monitoring and data resources.

---

## Validation Rules

The policy service validates YAML before storing it. The following rules apply:

| Rule | Error Message |
|------|---------------|
| Policy must be valid YAML | `Invalid YAML format: {details}` |
| Top-level value must be a dict | `Policy must be a YAML object` |
| Must contain `permissions` key | `Policy must contain 'permissions' key` |
| `permissions` must be a dict | `'permissions' must be a YAML object` |
| `permissions` must not be empty | `Policy must contain at least one resource in 'permissions'` |
| Resource names must be strings | `Resource name must be a string: {name}` |
| Resource permissions must be `bool` or `dict` | `Permissions for resource '{name}' must be a boolean or an object` |
| Action dict must not be empty | `Action list for resource '{name}' cannot be empty` |
| Action names must be strings | `Action name must be a string: {name} in resource '{resource}'` |
| Action values must be booleans | `Permission for action '{name}' in resource '{resource}' must be a boolean` |

### Common Validation Errors

**Empty permissions:**
```yaml
permissions: {}
# ERROR: Policy must contain at least one resource in 'permissions'
```

**Invalid action value (string instead of boolean):**
```yaml
permissions:
  github:
    read: "yes"   # ERROR: must be true/false, not a string
```

**Missing permissions key:**
```yaml
rules:
  - resource: github
    action: read
# ERROR: Policy must contain 'permissions' key
```

**Empty action list:**
```yaml
permissions:
  github: {}
# ERROR: Action list for resource 'github' cannot be empty
```

---

## API Usage

### Create a Policy

```bash
curl -X POST http://localhost:8000/api/v1/policies/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1,
    "policy_yaml": "permissions:\n  github:\n    read: true\n    write: true\n    delete: false"
  }'
```

### Get a Policy by Agent ID

```bash
curl http://localhost:8000/api/v1/policies/agent/1 \
  -H "Authorization: Bearer <token>"
```

### Update a Policy

```bash
curl -X PUT http://localhost:8000/api/v1/policies/1 \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_yaml": "permissions:\n  github:\n    read: true\n    write: false\n    delete: false"
  }'
```

### Delete a Policy

```bash
curl -X DELETE http://localhost:8000/api/v1/policies/1 \
  -H "Authorization: Bearer <admin_token>"
```

---

## Tips and Best Practices

1. **Start restrictive, expand as needed.** Begin with read-only permissions and add write/delete only when the agent demonstrably needs them.

2. **Use explicit deny for dangerous actions.** Even if you grant a wildcard, explicitly deny destructive operations like `delete` or `admin`.

3. **Name resources consistently.** Use lowercase, underscore-separated names that match your tool identifiers (e.g., `payment_api`, `github`, `database`).

4. **Audit regularly.** Check the audit log to see what actions your agents are actually performing and adjust policies accordingly.

5. **One agent, one policy.** Each agent can only have one policy. If you need different permission sets, create separate agents.

6. **Test policies before deploying.** Use the `/api/v1/audit/` endpoint to review authorization decisions and catch over-permissive policies.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-05-30 | Initial schema documentation created. |
