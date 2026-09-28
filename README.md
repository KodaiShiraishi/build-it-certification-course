# Build IT Certification Course

A Codex skill for designing, expanding, auditing, validating, and publishing exam-aligned IT certification courses and study sites.

It supports certification work for platforms and domains such as Databricks, AWS, Microsoft Azure, Google Cloud, Kubernetes, security, networking, and databases. The skill instructions and reference material are primarily written in Japanese, while product names, exam codes, APIs, identifiers, URLs, and code remain unchanged.

## What this skill covers

- Confirming the current official exam scope before course design
- Building prerequisite-aware lectures, glossaries, and hands-on labs
- Creating and reviewing high-quality practice questions and mock exams
- Applying vendor-neutral writing principles, with supplied question and explanation sources calibrating their respective roles
- Comparing feasible solutions by the stated operational, cost, or performance objective, with candidate-specific explanations
- Validating question-bank structure, explanations, artifacts, and reproducibility
- Organizing multi-course certification study sites
- Applying release gates before publication
- Recording material project decisions when needed and updating the skill when requested

## Repository structure

```text
.
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   `-- ...
`-- scripts/
    `-- ...
```

`SKILL.md` is the entry point. Supporting standards and procedures live under `references/`, and deterministic validation helpers live under `scripts/`.

The [course settings](references/course-settings.md) separate common quality requirements from this personal skill's retained portal defaults. The [review update policy](references/review-update-policy.md) defines checks for content, dependency, link, and display changes without weakening current-version evidence.

## Install

### Using Codex

Invoke `$skill-installer` and ask it to install the skill at the repository root from:

```text
https://github.com/KodaiShiraishi/build-it-certification-course
```

### Manual installation on Windows

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null
git clone https://github.com/KodaiShiraishi/build-it-certification-course.git `
  "$env:USERPROFILE\.agents\skills\build-it-certification-course"
```

Restart Codex if the skill does not appear immediately.

## Use

Invoke the skill explicitly:

```text
$build-it-certification-course
```

Then describe the certification, course, audit, repair, validation, or publication task. Codex may also select the skill automatically when the request matches the scope in `SKILL.md`.

## Validation

The repository includes validators for learning contracts, question banks, artifact coverage, and generated-output reproducibility. Run the relevant project-level tests and release gates in addition to validating the skill structure itself.

Run the validator regression suites with an existing Python environment:

```text
python -B -X utf8 scripts/test_validate_question_bank_artifacts.py
python -B -X utf8 scripts/test_question_authoring_contracts.py
python -B -X utf8 scripts/test_validate_learning_contract.py
```

Strict learning-contract checks require canonical question text and `learning_requirements`, not ID-only exports. See [the learning-contract schema](references/lecture-completeness-and-prerequisite-closure.md). Review-ledger checks establish record consistency; actual reviewer identity and independence require separate evidence.

For changes to the skill's decisions, use the relevant [behavioral cases](references/skill-behavior-checks.md). These test source interpretation, scope, settings, and review planning; they complement structural and validator tests.

## License

This repository is published without an open-source license.
