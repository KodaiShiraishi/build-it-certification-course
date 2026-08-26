#!/usr/bin/env python3
"""Regression tests for learner-visible artifact evidence validation."""

from __future__ import annotations

import copy
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
    validate_question_source_profile,
)


def validate(question: dict[str, Any]) -> tuple[set[str], set[str]]:
    findings: list[Finding] = []
    valid_types = validate_question_artifact_evidence(question, findings)
    return valid_types, {finding.code for finding in findings}


def validate_source_profile(profile: dict[str, Any]) -> set[str]:
    findings: list[Finding] = []
    validate_question_source_profile({"question_source_profile": profile}, True, findings)
    return {finding.code for finding in findings}


def validate_policy(
    questions: list[dict[str, Any]], minimum: int, target_ratio: float | None = None
) -> set[str]:
    reviewed_at = date.today().isoformat()
    surface_counts = Counter(str(question.get("assessment_surface", "")) for question in questions)
    artifact_policy: dict[str, Any] = {
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
        "minimum_by_type": {"code": 1} if minimum > 0 else {},
        "assessment_surfaces": {
            surface: {
                "total": total,
                "minimum_questions_with_artifacts": (
                    math.ceil(total * target_ratio) if target_ratio is not None else minimum
                ),
            }
            for surface, total in surface_counts.items()
            if surface
        },
    }
    if target_ratio is not None:
        artifact_policy["artifact_target_ratio"] = target_ratio
    targets = {"artifact_policy": artifact_policy}
    findings: list[Finding] = []
    validate_artifact_policy(targets, questions, True, ["vendor.example"], findings)
    return {finding.code for finding in findings}


def question_variant(
    question: dict[str, Any],
    question_id: str,
    assessment_surface: str | None = None,
) -> dict[str, Any]:
    variant = copy.deepcopy(question)
    digit_words = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
    }
    contract_token = "".join(digit_words.get(character, character) for character in question_id)
    original_context = variant["artifact_selection"]["stem_contract"]["scenario"]["context"]
    variant_context = f"{original_context} for scenario {question_id}"
    original_observation = variant["artifact_selection"]["stem_contract"]["scenario"][
        "expected_observation"
    ]
    variant_observation = f"{original_observation} for contract {contract_token}"
    variant["id"] = question_id
    variant["stem"] = variant["stem"].replace(original_context, variant_context)
    variant["stem"] = variant["stem"].replace(original_observation, variant_observation)
    variant["artifact_selection"]["stem_contract"]["scenario"]["context"] = variant_context
    variant["artifact_selection"]["stem_contract"]["scenario"][
        "expected_observation"
    ] = variant_observation
    variant["artifact_selection"]["stem_contract"]["deletion_test"]["review_reference"] = (
        f"reviews/artifact-deletion.csv#{question_id}"
    )
    if assessment_surface is not None:
        variant["assessment_surface"] = assessment_surface
    return variant


