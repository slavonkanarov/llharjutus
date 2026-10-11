# Repository instructions

This repository is for a language-learning exercise platform. English is the language of code, documentation, schemas, API names, and comments. The initial learning language is Estonian, but content models must support other languages without schema changes.

## Product documents

- `docs/BLOCK_CATALOG.md` defines the learner-facing block catalog and its priority levels.
- `docs/IMPLEMENTATION_PLAN.md` defines the service boundaries, data contracts, security invariants, and delivery sequence.
- Update these documents when a product decision changes. Keep examples and implementation consistent with them.

## Architecture boundaries

- Keep three application services: frontend, backend, and AI service. MongoDB is the primary database. Use S3-compatible object storage (MinIO in development) for media and generated files.
- The frontend talks to the backend. The backend owns authorization, lesson publication, attempts, grading decisions, progress, and all persistent data. The AI service is called by the backend through an internal interface; it does not publish lessons or grade attempts by itself.
- Keep public learner content separate from private answer keys and grading rubrics. Prefer separate MongoDB collections and explicit public DTOs. Never serialize an answer key, correctness flag, hidden mapping, rubric, or AI grading prompt into an initial learner-facing exercise response.
- An exercise logically includes its answer specification, even when the answer specification is stored separately and referenced by ID. Every objectively graded item or blank must have its own accepted answer variants and normalization rules.
- Use deterministic grading first. Invoke AI review only when the exercise policy allows it and deterministic grading cannot accept an answer. A model result must be validated by the backend; ambiguous results become `needs_review`, not an invented correct/incorrect verdict.
- Learner-visible exercise metadata must say when equivalent answers or AI review are permitted. Reveal a correct answer after submission only when the exercise's explicit feedback policy allows it.
- Generated exercises stay in draft until schema validation and author review or an explicit trusted publishing policy have passed. Store generation provenance and versions.

## Implementation practices

- Define versioned, typed contracts for blocks, attempts, grading results, and AI jobs before implementing renderers or prompts. Use an extensible discriminator such as `blockType` or `activityType` rather than a separate lesson model for each exercise format.
- Validate data at service boundaries and define a safe behavior for unsupported block versions. Keep storage models separate from API response models.
- Scope all reads and writes to the authenticated learner or author. Protect internal AI endpoints and MinIO objects; use short-lived access when media must be downloaded directly.
- Add tests for answer-key non-disclosure, per-item variants, grading rules, authorization, and any new exercise type with nontrivial answer logic. Avoid tests that only repeat a renderer's implementation.
- Preserve Estonian-specific teaching content as data and examples. Do not hard-code Estonian grammar into shared grading or rendering logic.
