#!/usr/bin/env python3
"""Regression tests for learner-visible artifact evidence validation."""

from __future__ import annotations

import sys
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
        }
    }
    findings: list[Finding] = []
    validate_artifact_policy(targets, questions, True, ["vendor.example"], findings)
    return {finding.code for finding in findings}


def main() -> int:
    code = "```python\nresponse = glue.start_job_run(JobName=job_name)\nrun_id = response['JobRunId']\n```"
    valid_question = {
        "id": "PASS-CODE-001",
        "artifact_types": ["code"],
        "stem": f"Inspect the following code and select the statement that is true.\n\n{code}",
        "options": {"A": "The returned run ID is retained.", "B": "No job is started."},
        "artifact_evidence": [
            {
                "type": "code",
                "location": "stem",
                "content": code,
                "decision_binding": "The start_job_run call and JobRunId lookup determine the result.",
            }
        ],
    }
    valid_types, codes = validate(valid_question)
    assert valid_types == {"code"} and not codes, (valid_types, codes)
    assert not validate_policy([valid_question], 1)

    label_only_question = {
        "id": "FAIL-LABEL-ONLY-001",
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
    assert not valid_types and "artifact-evidence-not-learner-visible" in codes, (valid_types, codes)

    prose_disguised_as_code = {
        "id": "FAIL-PROSE-AS-CODE-001",
        "artifact_types": ["code"],
        "stem": "Code review evidence: choose the most operationally efficient answer.",
        "options": {"A": "Use the service API.", "B": "Run the job manually."},
        "artifact_evidence": [
            {
                "type": "code",
                "location": "stem",
                "content": "Code review evidence: choose the most operationally efficient answer.",
                "decision_binding": "The displayed code determines the answer.",
            }
        ],
    }
    valid_types, codes = validate(prose_disguised_as_code)
    assert not valid_types and "artifact-evidence-not-structural" in codes, (valid_types, codes)

    conceptual_question = {
        "id": "PASS-CONCEPT-001",
        "artifact_types": [],
        "artifact_evidence": [],
        "stem": "Which storage service best fits the stated requirements?",
        "options": {"A": "Service A", "B": "Service B"},
    }
    valid_types, codes = validate(conceptual_question)
    assert not valid_types and not codes, (valid_types, codes)

    print("Artifact evidence regression tests: PASS (60% boundary, evidence, and rejection fixtures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
