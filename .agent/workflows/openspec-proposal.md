---
description: Create a new OpenSpec change proposal
---

# OpenSpec Proposal Workflow

This workflow guides you through creating a new OpenSpec change proposal.

## Steps

1. **Review existing context**
   ```bash
   openspec list
   openspec spec list --long
   ```

2. **Choose a unique change ID**
   - Use kebab-case
   - Start with a verb: `add-`, `update-`, `remove-`, `refactor-`
   - Example: `add-user-notifications`, `update-auth-flow`

3. **Create the proposal directory**
   ```bash
   mkdir -p openspec/changes/[change-id]
   ```

4. **Create proposal.md**
   - Describe WHY the change is needed
   - List WHAT will change
   - Identify the IMPACT (affected specs, code, systems)

5. **Create tasks.md**
   - Break down implementation into concrete steps
   - Use checkboxes: `- [ ] Task description`

6. **Create spec deltas** (if needed)
   - Create `openspec/changes/[change-id]/specs/[capability]/spec.md`
   - Use sections: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`
   - Each requirement MUST have at least one `#### Scenario:`

7. **Create design.md** (optional, only if needed)
   - Add if: cross-cutting changes, new dependencies, security/performance concerns
   - Include: Context, Goals/Non-Goals, Decisions, Risks, Migration Plan

8. **Validate the proposal**
   ```bash
   openspec validate [change-id] --strict
   ```

9. **Request review**
   - Share the proposal with stakeholders
   - Get approval before implementation

## Example Change ID

- `add-pdf-export`
- `update-lambda-timeout`
- `refactor-auth-service`
- `remove-legacy-api`
