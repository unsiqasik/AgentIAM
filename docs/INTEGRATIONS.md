# AgentIAM Integration Guide — LangChain

This guide shows how to integrate AgentIAM with [LangChain](https://python.langchain.com/) to add permission checks before your AI agent executes tools.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Python Integration](#python-integration)
  - [Install Dependencies](#install-dependencies)
  - [Create the Permission Checker](#create-the-permission-checker)
  - [Wrap LangChain Tools](#wrap-langchain-tools)
  - [Full Example](#full-example)
- [TypeScript/JavaScript Integration](#typescriptjavascript-integration)
  - [Install Dependencies](#install-dependencies-1)
  - [Create the Permission Checker](#create-the-permission-checker-1)
  - [Wrap LangChain Tools](#wrap-langchain-tools-1)
  - [Full Example](#full-example-1)
- [Policy Examples](#policy-examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

AgentIAM acts as an authorization layer between your AI agent and external tools. When integrated with LangChain, every tool call goes through AgentIAM's permission check before execution. If the action is denied, the tool raises an error instead of executing.

```
User → LangChain Agent → Tool Call → AgentIAM Check → Allow/Deny → Execute/Block
```

---

## Prerequisites

1. **AgentIAM running** — Follow the [Quick Start](../README.md#-quick-start) to set up the backend.
2. **An agent created** — Use the AgentIAM dashboard or API to create an agent and note its `agent_id`.
3. **A policy assigned** — Create a YAML policy for the agent (see [Policy Schema](POLICY_SCHEMA.md)).

---

## Python Integration

### Install Dependencies

```bash
pip install langchain langchain-openai httpx
```

### Create the Permission Checker

```python
import httpx
from langchain.tools import tool
from langchain_core.tools import BaseTool
from functools import wraps
from typing import Callable, Any

AGENTIAM_URL = "http://localhost:8000"  # Your AgentIAM backend URL


def check_permission(agent_id: int, resource: str, action: str) -> bool:
    """
    Check if an agent is allowed to perform an action on a resource.

    Args:
        agent_id: The ID of the agent requesting permission.
        resource: The resource being accessed (e.g., "github", "database").
        action: The action being performed (e.g., "read", "write", "delete").

    Returns:
        True if allowed, False if denied.

    Raises:
        PermissionDeniedError: If the action is not allowed.
    """
    response = httpx.post(
        f"{AGENTIAM_URL}/api/v1/audit/check-permission",
        json={
            "agent_id": agent_id,
            "resource": resource,
            "action": action,
        },
        timeout=10.0,
    )
    response.raise_for_status()
    result = response.json()

    if not result["allowed"]:
        raise PermissionDeniedError(
            f"Agent {agent_id} denied: {action} on {resource}. "
            f"Reason: {result['reason']}"
        )
    return True


class PermissionDeniedError(Exception):
    """Raised when an agent action is denied by AgentIAM."""
    pass
```

### Wrap LangChain Tools

Use the `check_permission` function to wrap any LangChain tool:

```python
def permissioned_tool(agent_id: int, resource: str, action: str):
    """
    Decorator that adds AgentIAM permission checks to a LangChain tool.

    Args:
        agent_id: The ID of the agent using the tool.
        resource: The resource the tool accesses.
        action: The action the tool performs.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            check_permission(agent_id, resource, action)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Full Example

```python
import httpx
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

# --- Configuration ---
AGENTIAM_URL = "http://localhost:8000"
AGENT_ID = 1  # Your agent's ID from AgentIAM

# --- Permission Check ---
def check_permission(agent_id: int, resource: str, action: str) -> bool:
    response = httpx.post(
        f"{AGENTIAM_URL}/api/v1/audit/check-permission",
        json={"agent_id": agent_id, "resource": resource, "action": action},
    )
    result = response.json()
    if not result["allowed"]:
        raise PermissionDeniedError(
            f"Denied: {action} on {resource} — {result['reason']}"
        )
    return True

class PermissionDeniedError(Exception):
    pass

# --- Permissioned Tools ---
@tool
def read_github_repo(repo_name: str) -> str:
    """Read a GitHub repository's metadata."""
    check_permission(AGENT_ID, "github", "read")
    # Your actual GitHub API call here
    return f"Repository: {repo_name}, Stars: 150, Language: Python"

@tool
def write_github_file(repo_name: str, file_path: str, content: str) -> str:
    """Write a file to a GitHub repository."""
    check_permission(AGENT_ID, "github", "write")
    # Your actual GitHub API call here
    return f"Written {file_path} to {repo_name}"

@tool
def query_database(sql: str) -> str:
    """Execute a read-only SQL query."""
    check_permission(AGENT_ID, "database", "read")
    # Your actual database query here
    return f"Query returned 42 rows"

# --- Agent Setup ---
llm = ChatOpenAI(model="gpt-4", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with access to GitHub and a database."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

tools = [read_github_repo, write_github_file, query_database]
agent = create_openai_functions_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Run ---
if __name__ == "__main__":
    try:
        result = executor.invoke({"input": "What repos do I have access to?"})
        print(result["output"])
    except PermissionDeniedError as e:
        print(f"Permission denied: {e}")
```

---

## TypeScript/JavaScript Integration

### Install Dependencies

```bash
npm install langchain @langchain/openai axios
```

### Create the Permission Checker

```typescript
import axios from "axios";

const AGENTIAM_URL = process.env.AGENTIAM_URL || "http://localhost:8000";

export class PermissionDeniedError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PermissionDeniedError";
  }
}

export async function checkPermission(
  agentId: number,
  resource: string,
  action: string
): Promise<boolean> {
  try {
    const response = await axios.post(
      `${AGENTIAM_URL}/api/v1/audit/check-permission`,
      { agent_id: agentId, resource, action },
      { timeout: 10000 }
    );

    if (!response.data.allowed) {
      throw new PermissionDeniedError(
        `Agent ${agentId} denied: ${action} on ${resource}. ` +
        `Reason: ${response.data.reason}`
      );
    }
    return true;
  } catch (error) {
    if (error instanceof PermissionDeniedError) throw error;
    if (axios.isAxiosError(error)) {
      throw new PermissionDeniedError(
        `AgentIAM check failed: ${error.message}. ` +
        `Ensure the backend is running at ${AGENTIAM_URL}.`
      );
    }
    throw error;
  }
}
```

### Wrap LangChain Tools

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const AGENT_ID = 1; // Your agent's ID from AgentIAM

export const readGithubRepo = tool(
  async ({ repoName }) => {
    await checkPermission(AGENT_ID, "github", "read");
    // Your actual GitHub API call here
    return `Repository: ${repoName}, Stars: 150, Language: TypeScript`;
  },
  {
    name: "read_github_repo",
    description: "Read a GitHub repository's metadata.",
    schema: z.object({
      repoName: z.string().describe("The repository name (owner/repo)"),
    }),
  }
);

export const writeGithubFile = tool(
  async ({ repoName, filePath, content }) => {
    await checkPermission(AGENT_ID, "github", "write");
    // Your actual GitHub API call here
    return `Written ${filePath} to ${repoName}`;
  },
  {
    name: "write_github_file",
    description: "Write a file to a GitHub repository.",
    schema: z.object({
      repoName: z.string(),
      filePath: z.string(),
      content: z.string(),
    }),
  }
);
```

### Full Example

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { AgentExecutor, createOpenAIFunctionsAgent } from "langchain/agents";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import { readGithubRepo, writeGithubFile } from "./tools";

async function main() {
  const llm = new ChatOpenAI({ modelName: "gpt-4", temperature: 0 });

  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "You are a helpful assistant with access to GitHub."],
    ["user", "{input}"],
    new MessagesPlaceholder("agent_scratchpad"),
  ]);

  const tools = [readGithubRepo, writeGithubFile];
  const agent = await createOpenAIFunctionsAgent({ llm, tools, prompt });
  const executor = new AgentExecutor({ agent, tools, verbose: true });

  try {
    const result = await executor.invoke({
      input: "What repos do I have access to?",
    });
    console.log(result.output);
  } catch (error) {
    if (error.name === "PermissionDeniedError") {
      console.error(`Permission denied: ${error.message}`);
    } else {
      throw error;
    }
  }
}

main();
```

---

## Policy Examples

### Read-Only GitHub Access

```yaml
permissions:
  github:
    read: true
    write: false
    delete: false
```

### Full Database Access

```yaml
permissions:
  database:
    read: true
    write: true
    delete: false
```

### Wildcard (All Actions on All Resources)

```yaml
permissions:
  "*": true
```

### Mixed Permissions

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
  payments:
    read: false
    write: false
    delete: false
```

---

## Troubleshooting

### Connection Refused

```
httpx.ConnectError: Connection refused
```

**Solution:** Ensure AgentIAM backend is running:
```bash
cd backend && uvicorn app.main:app --reload --port 8000
```

### Agent Not Found

```
{"detail":"Agent not found"}
```

**Solution:** Verify the `agent_id` exists in the AgentIAM dashboard or via API:
```bash
curl http://localhost:8000/api/v1/agents/
```

### Permission Always Denied

**Solution:** Check that the agent has a policy assigned. Create one via the dashboard or API:
```bash
curl -X POST http://localhost:8000/api/v1/policies/ \
  -H "Content-Type: application/json" \
  -d '{"agent_id": 1, "policy_yaml": "permissions:\n  \"*\": true"}'
```

### Timeout Errors

```
httpx.ReadTimeout
```

**Solution:** Increase the timeout in your HTTP client:
```python
response = httpx.post(
    f"{AGENTIAM_URL}/api/v1/audit/check-permission",
    json={...},
    timeout=10.0,  # seconds
)
```
