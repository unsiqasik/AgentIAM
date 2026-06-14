# OPA Integration Research Report

## Executive Summary

This report evaluates the feasibility of integrating Open Policy Agent (OPA) with AgentIAM for policy-as-code authorization. The analysis covers technical architecture, performance implications, and a recommendation for v1.0.

## Table of Contents

1. [Current State](#current-state)
2. [OPA Overview](#opa-overview)
3. [Integration Architecture](#integration-architecture)
4. [Performance Analysis](#performance-analysis)
5. [Prototype Implementation](#prototype-implementation)
6. [Comparison: Current Engine vs OPA](#comparison)
7. [Recommendation](#recommendation)
8. [Next Steps](#next-steps)

## Current State

AgentIAM currently uses a custom YAML-based policy engine with the following characteristics:

### Strengths
- **Simple**: Easy to understand and write policies
- **Lightweight**: No external dependencies
- **Fast**: In-memory evaluation with minimal overhead
- **Integrated**: Part of the application codebase

### Limitations
- **Limited Expressiveness**: Basic resource-action-permission model
- **No Advanced Logic**: Cannot express complex conditions (time-based, attribute-based)
- **No Ecosystem**: No community tools, editors, or validators
- **Scalability**: May not scale to complex policy requirements

### Current Policy Format
```yaml
permissions:
  github:
    read: true
    write: false
    delete: false
  database:
    query: true
    insert: false
```

## OPA Overview

Open Policy Agent (OPA) is an open-source, general-purpose policy engine that enables unified, context-aware policy enforcement across the stack.

### Key Features
- **Rego Language**: Purpose-built policy language for expressing complex rules
- **Decoupled**: Runs as a sidecar, service, or library
- **Standardized**: CNCF graduated project with wide adoption
- **Rich Ecosystem**: Tools for testing, linting, visualization

### Rego Language Example
```rego
package agentiam

default allow = false

allow {
    input.resource == "github"
    input.action == "read"
    agent_has_permission(input.agent_id, "github", "read")
}

agent_has_permission(agent_id, resource, action) {
    policy := data.policies[agent_id]
    policy.permissions[resource][action] == true
}

# Time-based access
allow {
    input.resource == "database"
    time.now_ns() < data.policies[input.agent_id].expires_at
}
```

## Integration Architecture

### Option 1: OPA Sidecar (Recommended)
```
┌─────────────────┐     ┌─────────────────┐
│   AgentIAM      │     │   OPA Sidecar   │
│   Application   │────▶│   (localhost)   │
│                 │     │   Port 8181     │
└─────────────────┘     └─────────────────┘
        │                        │
        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐
│   PostgreSQL    │     │   Policy Store  │
│   (Policies)    │     │   (Bundle)      │
└─────────────────┘     └─────────────────┘
```

**Pros:**
- Decoupled from application
- Independent scaling
- Easy to update policies without redeployment
- Standard HTTP API

**Cons:**
- Additional infrastructure
- Network latency (~1-5ms)
- Requires bundle management

### Option 2: OPA Library (Embedded)
```
┌─────────────────────────────────┐
│   AgentIAM Application          │
│   ┌─────────────────────────┐   │
│   │   OPA Go Library        │   │
│   │   (Embedded)            │   │
│   └─────────────────────────┘   │
└─────────────────────────────────┘
```

**Pros:**
- No network overhead
- Simpler deployment
- Direct memory access

**Cons:**
- Requires Go integration (Python binding exists)
- Tighter coupling
- Harder to update independently

### Option 3: Hybrid Approach
```
┌─────────────────┐     ┌─────────────────┐
│   AgentIAM      │     │   OPA Service   │
│   (Simple       │────▶│   (Complex      │
│    Policies)    │     │    Policies)    │
└─────────────────┘     └─────────────────┘
```

**Pros:**
- Best of both worlds
- Gradual migration path
- Performance for simple cases

**Cons:**
- More complex architecture
- Policy distribution challenges

## Performance Analysis

### Benchmark Results (Hypothetical)

| Metric | Current Engine | OPA Sidecar | OPA Library |
|--------|----------------|-------------|-------------|
| Latency (p50) | 0.1ms | 2ms | 0.3ms |
| Latency (p99) | 0.5ms | 10ms | 1ms |
| Throughput | 100K req/s | 50K req/s | 80K req/s |
| Memory | 10MB | 50MB | 30MB |
| Startup Time | 1s | 5s | 2s |

### Performance Considerations
- **Network Overhead**: OPA sidecar adds ~1-5ms per decision
- **Caching**: OPA supports decision caching (recommended)
- **Batching**: OPA supports batch evaluations for bulk operations
- **Local Evaluation**: OPA can evaluate locally with data bundles

### Optimization Strategies
1. **Decision Caching**: Cache frequent decisions (TTL-based)
2. **Batch Evaluation**: Group multiple decisions into single call
3. **Local Data**: Push policy data to OPA (avoid DB queries)
4. **Connection Pooling**: Reuse HTTP connections to OPA

## Prototype Implementation

### Step 1: Install OPA
```bash
# Linux
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
sudo mv opa /usr/local/bin/opa

# macOS
brew install opa
```

### Step 2: Create Policy File
```rego
# policy.rego
package agentiam

import future.keywords.if
import future.keywords.in

default allow = false

# Simple resource-action permissions
allow if {
    input.resource in data.policies[input.agent_id].resources
    input.action in data.policies[input.agent_id].resources[input.resource]
}

# Wildcard permissions
allow if {
    data.policies[input.agent_id].resources["*"] == true
}

# Time-based access
allow if {
    input.resource in data.policies[input.agent_id].resources
    time.now_ns() < data.policies[input.agent_id].expires_at
}
```

### Step 3: Create Data File
```json
{
    "policies": {
        "agent1": {
            "resources": {
                "github": ["read", "write"],
                "database": ["query"]
            },
            "expires_at": 1735689600000000000
        },
        "agent2": {
            "resources": {
                "*": true
            }
        }
    }
}
```

### Step 4: Test OPA
```bash
# Start OPA server
opa run --server policy.rego

# Test decision
curl -X POST http://localhost:8181/v1/data/agentiam/allow \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
        "agent_id": "agent1",
        "resource": "github",
        "action": "read"
    }
  }'
```

### Step 5: Python Integration
```python
import requests

class OPAClient:
    def __init__(self, base_url="http://localhost:8181"):
        self.base_url = base_url
    
    def check_permission(self, agent_id: str, resource: str, action: str) -> bool:
        response = requests.post(
            f"{self.base_url}/v1/data/agentiam/allow",
            json={
                "input": {
                    "agent_id": agent_id,
                    "resource": resource,
                    "action": action
                }
            }
        )
        return response.json().get("result", False)
```

## Comparison: Current Engine vs OPA

### Feature Comparison

| Feature | Current Engine | OPA |
|---------|----------------|-----|
| **Policy Language** | YAML | Rego |
| **Expressiveness** | Low | High |
| **Complexity** | Simple | Moderate |
| **Performance** | Excellent | Good |
| **Ecosystem** | None | Rich |
| **Learning Curve** | Low | Medium |
| **Community** | Internal | CNCF |
| **Tooling** | Basic | Comprehensive |
| **Testing** | Manual | Built-in |
| **Visualization** | None | Available |
| **Versioning** | Manual | Built-in |
| **Distribution** | Database | Bundles |
| **Caching** | None | Built-in |
| **Auditing** | Basic | Comprehensive |

### Use Case Comparison

| Use Case | Current Engine | OPA |
|----------|----------------|-----|
| Simple CRUD permissions | ✅ Excellent | ✅ Good |
| Time-based access | ❌ Not supported | ✅ Excellent |
| Attribute-based access | ❌ Not supported | ✅ Excellent |
| Complex business rules | ❌ Limited | ✅ Excellent |
| Multi-tenant policies | ❌ Manual | ✅ Built-in |
| Policy testing | ❌ Manual | ✅ Built-in |
| Policy visualization | ❌ None | ✅ Available |
| Policy migration | ❌ Manual | ✅ Tools available |

## Recommendation

### Short-term (v0.4-v0.5)
**Recommendation: Continue with Current Engine**

**Rationale:**
1. **Simplicity**: Current engine meets v0.4 requirements
2. **Performance**: No overhead for simple policies
3. **Team Expertise**: Team familiar with YAML
4. **Time Constraints**: OPA integration requires significant effort

**Action Items:**
- Document current engine limitations
- Design policy format for future OPA migration
- Add comprehensive tests for current engine

### Medium-term (v0.6-v0.8)
**Recommendation: Implement Hybrid Approach**

**Rationale:**
1. **Gradual Migration**: Move complex policies to OPA
2. **Performance**: Keep simple policies in current engine
3. **Risk Mitigation**: Test OPA in production gradually

**Action Items:**
- Implement OPA sidecar for complex policies
- Create migration tools for YAML → Rego
- Add policy testing framework

### Long-term (v1.0+)
**Recommendation: Full OPA Integration**

**Rationale:**
1. **Industry Standard**: OPA is CNCF graduated
2. **Ecosystem**: Rich tooling and community
3. **Scalability**: Better for complex requirements
4. **Future-proof**: Aligned with industry trends

**Action Items:**
- Complete migration to OPA
- Deprecate current engine
- Implement advanced OPA features

## Next Steps

### Immediate Actions
1. **Document Current Limitations**: Create comprehensive list
2. **Design Migration Path**: Plan YAML → Rego conversion
3. **Create Proof of Concept**: Test OPA with sample policies
4. **Performance Benchmark**: Compare current vs OPA

### Research Tasks
1. **OPA Go Library**: Evaluate Python bindings
2. **Bundle Management**: Investigate policy distribution
3. **Caching Strategy**: Design decision caching
4. **Monitoring**: Plan OPA observability

### Team Preparation
1. **Training**: Rego language workshops
2. **Documentation**: OPA integration guides
3. **Tooling**: Policy editors and validators
4. **Testing**: Policy test frameworks

## Appendix

### A. OPA Resources
- [OPA Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Rego Language](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [OPA Playground](https://play.openpolicyagent.org/)
- [OPA GitHub](https://github.com/open-policy-agent/opa)

### B. Rego Examples

#### Simple Permission Check
```rego
package agentiam

default allow = false

allow {
    input.resource == "github"
    input.action == "read"
}
```

#### Time-based Access
```rego
package agentiam

default allow = false

allow {
    input.resource == "database"
    time.now_ns() < data.policies[input.agent_id].expires_at
}
```

#### Attribute-based Access
```rego
package agentiam

default allow = false

allow {
    input.resource == "admin"
    data.users[input.user_id].role == "admin"
    time.now_ns() < data.users[input.user_id].session_expires_at
}
```

### C. Migration Example

#### YAML Policy
```yaml
permissions:
  github:
    read: true
    write: false
  database:
    query: true
```

#### Equivalent Rego
```rego
package agentiam

default allow = false

allow {
    input.resource == "github"
    input.action == "read"
}

allow {
    input.resource == "database"
    input.action == "query"
}
```

---

**Report Author:** ZKA Agent  
**Date:** 2026-06-01  
**Version:** 1.0  
**Status:** Draft
