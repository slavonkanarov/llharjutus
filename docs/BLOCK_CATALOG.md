# Learner-facing block catalog

This catalog is an extensible product inventory, not a requirement to implement every block in the first release. A lesson is an ordered sequence of blocks. Blocks can be informational, interactive, navigational, or feedback-oriented. Each block has a stable ID, a version, learner-visible content, optional media references, and presentation/accessibility metadata. Interactive blocks additionally have a private answer specification and grading policy.

## Priority legend

- **MVP**: enough to create useful Estonian lessons and verify the answer boundary.
- **Next**: high-value additions after the core lesson flow works.
- **Later**: specialized formats or features that need more complex media, AI, or analytics.

## Lesson structure and guidance

| Block | Purpose | Priority |
| --- | --- | --- |
| Lesson title and learning outcomes | State what the learner will be able to do. | MVP |
| Prerequisites and estimated time | Set expectations and link required prior knowledge. | Next |
| Section heading and divider | Group blocks into a readable sequence. | MVP |
| Instructions | Explain what to read, listen to, or submit. | MVP |
| Context or scenario | Introduce a real-life situation for the lesson. | MVP |
| Hint, expandable clue, and step-by-step hint | Help without immediately revealing the answer; hints can be tied to an exercise. | MVP |
| Worked example | Show a model answer with an explanation before practice. | MVP |
| Summary and key takeaways | Recap the rule and common mistakes. | MVP |
| Reflection and self-rating | Ask learners what still feels uncertain. | Next |
| Branch or recommendation | Route learners to remediation or harder practice. | Later |

## Explanations and reference material

| Block | Purpose | Priority |
| --- | --- | --- |
| Rule and explanation | Explain grammar, spelling, pronunciation, or usage. | MVP |
| Rule with exceptions | Show a rule beside its exceptions and restrictions. | MVP |
| Before/after or correct/incorrect comparison | Contrast similar forms and explain the difference. | MVP |
| Sentence pattern or template | Display reusable sentence structures and substitutions. | MVP |
| Vocabulary list or new-word cards | Show lemma, translation/gloss, part of speech, examples, and optional audio. | MVP |
| Inflection or conjugation table | Show forms and labels as teaching content. | Next |
| Pronunciation guide | Explain sounds, stress, rhythm, or spelling-to-sound patterns. | Next |
| Mini glossary and cultural note | Define terms or explain context and register. | Next |
| Source passage and translation | Provide a paired reference text when pedagogically appropriate. | Next |
| Teacher note | Author-only guidance; never included in learner responses. | Next |

## Input and media

| Block | Purpose | Priority |
| --- | --- | --- |
| Rich text, quote, and table | Present reading material and structured information. | MVP |
| Image or illustrated scene | Provide visual context, alt text, and optional captions. | Next |
| Audio clip and transcript | Support listening and pronunciation; transcript visibility is configurable. | Next |
| Video clip and captions | Provide contextual listening and demonstrations. | Later |
| Dialogue or story | Present a multi-turn conversation or narrative, with optional speaker audio. | Next |
| Interactive transcript | Highlight words while audio plays. | Later |
| Downloadable reference sheet | Provide optional printable material. | Later |

## Objective exercises

Each exercise can contain one or several independently graded items. The private answer specification belongs to each item or blank; a whole-exercise score is derived from those results.

