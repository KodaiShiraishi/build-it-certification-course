#!/usr/bin/env python3
"""Regression tests for learner-visible artifact evidence validation."""

from __future__ import annotations

import sys
import math
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_question_bank import (  # noqa: E402
    Finding,
    validate_artifact_policy,
    validate_question_artifact_evidence,
)


def validate(question: dict[str, Any]) -> tuple[set[str], set[str]]:
    findings: list[Finding] = []
    valid_types = validate_question_artifact_evidence(question, findings)
    return valid_types, {finding.code for finding in findings}


def validate_policy(questions: list[dict[str, Any]], minimum: int) -> set[str]:
    reviewed_at = date.today().isoformat()
    surface_counts = Counter(str(question.get("assessment_surface", "")) for question in questions)
    targets = {
        "artifact_policy": {
            "calibration_evidence": [
                {
                    "kind": "exam_guide",
                    "status": "current",
                    "url": "https://vendor.example/exam-guide",
                    "reviewed_at": reviewed_at,
                },
                {
                    "kind": "official_sample",
                    "status": "login_required",
                    "reviewed_at": reviewed_at,
                },
            ],
            "calibration_note": "Test fixture for artifact evidence counting.",
            "minimum_questions_with_artifacts": minimum,
            "minimum_by_type": {"code": 1},
            "assessment_surfaces": {
                surface: {
                    "total": total,
                    "minimum_questions_with_artifacts": math.ceil(total * 0.60),
                }
                for surface, total in surface_counts.items()
                if surface
            },
        }
    }
    findings: list[Finding] = []
    validate_artifact_policy(targets, questions, True, ["vendor.example"], findings)
    return {finding.code for finding in findings}


