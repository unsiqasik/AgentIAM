# AgentIAM OPA Policy
# This policy demonstrates how AgentIAM could use OPA for authorization

package agentiam

import future.keywords.if
import future.keywords.in

# Default deny
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

# Time-based access (if expires_at is set)
allow if {
    input.resource in data.policies[input.agent_id].resources
    data.policies[input.agent_id].expires_at
    time.now_ns() < data.policies[input.agent_id].expires_at
}

# Role-based access (example)
allow if {
    input.resource == "admin"
    data.users[input.user_id].role == "admin"
}

# Get all permissions for an agent
permissions[resource] {
    resource := data.policies[input.agent_id].resources[_]
}

# Check if agent has any permission
has_permissions if {
    count(data.policies[input.agent_id].resources) > 0
}
