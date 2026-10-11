# Implementation plan

## Product goal and scope

Build a service that turns a learner request such as “I want to practice Estonian partitive forms” into a lesson or practice set. The first release supports Estonian content, while the data model uses language tags so additional languages can be added later. An author can create and review lessons; a learner can complete exercises and receive feedback. AI generation and AI-assisted grading are controlled by the backend.

The block inventory and priorities are in [`BLOCK_CATALOG.md`](BLOCK_CATALOG.md). The MVP uses a focused subset of blocks; the catalog is the backlog for expanding lesson formats.

## Service and data boundaries

| Component | Responsibilities |
| --- | --- |
| Frontend | Authoring and learner interfaces; rendering versioned blocks; collecting responses; showing hints, grades, and progress. Calls the backend only. |
| Backend | Authentication and roles; public lesson DTOs; publishing; answer keys; attempts; deterministic grading; final AI grading decisions; progress; orchestration of AI jobs and media access. |
| AI service | Generate draft lesson/block data from a learning goal; propose hints and explanations; review allowed nonmatching or open-ended answers against a supplied rubric. Returns structured suggestions to the backend. |
| MongoDB | Lessons, block content, private answer keys, attempts, progress, generation jobs, and audit/version metadata. |
| MinIO/S3 | Images, audio, video, and generated files. MongoDB stores object references and metadata. |

The browser must never connect to MongoDB or the AI service. Media may be downloaded through the backend or a short-lived signed URL issued by the backend. Internal service credentials and object-storage secrets stay on the server.

## Core domain and contract decisions

- `Lesson`: owner, language tag, title, goal, skill tags, level, ordered block references, version, and `draft`/`published` state.
- `Block`: stable ID, schema version, `blockType`, public presentation data, and optional private content references. Interactive blocks use an `activityType`, item IDs, and an `answerKeyId` in the backend storage model.
- `AnswerKey`: one private record per interactive block or exercise version; answer specifications per item/blank, accepted variants, normalization policy, correct mappings/sequences, optional rubric, AI review policy, and feedback/reveal policy. It is never returned by learner read endpoints.
- `Attempt`: learner ID, lesson/exercise/version IDs, submitted item responses, grading decisions, timestamps, and retry count. An attempt keeps the exercise version used when submitted.
- `GenerationJob`: learner or author goal, language tag, constraints, status, generated draft references, validation errors, model/provenance metadata, and timestamps.
- `Asset`: owner, object key, media type, alt text/caption/transcript metadata, and access policy.

Use versioned, typed DTOs. Construct learner responses with an explicit allowlist; do not serialize MongoDB documents directly. Separate storage, author-preview, and learner DTOs. An author may inspect answer keys through a dedicated authorized endpoint; learner endpoints cannot.

### Example: multi-blank exercise

Public learner DTO (the actual exercise response):

```json
{
  "id": "exercise-42",
  "schemaVersion": 1,
  "blockType": "exercise",
  "activityType": "fill_blanks",
  "prompt": "Complete each blank with an appropriate form.",
  "items": [
    { "id": "blank-a", "before": "I see ", "after": "." },
    { "id": "blank-b", "before": "This is ", "after": "." }
  ],
  "gradingDisclosure": {
    "equivalentAnswersMayBeAccepted": true,
    "aiReviewPossible": true
  }
}
```

Private `AnswerKey` record, loaded by the backend during grading:

```json
{
  "exerciseId": "exercise-42",
  "exerciseVersion": 1,
  "items": {
    "blank-a": {
      "acceptedAnswers": ["a house", "one house"],
      "normalization": { "trim": true, "caseFold": true, "punctuation": "strict" },
      "aiReviewOnMismatch": true
    },
    "blank-b": {
      "acceptedAnswers": ["my house"],
      "normalization": { "trim": true, "caseFold": true, "punctuation": "strict" },
      "aiReviewOnMismatch": false
    }
  },
  "feedbackPolicy": { "revealAnswer": "after_final_attempt", "maxAttempts": 2 }
}
```

The example strings only demonstrate the contract. Content and answer variants are authored or generated for a specific target language and prompt. Every exercise type must define its response shape and private answer specification.

## Grading flow

1. The learner submits responses to the backend with exercise ID/version and an idempotency key. The backend authenticates the learner and checks the lesson, version, attempt limits, response shape, and ownership.
2. The backend loads the private answer key and evaluates each item with its own accepted variants, mapping, or sequence. Apply only the normalization rules specified for that item.
3. For a mismatch, call the AI service only when `aiReviewOnMismatch` or a rubric-based policy allows it. Send the prompt, learner response, relevant private answer data, rubric, and language tag over an authenticated internal channel. Validate the structured AI result.
4. The backend records a final `correct`, `incorrect`, `partial`, or `needs_review` result per item, plus safe feedback. If AI is unavailable or uncertain, keep the relevant item `needs_review` when equivalent answers could be valid; do not claim it is wrong solely because the AI call failed.
5. Return the grade, explanation, and next action. Reveal correct answers only according to `feedbackPolicy`. Keep private rubrics and internal model prompts out of learner responses and logs.

