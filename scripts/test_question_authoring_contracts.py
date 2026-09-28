"""Regression cases for source formats, feasible alternatives, and reskin detection."""

from __future__ import annotations

import argparse
import copy

from question_bank_test_fixtures import make_artifact_question
from test_validate_question_bank_artifacts import validate, validate_policy
from validate_question_bank import Finding, validate_structure, question_hash, _artifact_candidate_fingerprint


def structure_codes(question: dict) -> set[str]:
    findings: list[Finding] = []
    validate_structure([question], argparse.Namespace(min_correct_explanation=0, min_wrong_explanation=0), findings)
    return {finding.code for finding in findings}


def main() -> int:
    assert _artifact_candidate_fingerprint("```python\nresult = a + b\n```") == _artifact_candidate_fingerprint("```python\n# A renamed scenario\nresult=a+b\n```")
    assert _artifact_candidate_fingerprint("```python\nresult = a + b\n```") != _artifact_candidate_fingerprint("```python\nresult = a * b\n```")
    ordered = {
        "id": "ORDER-SUBSET", "objective": "workflow", "difficulty": "medium",
        "cognitive_type": "application", "question_type": "ordering", "ordering_mode": "subset",
        "stem": "Select and order the steps that prepare and validate the report. Use each step at most once.",
        "selection_instruction": "Select three steps and order them. Use each step once or not at all.",
        "select_count": 3,
        "options": {"A": "Delete the input", "B": "Publish before validation", "C": "Load the input",
                    "D": "Skip validation", "E": "Transform the rows", "F": "Validate the report"},
        "correct": ["C", "E", "F"], "rendered_correct": ["C", "E", "F"],
        "correct_explanation": "Load the data before transforming it, then validate the resulting report.",
        "wrong_explanations": {"A": "Deleting the input prevents transformation.",
                               "B": "Publishing before validation exposes unchecked results.",
                               "D": "Skipping validation omits the required check."},
        "links": ["lectures/workflow.md"],
    }
    assert not structure_codes(ordered)
    all_steps = copy.deepcopy(ordered)
    all_steps.update(ordering_mode="all", correct=list("ABCDEF"), rendered_correct=list("ABCDEF"),
                     select_count=6, wrong_explanations={})
    all_steps.pop("selection_instruction")
    assert not structure_codes(all_steps)
    for answer in ([], ["C"], ["C", "C", "F"], ["C", "X", "F"]):
        assert "invalid-correct" in structure_codes(ordered | {"correct": answer})
    assert "ordering-all-options-required" in structure_codes(ordered | {"ordering_mode": "all"})
    for mode in ("reuse", None, [], {}):
        assert "invalid-ordering-mode" in structure_codes(ordered | {"ordering_mode": mode})
    assert "selection-count-mismatch" in structure_codes(ordered | {"select_count": 2})
    assert "missing-selection-instruction" in structure_codes(ordered | {"selection_instruction": ""})
    assert "missing-wrong-explanation" in structure_codes(ordered | {"wrong_explanations": {}})
    assert "rendered-correct-mismatch" in structure_codes(ordered | {"rendered_correct": ["F", "E", "C"]})

    # Both algorithms calculate the total; actual operation counts select the best one.
    optimized = make_artifact_question("fewest_calls")
    assert validate(optimized) == ({"code"}, set())

    # Two different incorrect expressions may yield the same observed result.
    shared_result = make_artifact_question("total")
    expression = "sum(value > 0 for value in values)"
    assert eval(expression, {"values": [2, 3, 4]}) == 3 == len([2, 3, 4])
    code = f"```python\nresult = {expression}\n```"
    explanation = f"`{expression}` produces 3; it counts positive entries rather than totaling their values."
    shared_result["options"]["C"] = code
    shared_result["wrong_explanations"]["C"] = explanation
    shared_result["artifact_evidence"].append({"type": "code", "location": "option:C", "content": code,
                                               "decision_binding": "The predicate counts matching entries instead of summing values."})
    selection = shared_result["artifact_selection"]
    selection["decision_axes"][0]["option_values"]["C"] = expression
    selection["validation"]["candidate_results"]["C"] = "produces 3"
    selection["explanation_bindings"]["C"] = {"artifact_excerpt": expression, "result_excerpt": "produces 3",
                                                "explanation_excerpt": explanation}
    assert validate(shared_result) == ({"code"}, set())
    broken = copy.deepcopy(shared_result)
    broken["wrong_explanations"]["C"] = "The answer is unsuitable."
    assert "artifact-explanation-binding-not-visible" in validate(broken)[1]

    original = make_artifact_question("total")
    reskin = copy.deepcopy(original)
    reskin["id"] = "NEW-ID"
    scenario = reskin["artifact_selection"]["stem_contract"]["scenario"]
    for field in ("context", "expected_observation"):
        old = scenario[field]
        scenario[field] += " for contract distinct-alpha"
        reskin["stem"] = reskin["stem"].replace(old, scenario[field])
    assert validate(reskin) == ({"code"}, set())
    assert "artifact-scenario-contract-reused" in validate_policy([original, reskin], 2)
    # Reordering labels cannot make a new decision either.
    relabeled = copy.deepcopy(original)
    swap = {"A": "B", "B": "A"}
    relabeled["id"] = "RELABEL"
    relabeled["options"] = {swap[k]: v for k, v in original["options"].items()}
    relabeled["correct"] = "B"
    relabeled["wrong_explanations"] = {"A": original["wrong_explanations"]["B"]}
    for evidence in relabeled["artifact_evidence"]:
        evidence["location"] = "option:" + swap[evidence["location"].split(":")[1]]
    selection = relabeled["artifact_selection"]
    selection["decision_axes"][0]["option_values"] = {swap[k]: v for k, v in selection["decision_axes"][0]["option_values"].items()}
    selection["validation"]["validated_correct"] = ["B"]
    selection["validation"]["candidate_results"] = {swap[k]: v for k, v in selection["validation"]["candidate_results"].items()}
    selection["explanation_bindings"] = {swap[k]: v for k, v in selection["explanation_bindings"].items()}
    assert validate(relabeled) == ({"code"}, set())
    assert "artifact-scenario-contract-reused" in validate_policy([original, relabeled], 2)
    assert not validate_policy([original, make_artifact_question("filter")], 2)
    # The same alternatives can support a different decision, with a different
    # requirement and correctly rebound answer (total versus element count).
    counting = copy.deepcopy(original)
    counting.update(id="COUNT-INSTEAD-OF-TOTAL", correct="B")
    counting["stem"] = counting["stem"].replace("compute the total", "count the elements").replace("output is 9", "output is 3")
    counting["correct_explanation"] = "`len(values)` produces 3; it counts the input elements."
    counting["wrong_explanations"] = {"A": "`sum(values)` produces 9; it adds values instead of counting elements."}
    selection = counting["artifact_selection"]
    selection["requirement"] = "count the elements"
    selection["stem_contract"]["scenario"]["hard_constraints"] = ["count the elements"]
    selection["stem_contract"]["scenario"]["expected_observation"] = "the required output is 3"
    selection["validation"]["validated_correct"] = ["B"]
    selection["explanation_bindings"]["A"]["explanation_excerpt"] = counting["wrong_explanations"]["A"]
    selection["explanation_bindings"]["B"]["explanation_excerpt"] = counting["correct_explanation"]
    assert validate(counting) == ({"code"}, set())
    assert not validate_policy([original, counting], 2)
    # Final review still binds delivery fields; the workflow must finalize links first.
    assert question_hash(ordered) != question_hash(ordered | {"links": ["lectures/rebuilt.md"]})
    print("Question authoring contract tests: PASS (subset ordering, optimization, shared outcomes, reskins, final hashes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