def main() -> int:
    valid_source_profile = {
        "analyzed_before_authoring": True,
        "sample_size": 20,
        "observed_question_type_counts": {
            "single_choice": 16,
            "multiple_response": 4,
        },
        "observed_primary_decision_pattern_counts": {
            "service_or_feature_selection": 8,
            "configuration_or_permission_change": 5,
            "failure_diagnosis": 4,
            "cost_performance_tradeoff": 3,
        },
        "scope_analysis": {
            "official_weight_status": "published",
            "official_domain_weights": {
                "D1": 0.34,
                "D2": 0.26,
                "D3": 0.22,
                "D4": 0.18,
            },
            "official_objectives": ["D1", "D2", "D3", "D4"],
            "observed_primary_objective_counts": {
                "D1": 7,
                "D2": 5,
                "D3": 4,
                "D4": 0,
                "unmapped": 4,
            },
            "observed_primary_content_family_counts": {
                "ingestion_and_transformation": 7,
                "data_store_management": 5,
                "operations_and_monitoring": 4,
                "security_and_governance": 4,
            },
            "observed_service_feature_counts": {
                "object storage": 6,
                "managed ETL": 5,
                "stream processing": 4,
            },
            "observed_integration_pattern_counts": {
                "source_to_ingestion_to_lake": 5,
                "event_to_stream_processor": 3,
            },
            "observed_lifecycle_stage_counts": {
                "ingest": 7,
                "transform": 5,
                "operate": 4,
                "secure": 4,
            },
            "observed_constraint_counts": {
                "least_operational_overhead": 6,
                "cost_optimization": 4,
                "least_privilege": 3,
            },
            "scope_gaps": [
                "The small source does not cover every official objective.",
            ],
            "authoring_scope_decisions": [
                "Use official domain weights for final coverage and source observations for scenario depth.",
            ],
            "scope_selection_patterns": [
                {
                    "id": "constraint_to_managed_boundary",
                    "description": "The source turns an operational constraint into a managed-service boundary decision.",
                    "observed_count": 6,
                    "question_transformation": "Compare supported service behavior under the stated operational constraint.",
                },
                {
                    "id": "failure_signal_to_remediation",
                    "description": "The source maps an observable failure signal to a corrective action.",
                    "observed_count": 4,
                    "question_transformation": "Present a failure condition and ask for the supported remediation.",
                },
            ],
            "official_scope_extrapolations": [
                {
                    "objective": "D4",
                    "primary_source_topics": ["least-privilege access and data protection"],
                    "primary_source_urls": ["https://vendor.example/security-guide"],
                    "inferred_question_patterns": [
                        "Select the least-privilege control that preserves the required data flow."
                    ],
                    "basis_pattern_ids": ["constraint_to_managed_boundary"],
                    "confidence": "medium",
                    "reasoning": "The official objective contains the same constraint-to-boundary decision shape.",
                    "authoring_status": "adopted",
                }
            ],
        },
        "artifact_location_counts": {
            "stem_artifact_questions": 4,
            "option_artifact_questions": 6,
            "both_stem_and_option_artifact_questions": 2,
            "neither_artifact_questions": 12,
        },
        "artifact_location_rates": {
            "stem_artifact_rate": 0.2,
            "option_artifact_rate": 0.3,
            "both_stem_and_option_artifact_rate": 0.1,
            "neither_artifact_rate": 0.6,
        },
        "stem_artifact_by_type": {"logs_metrics": 3, "configuration": 1},
        "option_artifact_by_type": {"configuration": 4, "command": 2},
        "classification_rule": {
            "mention_only_is_artifact": False,
            "requires_learner_visible_material_and_decision_dependency": True,
        },
    }
    assert not validate_source_profile(valid_source_profile)

    invalid_overlap_profile = copy.deepcopy(valid_source_profile)
    invalid_overlap_profile["artifact_location_counts"]["neither_artifact_questions"] = 13
    profile_codes = validate_source_profile(invalid_overlap_profile)
    assert "question-source-artifact-overlap-mismatch" in profile_codes, profile_codes

    invalid_rate_profile = copy.deepcopy(valid_source_profile)
    invalid_rate_profile["artifact_location_rates"]["stem_artifact_rate"] = 0.3
    profile_codes = validate_source_profile(invalid_rate_profile)
    assert "question-source-artifact-rate-mismatch" in profile_codes, profile_codes

    mention_only_profile = copy.deepcopy(valid_source_profile)
    mention_only_profile["classification_rule"]["mention_only_is_artifact"] = True
    profile_codes = validate_source_profile(mention_only_profile)
    assert "invalid-question-source-classification-rule" in profile_codes, profile_codes

    invalid_scope_profile = copy.deepcopy(valid_source_profile)
    invalid_scope_profile["scope_analysis"]["observed_primary_content_family_counts"][
        "ingestion_and_transformation"
    ] = 6
    profile_codes = validate_source_profile(invalid_scope_profile)
    assert "question-source-distribution-total-mismatch" in profile_codes, profile_codes

    outside_scope_profile = copy.deepcopy(valid_source_profile)
    outside_scope_profile["scope_analysis"]["observed_primary_objective_counts"] = {
        "D1": 7,
        "D2": 5,
        "D3": 4,
        "D4": 3,
        "D5": 1,
    }
    profile_codes = validate_source_profile(outside_scope_profile)
    assert "question-source-objective-outside-official-scope" in profile_codes, profile_codes

    missing_extrapolation_profile = copy.deepcopy(valid_source_profile)
    missing_extrapolation_profile["scope_analysis"]["official_scope_extrapolations"] = []
    profile_codes = validate_source_profile(missing_extrapolation_profile)
    assert "invalid-question-source-scope-extrapolations" in profile_codes, profile_codes
    assert "question-source-unobserved-objective-not-extrapolated" in profile_codes, profile_codes

    unknown_pattern_profile = copy.deepcopy(valid_source_profile)
    unknown_pattern_profile["scope_analysis"]["official_scope_extrapolations"][0][
        "basis_pattern_ids"
    ] = ["missing-pattern"]
    profile_codes = validate_source_profile(unknown_pattern_profile)
    assert "question-source-extrapolation-unknown-pattern" in profile_codes, profile_codes

    code_a = "```python\nresponse = glue.start_job_run(JobName=job_name)\nreturn response['JobRunId']\n```"
    code_b = "```python\nresponse = glue.get_job_run(JobName=job_name, RunId=job_name)\nreturn response['JobRun']['Id']\n```"
    valid_question = {
        "id": "PASS-CODE-001",
        "assessment_surface": "practice-bank",
        "question_type": "single_choice",
        "artifact_types": ["code"],
        "stem": (
            "An application invokes AWS Glue and has the job name. Which Python implementation "
            "starts exactly one job run and returns the new JobRunId?"
        ),
        "options": {"A": code_a, "B": code_b},
        "correct": "A",
        "correct_explanation": (
            "`start_job_run` records one start call and returns jr-123, so option A starts the "
            "requested run and exposes the newly created JobRunId."
        ),
        "wrong_explanations": {
            "B": (
                "`get_job_run` records no start_job_run call and only attempts to read an existing "
                "run, so option B cannot create the requested run."
            )
        },
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
            "stem_contract": {
                "artifact_request": "Which Python implementation",
                "scenario": {
                    "context": "An application invokes AWS Glue",
                    "input_or_state": "has the job name",
                    "hard_constraints": ["starts exactly one job run"],
                    "expected_observation": "returns the new JobRunId",
                },
                "deletion_test": {
                    "artifact_candidates_required": True,
                    "review_reference": "reviews/artifact-deletion.csv#PASS-CODE-001",
                },
            },
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
            "explanation_bindings": {
                "A": {
                    "artifact_excerpt": "start_job_run",
                    "result_excerpt": "returns jr-123",
                    "explanation_excerpt": (
                        "`start_job_run` records one start call and returns jr-123, so option A "
                        "starts the requested run and exposes the newly created JobRunId."
                    ),
                },
                "B": {
                    "artifact_excerpt": "get_job_run",
                    "result_excerpt": "records no start_job_run call",
                    "explanation_excerpt": (
                        "`get_job_run` records no start_job_run call and only attempts to read an "
                        "existing run, so option B cannot create the requested run."
                    ),
                },
            },
        },
    }
    valid_types, codes = validate(valid_question)
    assert valid_types == {"code"} and not codes, (valid_types, codes)
    assert not validate_policy([valid_question], 1)

    stale_correct_explanation = copy.deepcopy(valid_question)
    stale_correct_explanation["id"] = "FAIL-STALE-CORRECT-EXPLANATION-001"
    stale_correct_explanation["correct_explanation"] = (
        "The former prose answer was appropriate because it followed the preferred service "
        "architecture and met the general requirement."
    )
    valid_types, codes = validate(stale_correct_explanation)
    assert not valid_types and "artifact-explanation-binding-not-visible" in codes, (
        valid_types,
        codes,
    )

    stale_wrong_explanation = copy.deepcopy(valid_question)
    stale_wrong_explanation["id"] = "FAIL-STALE-WRONG-EXPLANATION-001"
    stale_wrong_explanation["wrong_explanations"]["B"] = (
        "The former prose option is less suitable because it does not follow the recommended "
        "architecture for the scenario."
    )
    valid_types, codes = validate(stale_wrong_explanation)
    assert not valid_types and "artifact-explanation-binding-not-visible" in codes, (
        valid_types,
        codes,
    )

    legacy_generic_stem = copy.deepcopy(valid_question)
    legacy_generic_stem["id"] = "FAIL-LEGACY-GENERIC-STEM-001"
    legacy_generic_stem["stem"] = (
        "A team needs to start an AWS Glue job. Which general approach is best?"
    )
    valid_types, codes = validate(legacy_generic_stem)
    assert not valid_types and "artifact-stem-contract-not-visible" in codes, (
        valid_types,
        codes,
    )
    assert "artifact-stem-scenario-not-visible" in codes, codes

    changed_candidate_with_stale_explanation = copy.deepcopy(valid_question)
    changed_candidate_with_stale_explanation["id"] = "FAIL-CHANGED-CANDIDATE-STALE-EXPLANATION-001"
    changed_code_a = code_a.replace("start_job_run", "stop_job_run")
    changed_candidate_with_stale_explanation["options"]["A"] = changed_code_a
    changed_candidate_with_stale_explanation["artifact_evidence"][0]["content"] = changed_code_a
    changed_candidate_with_stale_explanation["artifact_selection"]["decision_axes"][0][
        "option_values"
    ]["A"] = "stop_job_run"
    valid_types, codes = validate(changed_candidate_with_stale_explanation)
    assert not valid_types and "artifact-explanation-binding-artifact-not-visible" in codes, (
        valid_types,
        codes,
    )

    reused_contract = copy.deepcopy(valid_question)
    reused_contract["id"] = "FAIL-REUSED-SCENARIO-CONTRACT-002"
    reused_contract["stem"] = reused_contract["stem"].replace(
        "An application invokes AWS Glue",
        "A different application invokes AWS Glue",
    )
    reused_contract["artifact_selection"]["stem_contract"]["scenario"]["context"] = (
        "A different application invokes AWS Glue"
    )
    policy_codes = validate_policy([valid_question, reused_contract], 2)
    assert "artifact-scenario-contract-reused" in policy_codes, policy_codes

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
    second_artifact = question_variant(valid_question, "PASS-CODE-002")
    third_artifact = question_variant(valid_question, "PASS-CODE-003")
    exact_floor_questions = [valid_question, second_artifact, third_artifact, *conceptual_questions[:2]]
    assert not validate_policy(exact_floor_questions, 3)

    thirty_percent_questions = [
        valid_question,
        second_artifact,
        third_artifact,
        *[
            conceptual_questions[0] | {"id": f"CONCEPT-THIRTY-{index:03d}"}
            for index in range(1, 8)
        ],
    ]
    assert not validate_policy(thirty_percent_questions, 3, 0.30)

    source_profile_minimum_questions = [
        valid_question,
        *[
            conceptual_questions[0] | {"id": f"CONCEPT-SOURCE-{index:03d}"}
            for index in range(1, 10)
        ],
    ]
    assert not validate_policy(source_profile_minimum_questions, 1)
    assert not validate_policy([conceptual_questions[0] | {"id": "CONCEPT-ZERO-001"}], 0)

    below_floor_questions = [valid_question, *conceptual_questions, conceptual_questions[0] | {"id": "CONCEPT-004"}]
    policy_codes = validate_policy(below_floor_questions, 1, 0.60)
    assert "artifact-minimum-below-global-floor" in policy_codes, policy_codes
    assert "artifact-question-count-below-minimum" in policy_codes, policy_codes

    sixty_artifacts = [
        question_variant(valid_question, f"ARTIFACT-{index:03d}")
        for index in range(1, 61)
    ]
    forty_concepts = [conceptual_questions[0] | {"id": f"CONCEPT-100-{index:03d}"} for index in range(1, 41)]
    assert not validate_policy([*sixty_artifacts, *forty_concepts], 60, 0.60)

    fifty_nine_artifacts = sixty_artifacts[:59]
    forty_one_concepts = [conceptual_questions[0] | {"id": f"CONCEPT-059-{index:03d}"} for index in range(1, 42)]
    policy_codes = validate_policy([*fifty_nine_artifacts, *forty_one_concepts], 59, 0.60)
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
        "stem": (
            "An event-routing team receives Amazon S3 object creation events. Which Mermaid "
            "architecture diagram sends each event through Amazon EventBridge and shows the "
            "ObjectCreated edge?"
        ),
        "options": {"A": raw_diagram_a, "B": raw_diagram_b},
        "correct": "A",
        "correct_explanation": (
            "`ObjectCreated` is the decisive edge; the shared derivation confirms that the edge "
            "routes ObjectCreated events through Amazon EventBridge."
        ),
        "wrong_explanations": {
            "B": (
                "`Schedule` is the decisive edge; the shared derivation shows that the edge routes "
                "a scheduled event rather than an Amazon S3 object creation event."
            )
        },
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
            "stem_contract": {
                "artifact_request": "Which Mermaid architecture diagram",
                "scenario": {
                    "context": "An event-routing team receives Amazon S3 object creation events",
                    "input_or_state": "Amazon S3 object creation events",
                    "hard_constraints": ["sends each event through Amazon EventBridge"],
                    "expected_observation": "shows the ObjectCreated edge",
                },
                "deletion_test": {
                    "artifact_candidates_required": True,
                    "review_reference": "reviews/artifact-deletion.csv#FAIL-RAW-MERMAID-001",
                },
            },
            "decision_axes": [
                {"name": "event edge", "option_values": {"A": "ObjectCreated", "B": "Schedule"}}
            ],
            "validation": {
                "method": "derived_result_check",
                "reference": "tests/event_diagrams.py::test_candidates",
                "validated_correct": ["A"],
                "candidate_results": {
                    "A": "edge routes ObjectCreated events",
                    "B": "edge routes a scheduled event",
                },
            },
            "explanation_bindings": {
                "A": {
                    "artifact_excerpt": "ObjectCreated",
                    "result_excerpt": "edge routes ObjectCreated events",
                    "explanation_excerpt": (
                        "`ObjectCreated` is the decisive edge; the shared derivation confirms that "
                        "the edge routes ObjectCreated events through Amazon EventBridge."
                    ),
                },
                "B": {
                    "artifact_excerpt": "Schedule",
                    "result_excerpt": "edge routes a scheduled event",
                    "explanation_excerpt": (
                        "`Schedule` is the decisive edge; the shared derivation shows that the edge "
                        "routes a scheduled event rather than an Amazon S3 object creation event."
                    ),
                },
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
        question_variant(
            valid_question,
            f"SURFACE-A-{index:03d}",
            "practice-exam-a",
        )
        for index in range(1, 6)
    ]
    surface_b_artifact = question_variant(
        valid_question,
        "SURFACE-B-001",
        "practice-exam-b",
    )
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

    print(
        "Artifact evidence regression tests: PASS (source-profile format, decision-pattern, official/observed "
        "scope, pattern-based official-scope extrapolation, and stem/option 2x2 validation, minimums without a "
        "universal ratio, optional per-surface ratio floors, atomic stem/explanation bindings, native artifacts, "
        "readability, and Mermaid rendering)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