def main() -> int:
    code_a = "```python\nresponse = glue.start_job_run(JobName=job_name)\nreturn response['JobRunId']\n```"
    code_b = "```python\nresponse = glue.get_job_run(JobName=job_name, RunId=job_name)\nreturn response['JobRun']['Id']\n```"
    valid_question = {
        "id": "PASS-CODE-001",
        "assessment_surface": "practice-bank",
        "question_type": "single_choice",
        "artifact_types": ["code"],
        "stem": "Which implementation starts the named AWS Glue job and returns the new run ID?",
        "options": {"A": code_a, "B": code_b},
        "correct": "A",
        "artifact_evidence": [
            {
                "type": "code",
                "location": "option:A",
                "content": code_a,
                "decision_binding": "start_job_run creates a run and JobRunId is the required return value.",
            },
            {
                "type": "code",
                "location": "option:B",
                "content": code_b,
                "decision_binding": "get_job_run reads an existing run and cannot create the required run.",
            },
        ],
        "artifact_selection": {
            "task": "select_correct_artifact",
            "requirement": "Start the named job and return the newly created run identifier.",
            "decision_axes": [
                {
                    "name": "AWS Glue operation",
                    "option_values": {"A": "start_job_run", "B": "get_job_run"},
                }
            ],
            "validation": {
                "method": "shared_fixture",
                "reference": "tests/glue_start_job_candidates.py::test_candidates",
                "validated_correct": ["A"],
                "candidate_results": {
                    "A": "Records one start_job_run call and returns jr-123.",
                    "B": "Attempts to read a run and records no start_job_run call.",
                },
            },
        },
    }
    valid_types, codes = validate(valid_question)
    assert valid_types == {"code"} and not codes, (valid_types, codes)
    assert not validate_policy([valid_question], 1)

    label_only_question = {
        "id": "FAIL-LABEL-ONLY-001",
        "assessment_surface": "practice-bank",
        "format": "code",
        "artifact_types": ["code"],
        "stem": "A team needs to start an AWS Glue job. Which approach is best?",
        "options": {"A": "Use the service API.", "B": "Run the job manually."},
    }
    valid_types, codes = validate(label_only_question)
    assert not valid_types and "missing-artifact-evidence" in codes, (valid_types, codes)
    policy_codes = validate_policy([label_only_question], 1)
    assert "missing-artifact-evidence" in policy_codes, policy_codes
    assert "artifact-question-count-below-minimum" in policy_codes, policy_codes
    assert "artifact-type-count-below-minimum" in policy_codes, policy_codes

    conceptual_questions = [
        {
            "id": f"CONCEPT-{index:03d}",
            "assessment_surface": "practice-bank",
            "artifact_types": [],
            "artifact_evidence": [],
            "stem": "Which service characteristic best fits the stated requirements?",
            "options": {"A": "Characteristic A", "B": "Characteristic B"},
        }
        for index in range(1, 4)
    ]
    second_artifact = {
        **valid_question,
        "id": "PASS-CODE-002",
    }
    third_artifact = {
        **valid_question,
        "id": "PASS-CODE-003",
    }
    exact_floor_questions = [valid_question, second_artifact, third_artifact, *conceptual_questions[:2]]
    assert not validate_policy(exact_floor_questions, 3)

    below_floor_questions = [valid_question, *conceptual_questions, conceptual_questions[0] | {"id": "CONCEPT-004"}]
    policy_codes = validate_policy(below_floor_questions, 1)
    assert "artifact-minimum-below-global-floor" in policy_codes, policy_codes
    assert "artifact-question-count-below-minimum" in policy_codes, policy_codes

    sixty_artifacts = [valid_question | {"id": f"ARTIFACT-{index:03d}"} for index in range(1, 61)]
    forty_concepts = [conceptual_questions[0] | {"id": f"CONCEPT-100-{index:03d}"} for index in range(1, 41)]
    assert not validate_policy([*sixty_artifacts, *forty_concepts], 60)

    fifty_nine_artifacts = sixty_artifacts[:59]
    forty_one_concepts = [conceptual_questions[0] | {"id": f"CONCEPT-059-{index:03d}"} for index in range(1, 42)]
    policy_codes = validate_policy([*fifty_nine_artifacts, *forty_one_concepts], 59)
    assert "artifact-minimum-below-global-floor" in policy_codes, policy_codes
    assert "artifact-question-count-below-minimum" in policy_codes, policy_codes

    hidden_evidence_question = {
        "id": "FAIL-HIDDEN-EVIDENCE-001",
        "artifact_types": ["code"],
        "stem": "A team needs to start an AWS Glue job. Which approach is best?",
        "options": {"A": "Use the service API.", "B": "Run the job manually."},
        "artifact_evidence": [
            {
                "type": "code",
                "location": "stem",
                "content": "response = glue.start_job_run(JobName=job_name)",
                "decision_binding": "The API call determines whether the job starts.",
            }
        ],
    }
    valid_types, codes = validate(hidden_evidence_question)
    assert not valid_types and "artifact-evidence-location-not-option" in codes, (valid_types, codes)

    hidden_option_evidence = {
        **valid_question,
        "id": "FAIL-HIDDEN-OPTION-EVIDENCE-001",
        "artifact_evidence": [
            {
                **valid_question["artifact_evidence"][0],
                "content": "response = glue.stop_job_run(JobName=job_name)",
            },
            valid_question["artifact_evidence"][1],
        ],
    }
    valid_types, codes = validate(hidden_option_evidence)
    assert not valid_types and "artifact-evidence-not-learner-visible" in codes, (valid_types, codes)

    stem_only_question = {
        **valid_question,
        "id": "FAIL-STEM-ONLY-001",
        "stem": f"Inspect this implementation.\n\n{code_a}",
        "options": {"A": "It starts the job.", "B": "It reads an existing run."},
        "artifact_evidence": [
            {
                "type": "code",
                "location": "stem",
                "content": code_a,
                "decision_binding": "The call in the stem determines the behavior.",
            }
        ],
    }
    valid_types, codes = validate(stem_only_question)
    assert not valid_types and "artifact-evidence-location-not-option" in codes, (valid_types, codes)
    assert "artifact-option-coverage-mismatch" in codes, codes

    one_candidate_question = {
        **valid_question,
        "id": "FAIL-ONE-CANDIDATE-001",
        "artifact_evidence": [valid_question["artifact_evidence"][0]],
    }
    valid_types, codes = validate(one_candidate_question)
    assert not valid_types and "artifact-option-coverage-mismatch" in codes, (valid_types, codes)

    identical_candidate_question = {
        **valid_question,
        "id": "FAIL-IDENTICAL-CANDIDATES-001",
        "options": {"A": f"Candidate A\n{code_a}", "B": f"Candidate B\n{code_a}"},
        "artifact_evidence": [
            {**valid_question["artifact_evidence"][0], "location": "option:A"},
            {**valid_question["artifact_evidence"][0], "location": "option:B"},
        ],
        "artifact_selection": {
            **valid_question["artifact_selection"],
            "decision_axes": [
                {
                    "name": "candidate label",
                    "option_values": {"A": "Candidate A", "B": "Candidate B"},
                }
            ],
        },
    }
    valid_types, codes = validate(identical_candidate_question)
    assert not valid_types and "artifact-candidates-not-distinct" in codes, (valid_types, codes)

    no_behavior_difference = {
        **valid_question,
        "id": "FAIL-NO-BEHAVIOR-DIFFERENCE-001",
        "artifact_selection": {
            **valid_question["artifact_selection"],
            "validation": {
                **valid_question["artifact_selection"]["validation"],
                "candidate_results": {"A": "Returns the required run ID.", "B": "Returns the required run ID."},
            },
        },
    }
    valid_types, codes = validate(no_behavior_difference)
    assert not valid_types and "artifact-candidate-results-not-distinct" in codes, (valid_types, codes)

    wrapper_a = """```yaml
apiVersion: course.aws/v1
kind: ArchitectureCandidate
spec:
  services:
    - Amazon SQS
  operations:
    - buffer deliveries
  controls:
    - isolate failures
  flow:
    - Process each partner independently
```"""
    wrapper_b = wrapper_a.replace("Amazon SQS", "not-specified").replace(
        "Process each partner independently", "Process every partner synchronously"
    )
    decorative_wrapper = {
        "id": "FAIL-DECORATIVE-WRAPPER-001",
        "assessment_surface": "practice-bank",
        "question_type": "single_choice",
        "artifact_types": ["configuration"],
        "stem": "Which implementation isolates a failed partner?",
        "options": {"A": wrapper_a, "B": wrapper_b},
        "correct": "A",
        "artifact_evidence": [
            {
                "type": "configuration",
                "location": "option:A",
                "content": wrapper_a,
                "decision_binding": "The services and flow fields claim independent processing.",
            },
            {
                "type": "configuration",
                "location": "option:B",
                "content": wrapper_b,
                "decision_binding": "The placeholder service and synchronous flow do not isolate failures.",
            },
        ],
        "artifact_selection": {
            "task": "select_correct_artifact",
            "requirement": "Isolate a failed partner delivery.",
            "decision_axes": [
                {
                    "name": "declared service",
                    "option_values": {"A": "Amazon SQS", "B": "not-specified"},
                }
            ],
            "validation": {
                "method": "schema_or_dry_run",
                "reference": "tests/decorative_wrapper.py::test_candidates",
                "validated_correct": ["A"],
                "candidate_results": {"A": "Claims isolation.", "B": "Claims synchronous blocking."},
            },
        },
    }
    valid_types, codes = validate(decorative_wrapper)
    assert not valid_types and "artifact-decorative-wrapper" in codes, (valid_types, codes)

    long_line_a = "```python\nresult = client.put_item(TableName=table_name, Item={'pk': {'S': '" + ("x" * 120) + "'}})\n```"
    long_line_b = "```python\nresult = client.get_item(TableName=table_name, Key={'pk': {'S': '" + ("x" * 120) + "'}})\n```"
    long_line_question = {
        **valid_question,
        "id": "FAIL-LONG-ARTIFACT-LINE-001",
        "options": {"A": long_line_a, "B": long_line_b},
        "artifact_evidence": [
            {**valid_question["artifact_evidence"][0], "content": long_line_a},
            {**valid_question["artifact_evidence"][1], "content": long_line_b},
        ],
        "artifact_selection": {
            **valid_question["artifact_selection"],
            "decision_axes": [
                {"name": "DynamoDB operation", "option_values": {"A": "put_item", "B": "get_item"}}
            ],
        },
    }
    valid_types, codes = validate(long_line_question)
    assert not valid_types and "artifact-line-too-long" in codes, (valid_types, codes)

    raw_diagram_a = "```text\nflowchart LR\n  S3[Amazon S3] -->|ObjectCreated| EB[Amazon EventBridge]\n```"
    raw_diagram_b = "```text\nflowchart LR\n  S3[Amazon S3] -->|Schedule| EB[Amazon EventBridge]\n```"
    raw_mermaid_question = {
        "id": "FAIL-RAW-MERMAID-001",
        "assessment_surface": "practice-bank",
        "question_type": "single_choice",
        "artifact_types": ["diagram_ui"],
        "stem": "Which diagram routes object creation events?",
        "options": {"A": raw_diagram_a, "B": raw_diagram_b},
        "correct": "A",
        "artifact_evidence": [
            {
                "type": "diagram_ui",
                "location": "option:A",
                "content": raw_diagram_a,
                "decision_binding": "The ObjectCreated edge represents the required event.",
            },
            {
                "type": "diagram_ui",
                "location": "option:B",
                "content": raw_diagram_b,
                "decision_binding": "The Schedule edge does not represent object creation.",
            },
        ],
        "artifact_selection": {
            "task": "select_correct_artifact",
            "requirement": "Route S3 object creation events through EventBridge.",
            "decision_axes": [
                {"name": "event edge", "option_values": {"A": "ObjectCreated", "B": "Schedule"}}
            ],
            "validation": {
                "method": "derived_result_check",
                "reference": "tests/event_diagrams.py::test_candidates",
                "validated_correct": ["A"],
                "candidate_results": {"A": "Routes ObjectCreated.", "B": "Routes a schedule."},
            },
        },
    }
    valid_types, codes = validate(raw_mermaid_question)
    assert not valid_types and "mermaid-artifact-not-renderable" in codes, (valid_types, codes)

    rendered_diagram_question = {
        **raw_mermaid_question,
        "id": "PASS-MERMAID-DIAGRAM-001",
        "options": {
            "A": raw_diagram_a.replace("```text", "```mermaid"),
            "B": raw_diagram_b.replace("```text", "```mermaid"),
        },
        "artifact_evidence": [
            {
                **raw_mermaid_question["artifact_evidence"][0],
                "content": raw_diagram_a.replace("```text", "```mermaid"),
            },
            {
                **raw_mermaid_question["artifact_evidence"][1],
                "content": raw_diagram_b.replace("```text", "```mermaid"),
            },
        ],
    }
    valid_types, codes = validate(rendered_diagram_question)
    assert valid_types == {"diagram_ui"} and not codes, (valid_types, codes)

    surface_a = [
        valid_question | {"id": f"SURFACE-A-{index:03d}", "assessment_surface": "practice-exam-a"}
        for index in range(1, 6)
    ]
    surface_b_artifact = valid_question | {"id": "SURFACE-B-001", "assessment_surface": "practice-exam-b"}
    surface_b_concepts = [
        {
            **conceptual_questions[0],
            "id": f"SURFACE-B-{index:03d}",
            "assessment_surface": "practice-exam-b",
        }
        for index in range(2, 6)
    ]
    reviewed_at = date.today().isoformat()
    surface_targets = {
        "artifact_policy": {
            "calibration_evidence": [
                {
                    "kind": "exam_guide",
                    "status": "current",
                    "url": "https://vendor.example/exam-guide",
                    "reviewed_at": reviewed_at,
                },
                {"kind": "official_sample", "status": "login_required", "reviewed_at": reviewed_at},
            ],
            "calibration_note": "The aggregate must not hide a weak exam form.",
            "minimum_questions_with_artifacts": 6,
            "minimum_by_type": {"code": 1},
            "assessment_surfaces": {
                "practice-exam-a": {"total": 5, "minimum_questions_with_artifacts": 3},
                "practice-exam-b": {"total": 5, "minimum_questions_with_artifacts": 3},
            },
        }
    }
    findings: list[Finding] = []
    validate_artifact_policy(
        surface_targets,
        [*surface_a, surface_b_artifact, *surface_b_concepts],
        True,
        ["vendor.example"],
        findings,
    )
    surface_codes = {finding.code for finding in findings}
    assert "artifact-question-count-below-minimum" not in surface_codes, surface_codes
    assert "artifact-surface-count-below-minimum" in surface_codes, surface_codes

    prose_a = "Code review evidence says to use the service API."
    prose_b = "Code validation evidence says to run the job manually."
    prose_disguised_as_code = {
        **valid_question,
        "id": "FAIL-PROSE-AS-CODE-001",
        "options": {"A": prose_a, "B": prose_b},
        "artifact_evidence": [
            {
                "type": "code",
                "location": "option:A",
                "content": prose_a,
                "decision_binding": "The displayed code determines the answer.",
            },
            {
                "type": "code",
                "location": "option:B",
                "content": prose_b,
                "decision_binding": "The displayed code determines the answer.",
            },
        ],
        "artifact_selection": {
            **valid_question["artifact_selection"],
            "decision_axes": [
                {
                    "name": "purported implementation",
                    "option_values": {"A": "service API", "B": "run the job manually"},
                }
            ],
        },
    }
    valid_types, codes = validate(prose_disguised_as_code)
    assert not valid_types and "artifact-evidence-not-structural" in codes, (valid_types, codes)

    conceptual_question = {
        "id": "PASS-CONCEPT-001",
        "assessment_surface": "practice-bank",
        "artifact_types": [],
        "artifact_evidence": [],
        "stem": "Which storage service best fits the stated requirements?",
        "options": {"A": "Service A", "B": "Service B"},
    }
    valid_types, codes = validate(conceptual_question)
    assert not valid_types and not codes, (valid_types, codes)

    print("Artifact evidence regression tests: PASS (per-surface 60%, native artifacts, readability, and Mermaid rendering)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
