/speckit.constitution

Create the project constitution for a Spec-Driven Development workflow using Codex and GitHub Spec Kit.

The constitution must be written entirely in English.

This constitution defines the non-negotiable engineering principles for this repository. It must guide all future specs, plans, tasks, implementations, Pull Requests, and AI-agent behavior.

The repository will use:

- Codex as the main AI coding agent.
- GitHub Spec Kit as the Spec-Driven Development framework.
- Jira as the source for product issues and business intent.
- Figma as the source for UX, layout, visual states, and interaction intent.
- OpenAPI, or an explicitly approved versioned architecture contract, as the source of truth for API contracts.
- AGENTS.md as the repository-level operating instructions for agents and contributors.
- Bitbucket repository with documentation in OKF: https://git.uxxi.net/projects/KNOW/repos/conocimiento/browse

Define principles for:

1. Specification-first development.
2. Human ownership of AI-generated code.
3. Jira traceability.
4. Spec folder and branch naming convention.
5. API contract authority.
6. Figma as UX intent.
7. Testable acceptance criteria.
8. Incremental implementation.
9. Security and privacy.
10. Language policy.
11. Architecture governance.
12. Required Spec Kit workflow.
13. Quality gates.
14. Amendment process.

Mandatory rules:

- Product-facing development must not start without `spec.md`, `plan.md`, and `tasks.md`.
- AI agents must not invent requirements, fields, endpoints, permissions, business rules, or acceptance criteria.
- Every product-facing feature must be linked to a Jira issue.
- Every Spec Kit feature must include the Jira issue key in the branch name and spec folder name.
- Use `feature/JIRAKEY-short-description` for the Git branch.
- Use `NNN-JIRAKEY-short-description` for the spec folder.
- Example: branch `feature/SGA-1234-enrollment-requests` and folder `specs/001-SGA-1234-enrollment-requests/`.
- OpenAPI is the preferred source of truth for endpoints, DTOs, response structures, error models, and pagination models.
- When OpenAPI is unavailable or explicitly deferred, a versioned architecture contract may become authoritative only through an approved feature clarification.
- If Figma or Jira requires data that is not present in the approved API contract authority, document the gap and request clarification.
- Figma provides UX and interaction intent, but it does not override API contracts or architecture standards.
- Required UI states must be considered when applicable: loading, empty, error, and success.
- Each acceptance criterion must be covered by an automated test or an explicit validation step.
- `/speckit.analyze` must be run before `/speckit.implement` for product-facing features.
- Do not implement requirements that are not present in `spec.md`.
- Do not add technical decisions that are not justified in `plan.md`.
- Do not execute tasks outside the scope of `tasks.md`.
- Do not introduce new libraries, architectural patterns, or cross-cutting changes without documenting the decision in `plan.md`.
- Human review is mandatory before merge.

Language rules:

- Persistent agent-facing instructions must be written in English.
- This applies to `AGENTS.md`, `.specify/memory/constitution.md`, repository-level agent instructions, reusable prompts, and workflow instructions consumed by coding agents.
- Team-facing delivery artifacts may be written in Spanish.
- This applies to Jira issues, Jira comments, `spec.md`, `plan.md`, `tasks.md`, Pull Request descriptions, functional documentation, and technical documentation intended for human review.
- Technical identifiers must remain in English.
- Do not translate API paths, DTOs, class names, component names, hooks, function names, commands, file paths, library names, or framework names.

Required Spec Kit workflow:

1. `/speckit.specify`
2. `/speckit.clarify` when Jira, Figma, the API contract authority, acceptance criteria, or source code are ambiguous
3. `/speckit.plan`
4. `/speckit.tasks`
5. `/speckit.analyze`
6. `/speckit.implement`

Do not include feature-specific details.
Do not include implementation details that belong in `plan.md`.
Do not duplicate the entire `AGENTS.md`; define stable governing principles.
Keep the constitution concise, enforceable, and suitable for long-term use.
