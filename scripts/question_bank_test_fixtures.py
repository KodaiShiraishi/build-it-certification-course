"""Executable fixtures for validator tests, not certification authoring templates."""

from __future__ import annotations

import builtins
import copy
from typing import Any


CASES = {
    "filter": ({"values": [-2, 0, 3]}, "keep only positive values",
               "[value for value in values if value > 0]", "[value for value in values if value < 0]", [3]),
    "total": ({"values": [2, 3, 4]}, "compute the total",
              "sum(values)", "len(values)", 9),
    "flatten": ({"rows": [[1, 2], [3]]}, "flatten the nested rows",
                "[value for row in rows for value in row]", "[row for row in rows]", [1, 2, 3]),
    "descending": ({"values": [1, 3, 2]}, "sort values in descending order",
                   "sorted(values, reverse=True)", "sorted(values)", [3, 2, 1]),
    "stable_unique": ({"values": [3, 1, 3]}, "remove duplicates while preserving first occurrence order",
                      "list(dict.fromkeys(values))", "sorted(set(values))", [3, 1]),
    "count": ({"values": [1, 1, 2], "target": 1}, "count occurrences of the target",
              "sum(value == target for value in values)", "sum(value != target for value in values)", 2),
    "fewest_calls": ({"values": [2, 3, 4]}, "compute the total with the fewest sum calls",
                     "sum(values)", "sum(sum([value]) for value in values)", 9),
}


def make_artifact_question(case: str, question_id: str | None = None,
                           surface: str = "practice-bank") -> dict[str, Any]:
    inputs, requirement, expression_a, expression_b, expected = CASES[case]
    expressions = {"A": expression_a, "B": expression_b}
    results: dict[str, Any] = {}
    calls: dict[str, int] = {}
    observations: dict[str, str] = {}
    for key, expression in expressions.items():
        count = 0
        def tracked_sum(values: Any) -> Any:
            nonlocal count
            count += 1
            return builtins.sum(values)
        namespace = copy.deepcopy(inputs)
        namespace["sum"] = tracked_sum
        exec("result = " + expression, namespace)
        results[key], calls[key] = namespace["result"], count
        observations[key] = f"produces {results[key]!r}"
        if case == "fewest_calls":
            observations[key] += f" using {count} sum calls"
    assert results["A"] == expected
    if case == "fewest_calls":
        assert results["B"] == expected and calls["A"] < calls["B"]
    else:
        assert results["B"] != expected
    options = {key: f"```python\nresult = {expression}\n```" for key, expression in expressions.items()}
    explanations = {
        key: f"`{expression}` {observations[key]}; " + (
            "this meets the stated selection criterion." if key == "A" else
            "the output is feasible but uses more calls than A." if case == "fewest_calls" else
            "this differs from the required output."
        ) for key, expression in expressions.items()
    }
    context = "A Python program transforms an in-memory input"
    state = f"input values are {inputs!r}"
    observation = f"the required output is {expected!r}"
    identifier = question_id or f"EXECUTABLE-{case}"
    return {
        "id": identifier, "objective": "validator-fixture", "difficulty": "medium",
        "cognitive_type": "application", "assessment_surface": surface,
        "question_type": "single_choice", "artifact_types": ["code"],
        "stem": f"{context}; {state}. To {requirement}, {observation}. Which Python implementation should be used?",
        "options": options, "correct": "A", "correct_explanation": explanations["A"],
        "wrong_explanations": {"B": explanations["B"]}, "links": ["lectures/python.md"],
        "artifact_evidence": [
            {"type": "code", "location": f"option:{key}", "content": options[key],
             "decision_binding": f"{expression} determines the transformation for the given input."}
            for key, expression in expressions.items()
        ],
        "artifact_selection": {
            "task": "select_correct_artifact", "requirement": requirement,
            "stem_contract": {
                "artifact_request": "Which Python implementation",
                "scenario": {"context": context, "input_or_state": state,
                             "hard_constraints": [requirement], "expected_observation": observation},
                "deletion_test": {"artifact_candidates_required": True,
                                  "review_reference": f"tests/decisions#{identifier}"},
            },
            "decision_axes": [{"name": "transformation", "option_values": expressions}],
            "validation": {"method": "shared_fixture", "reference": f"question_bank_test_fixtures.py::{case}",
                           "fixture_inputs": copy.deepcopy(inputs), "validated_correct": ["A"],
                           "candidate_results": observations},
            "explanation_bindings": {
                key: {"artifact_excerpt": expressions[key], "result_excerpt": observations[key],
                      "explanation_excerpt": explanations[key]} for key in expressions
            },
        },
    }