| Exercise | Learner interaction | Private answer specification | Priority |
| --- | --- | --- | --- |
| Single-choice question | Select one option. | Correct option ID. | MVP |
| Multiple-choice question | Select all valid options. | Correct option ID set; partial-credit rule. | MVP |
| True/false or yes/no | Choose a binary answer. | Correct value and explanation. | MVP |
| Short text answer | Enter a word, phrase, or short sentence. | Accepted variants, normalization, optional equivalent-answer review. | MVP |
| Fill one blank | Complete a missing word or phrase. | Accepted variants for that blank. | MVP |
| Fill several blanks | Complete multiple independent blanks. | Accepted variants for every blank; blank IDs. | MVP |
| Insert an ending or affix | Enter the required form or suffix. | Accepted surface forms per target; rule explanation. | MVP |
| Word-bank cloze | Drag or select words into blanks. | Correct token ID(s) per blank. | MVP |
| Match pairs | Connect words, translations, forms, definitions, or audio and text. | Private pair mapping. | MVP |
| Order words into a sentence | Arrange tokens. | One or more valid sequences. | MVP |
| Order sentences or dialogue turns | Reconstruct a passage or conversation. | One or more valid sequences. | Next |
| Classify into categories | Place items under case, tense, meaning, register, etc. | Accepted category IDs per item. | Next |
| Select a word in a text | Mark a form or phrase matching a prompt. | Accepted token/span IDs. | Next |
| Highlight an error | Locate a mistake. | Accepted span IDs and explanation. | Next |
| Correct an error | Rewrite an incorrect word or sentence. | Accepted corrections, normalization, optional AI review. | Next |
| Transform a sentence | Change tense, person, case, number, polarity, etc. | Accepted rewrites, rubric, optional AI review. | Next |
| Inflection/conjugation grid | Fill a table of forms. | Accepted variants for each cell. | Next |
| Build a sentence from components | Assemble a valid phrase from constrained parts. | Accepted structures/sequences or rubric. | Next |
| Translation | Translate a word, phrase, or sentence. | Multiple accepted translations plus optional AI review. | Next |
| Synonym/antonym or definition | Supply a related word or select its meaning. | Accepted variants or correct option IDs. | Next |
| Collocation and word-family task | Complete or group common combinations/derivations. | Accepted variants/mappings. | Next |
| Image labeling | Attach words to regions or objects. | Private region-to-label mapping. | Later |
| Pronunciation discrimination | Choose which sound or word was heard. | Correct option ID, audio reference. | Later |

## Reading, listening, speaking, and writing exercises

| Exercise | Learner interaction | Grading approach | Priority |
| --- | --- | --- | --- |
| Reading comprehension | Answer questions about a passage; reuse choice, text, or matching items. | Per-item answer keys and optional AI review for open answers. | Next |
| Listening comprehension | Answer questions after hearing audio. | Per-item answer keys and optional AI review. | Next |
| Dictation | Type what was heard. | Accepted transcriptions, punctuation policy, optional AI review. | Next |
| Audio-to-text matching | Match clips to text or images. | Private pair mapping. | Next |
| Read aloud | Record speech from a given prompt. | Speech pipeline plus review rubric; never silently auto-fail uncertain audio. | Later |
| Pronunciation practice | Record and compare a target sound, word, or sentence. | Speech pipeline plus pronunciation rubric. | Later |
| Guided writing | Write from a prompt with required words or structures. | Rubric, AI review, and human review path. | Later |
| Free writing | Compose a short text with feedback on meaning and language. | Rubric and human review path. | Later |
| Guided conversation or role-play | Respond across multiple turns in a scenario. | Per-turn constraints and conversation rubric. | Later |
| Spoken response | Answer orally rather than by typing. | Speech pipeline, rubric, human review path. | Later |

## Practice and feedback blocks

| Block | Purpose | Priority |
| --- | --- | --- |
| Immediate result | Show correct, incorrect, partial, or needs-review status after submission. | MVP |
| Explanation of a result | Explain the rule behind a grade, tied to submitted work. | MVP |
| Retry and reveal controls | Offer another attempt or show the solution according to feedback policy. | MVP |
| Lesson completion and score | Summarize completion and per-skill results. | Next |
| Review card and spaced repetition prompt | Revisit a word or structure later. | Next |
| Personal mistake review | Repractice previously missed items. | Next |
| AI coaching suggestion | Offer a targeted follow-up after a graded response. | Later |

## Shared behavior for every interactive block

- Public data includes the prompt, visible choices/tokens, input constraints, hint availability, and whether equivalent answers or AI review may apply. It never includes accepted answers, correct option IDs, hidden pair/order maps, rubrics, or private grading prompts before submission.
- Private data is keyed by exercise and item ID and can contain multiple accepted variants. Normalization is explicit per item: case, whitespace, punctuation, Unicode, and diacritics must not be silently ignored. This matters for Estonian inflection and spelling.
- Grading returns an item-level status: `correct`, `incorrect`, `partial`, or `needs_review`, plus safe feedback. AI review is an optional policy for deterministic mismatches or open-ended work; the backend owns the final decision.
- Feedback policy controls attempts, hints, scoring, and when an answer may be revealed. A revealed answer is an intentional post-submission response, never part of the initial exercise payload.
- Option IDs, blank IDs, and media metadata must be opaque. Public ordering and IDs must not encode correctness.
- Content must support keyboard use, screen readers, alt text, captions/transcripts where relevant, and mobile layouts. Media references point to managed objects, not embedded secrets.
