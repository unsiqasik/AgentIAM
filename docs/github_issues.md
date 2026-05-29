# GitHub Issues for AgentIAM

## Backend

1. **[Backend] Implement rate limiting for check_permission endpoint**
   - **Label**: enhancement, security, backend
   - **Description**: Add rate limiting to the authorization check endpoint to prevent brute-force probing of policies.

2. **[Backend] Support CIDR-based IP restrictions in policies**
   - **Label**: enhancement, security, backend
   - **Description**: Allow policies to specify allowed IP ranges for specific actions or agents.

3. **[Backend] Add support for temporary/expiring policies**
   - **Label**: enhancement, backend
   - **Description**: Policies should have an optional `expires_at` field to grant temporary permissions.

4. **[Backend] Implement policy versioning and history**
   - **Label**: enhancement, backend
   - **Description**: Keep track of policy changes to allow auditing and rollback of permission updates.

5. **[Backend] Optimize audit log database queries**
   - **Label**: enhancement, backend
   - **Description**: Add indexes to `agent_id` and `timestamp` fields in the `audit_logs` table for faster filtering.

6. **[Backend] Add structured logging across the service**
   - **Label**: enhancement, backend
   - **Description**: Replace standard print/log statements with structured JSON logging for better observability.

## Frontend

7. **[Frontend] Implement policy editor with YAML syntax highlighting**
   - **Label**: enhancement, frontend
   - **Description**: Use a library like Monaco or CodeMirror to provide a better editing experience for YAML policies.

8. **[Frontend] Add data visualization for audit logs**
   - **Label**: enhancement, frontend
   - **Description**: Create charts showing ALLOW vs DENY decisions over time on the dashboard.

9. **[Frontend] Implement search and filter for Audit Logs page**
   - **Label**: enhancement, frontend
   - **Description**: Allow users to filter audit logs by agent, resource, action, and decision.

10. **[Frontend] Add "Copy to Clipboard" for Agent IDs**
    - **Label**: enhancement, frontend, good first issue
    - **Description**: Add a small button next to Agent IDs in the list to quickly copy them.

11. **[Frontend] Implement dark mode toggle**
    - **Label**: enhancement, frontend
    - **Description**: Add a theme switcher to allow users to choose between light and dark modes.

## Security

12. **[Security] Implement password complexity requirements**
    - **Label**: security, backend
    - **Description**: Enforce minimum length and character variety for user passwords.

13. **[Security] Add Audit Log integrity checks**
    - **Label**: enhancement, security, backend
    - **Description**: Implement a mechanism (e.g., hashing/chaining) to detect tampering with audit records.

14. **[Security] Sanitize YAML input to prevent injection attacks**
    - **Label**: security, backend
    - **Description**: Ensure the YAML parser is configured securely to avoid arbitrary code execution or DOS via nested structures.

## Documentation

15. **[Docs] Create a "Quick Start" guide for LangChain integration**
    - **Label**: documentation
    - **Description**: Write a guide on how to use AgentIAM as a custom tool within a LangChain agent.

16. **[Docs] Document the YAML policy schema in detail**
    - **Label**: documentation
    - **Description**: Provide a comprehensive reference for all supported fields and logic in policies.

17. **[Docs] Add a FAQ section to the README**
    - **Label**: documentation, good first issue
    - **Description**: Answer common questions about setup, security, and use cases.

## Bug Fixes

18. **[Bug] Audit log timestamp precision issue**
    - **Label**: backend, bug
    - **Description**: Timestamps in the audit log are losing millisecond precision when retrieved via API.

19. **[Bug] Policy validation fails on empty resource list**
    - **Label**: backend, bug
    - **Description**: The API returns a 500 error instead of a validation error when a policy is submitted with no resources.

20. **[Bug] UI glitch on long agent names**
    - **Label**: frontend, bug
    - **Description**: Agent names that are very long overflow the card container in the Agents view.

## Integration & Future

21. **[Integration] Add Slack notification for DENIED critical actions**
    - **Label**: enhancement, backend
    - **Description**: Configure a webhook to notify a Slack channel when a high-risk action is denied.

22. **[Integration] Implement Prometheus metrics endpoint**
    - **Label**: enhancement, backend
    - **Description**: Export metrics such as total requests, error rates, and decision counts.

23. **[Future] Research OPA (Open Policy Agent) integration**
    - **Label**: enhancement, backend
    - **Description**: Evaluate if AgentIAM can delegate complex policy logic to OPA via Rego.

24. **[Feature] Add "Dry Run" mode for policies**
    - **Label**: enhancement, backend, frontend
    - **Description**: Allow testing a policy without actually enforcing it, logging what *would* have been the decision.

25. **[Feature] Support multi-factor authentication (MFA)**
    - **Label**: security, backend, frontend
    - **Description**: Add support for TOTP-based MFA for administrative accounts.