AI review output should include a proposed verdict, confidence or uncertainty reason, short learner-facing explanation, and model/version metadata. The backend applies defined thresholds and can queue uncertain cases for author review. Store enough evidence to audit a decision without exposing secrets in client logs.

## Delivery sequence

### Phase 0 — Foundation and contracts

- Set up a repository layout for frontend, backend, AI service, shared API schemas, local MongoDB/MinIO, and environment templates.
- Define typed/versioned block, answer-key, attempt, result, asset, and generation-job contracts. Add schema examples and decide how unknown block versions are handled.
- Define learner, author, and internal-service roles; document the public DTO allowlist and authorization matrix.

**Done when:** the services can start locally, contracts validate sample documents, and a learner response cannot contain a private answer field.

### Phase 1 — Authoring and lesson delivery (MVP)

- Implement lesson CRUD, versioned drafts, publishing, and ordered blocks in the backend.
- Implement the first content blocks: title/outcomes, section, instructions, rule, vocabulary, example, hint, and summary.
- Build an author editor/preview and learner lesson renderer. Unknown block types should show a safe fallback instead of breaking the entire lesson.

**Done when:** an author can publish a small Estonian lesson and a learner can read it on desktop and mobile.

### Phase 2 — Objective exercises and safe grading (MVP)

- Implement single choice, multiple choice, short text, fill blanks, insert ending, word-bank cloze, matching, and word ordering.
- Store answer keys separately; add per-item variants and explicit normalization. Add attempts, retry limits, hint/reveal rules, and deterministic grading.
- Add automated checks for non-disclosure, per-item alternatives, authorization, stale exercise versions, and grading behavior. Check browser network responses for private answer leakage.

**Done when:** learners can complete and retry a mixed lesson, receive item-level feedback, and cannot obtain answer keys through learner APIs before the configured reveal point.

### Phase 3 — AI generation (MVP)

- Accept a learning goal, language, level, desired duration, and optional exercise mix through the backend.
- Run generation as a job. AI returns structured draft blocks and private answer specifications; backend validates schema, IDs, supported types, answer completeness, and basic consistency before saving a draft.
- Provide author review/edit/publish flow and record generation provenance. Add regeneration of a selected block rather than replacing an entire lesson by default.

**Done when:** a goal such as “practice Estonian case endings” produces a reviewable draft with working answer keys and no learner-visible secrets.

### Phase 4 — AI-assisted answer review (MVP)

- Enable per-item `aiReviewOnMismatch` and rubric-based review. Add a structured internal AI review contract, timeouts, failure handling, decision audit, and `needs_review` state.
- Show learners when equivalent answers or AI review are possible. Make author override possible for an uncertain decision.
- Evaluate the reviewer on a small curated set of correct variants, incorrect variants, and ambiguous answers before enabling it broadly.

**Done when:** deterministic alternatives are accepted immediately, a valid unlisted equivalent can be accepted through allowed AI review, and uncertain/unavailable AI produces an honest pending state.

### Phase 5 — Media and expanded formats

- Add MinIO upload/processing and safe delivery, including ownership checks and short-lived download access.
- Add reading/listening passages, audio, images, dialogues, dictation, translation, correction, transformations, and inflection grids.
- Add accessibility metadata and captions/transcripts where applicable. Add speaking and open writing only after their review rubrics and user experience are defined.

**Done when:** lessons can include media and the added exercise types have complete response and answer contracts.

### Phase 6 — Learning loop and operations

- Add completion history, skill tags, mistake review, and spaced repetition suggestions.
- Add search, analytics, content moderation/review tools, backups, migrations, observability, rate limits, and deployment configuration.
- Validate the language-neutral schema with a second language before claiming broad multilingual support.

**Done when:** learners can revisit weak skills, authors can inspect quality, and the services can be operated and recovered reliably.

## Immediate implementation backlog

1. Choose the concrete frontend/backend/AI runtimes and repository layout.
2. Write JSON schemas or equivalent typed contracts for `Block`, `AnswerKey`, `Attempt`, and grading results.
3. Build the backend learner DTO mapper and a non-disclosure test before adding exercise renderers.
4. Implement one complete vertical slice: authored lesson → public delivery → submitted answer → deterministic grade → retry/feedback.
5. Add the remaining MVP exercise types, then generation and AI review.

The primary release gate is that no initial learner API response, cached frontend state, or rendered page contains private answer material. Inspect server responses and generated content paths as part of that gate.

## Local visual demo

The repository includes a dependency-free visual slice for reviewing the learner experience before building the full MVP. `frontend/` serves a static learner interface; `backend/` delivers one published fixture lesson and grades single-choice and two-blank exercises; `ai_service/` exposes a protected placeholder interface and is not called by these exercises. The two public exercise DTOs are built with an explicit allowlist, while their answer keys live in a separate backend module. Both exercise versions use deterministic grading, two attempts, and answer reveal only after the final attempt.

The demo uses two fixed learner tokens and in-memory attempts so it can run with Python alone. These are local-demo adapters, not the production authentication or persistence design. MongoDB remains the primary database for the product, with separate lesson, answer-key, and attempt collections. MinIO remains the media store; this fixture lesson has no media. The next implementation stage adds those adapters and the author review/publish workflow without changing the versioned learner exercise shape.
