#!/usr/bin/env python3
"""Regression tests for the lecture completeness and prerequisite-closure gate."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from validate_learning_contract import REQUIRED_DIMENSIONS, _resolved_markdown_target, validate_manifest


def _unit(unit_id: str, kind: str, sequence: int, path: str, **identity: str) -> tuple[dict, list[str]]:
    lines: list[str] = []
    evidence: list[dict] = []
    for dimension in sorted(REQUIRED_DIMENSIONS[kind]):
        content = f"{unit_id} teaches {dimension} with a distinct learner-visible explanation and concrete technical evidence."
        lines.append(content)
        evidence.append({"path": path, "content": content, "dimensions": [dimension]})
    return (
        {
            "id": unit_id,
            "kind": kind,
            "sequence": sequence,
            "evidence": evidence,
            **identity,
        },
        lines,
    )


def _write_fixture(root: Path) -> tuple[Path, Path, Path, Path, dict]:
    units: list[dict] = []
    service_lines: list[str] = []
    supporting_lines: list[str] = []
    specs = (
        ("foundation.cloud", "foundation", {"title": "Cloud foundations"}),
        ("service.object-storage", "service", {"subject": "Object Storage"}),
        ("artifact.policy", "artifact", {"artifact_type": "policy-json"}),
        ("integration.web-path", "integration", {"pattern_id": "web-request-path"}),
    )
    for index, (unit_id, kind, identity) in enumerate(specs, start=1):
        unit, lines = _unit(unit_id, kind, index, "lectures.md", **identity)
        if kind == "service":
            unit["lecture_id"] = "lecture.cloud-storage"
            service_lines.extend(lines)
        else:
            supporting_lines.extend(lines)
        units.append(unit)

    curriculum_unit, curriculum_lines = _unit(
        "curriculum.object-storage",
        "service",
        1,
        "services.md",
        subject="Object Storage",
    )
    curriculum_unit["path"] = "services.md"
    entry_name = "Amazon Elastic Kubernetes Service (Amazon EKS)"
    entry_alias = "EKS"
    entry_anchor = "service-object-storage"
    entry_lines: list[str] = []
    entry_evidence: list[dict] = []
    for dimension in sorted(REQUIRED_DIMENSIONS["service"]):
        content = (
            f"{entry_name} teaches {dimension} through its own request path, state owner, control, "
            "failure signal, operational evidence, and architecture decision rather than a family-level placeholder."
        )
        entry_lines.append(content)
        entry_evidence.append({"path": "services.md", "content": content, "dimensions": [dimension]})
    index_link = f"[{entry_name}](services.md#{entry_anchor})"
    (root / "services.md").write_text(
        "# Comprehensive Services\n\n"
        + index_link
        + "\n\n"
        + "\n\n".join(curriculum_lines)
        + f'\n\n<a id="{entry_anchor}"></a>\n\n## {entry_name}\n\n'
        + "\n\n".join(entry_lines),
        encoding="utf-8",
    )
    service_entry = {
        "id": "service-entry.object-storage",
        "name": entry_name,
        "aliases": [entry_name, "Amazon EKS", entry_alias],
        "kind": "service",
        "curriculum_unit_id": "curriculum.object-storage",
        "path": "services.md",
        "heading": f"## {entry_name}",
        "anchor": entry_anchor,
        "sequence": 2,
        "index_evidence": {"path": "services.md", "content": index_link},
        "evidence": entry_evidence,
    }
    curriculum_unit["service_entry_ids"] = [service_entry["id"]]
    service_entry_jsonl = root / "service-entries.jsonl"
    service_entry_jsonl.write_text(
        json.dumps({key: service_entry[key] for key in ("id", "name", "aliases", "kind", "curriculum_unit_id", "path", "anchor")}) + "\n",
        encoding="utf-8",
    )

    service_mention_link = f"[{entry_alias}](services.md#{entry_anchor})"
    service_section = (
        "## Services and major features\n\n"
        + f"The {service_mention_link} entry is linked from this lecture scenario.\n\n"
        + "\n\n".join(service_lines)
    )
    outside_service_evidence = (
        "This Object Storage purpose statement is visible only in the later design appendix and is outside the required Service section."
    )
    lecture_text = "\n\n".join(
        [
            "# Cloud storage lecture",
            "This lecture introduces the scenario before teaching its product services.",
            service_section,
            "## Foundations, artifacts, and integrations",
            *supporting_lines,
            "## Design appendix",
            outside_service_evidence,
        ]
    )
    (root / "lectures.md").write_text(lecture_text, encoding="utf-8")
    lecture_jsonl = root / "lectures.jsonl"
    lecture_jsonl.write_text(
        json.dumps({"id": "lecture.cloud-storage", "path": "lectures.md"}) + "\n",
        encoding="utf-8",
    )
    source_marker = "Q-001 source marker for the canonical assessment."
    question_text = "\n\n".join(
        [
            "# Questions",
            source_marker,
            f"Stem: Which {service_mention_link} design satisfies the requirement?",
            f"- A. Keep the {service_mention_link} design.",
            f"- B. Replace the {service_mention_link} design.",
            f"Correct explanation: The {service_mention_link} owns the required boundary.",
            f"Wrong explanation: The alternative misuses the {service_mention_link} boundary.",
            f"Formal name: [{entry_name}](services.md#{entry_anchor}) uses longest-alias matching.",
            "Code is protected: `OSS` and the URL https://example.test/OSS stay unlinked.",
            "```text\nOSS\n```",
        ]
    )
    (root / "questions.md").write_text(question_text, encoding="utf-8")
    question_jsonl = root / "questions.jsonl"
    question_jsonl.write_text(json.dumps({"id": "Q-001"}) + "\n", encoding="utf-8")

    navigation_categories = [
        {
            "id": "category.services",
            "kind": "service",
            "label": "Services",
            "sequence": 10,
            "landing_path": "services.md",
            "page_paths": ["services.md"],
            "parent_id": None,
        },
        {
            "id": "category.lectures",
            "kind": "lecture",
            "label": "Lectures",
            "sequence": 20,
            "landing_path": "lectures.md",
            "page_paths": ["lectures.md"],
            "parent_id": None,
        },
        {
            "id": "category.questions",
            "kind": "question",
            "label": "Questions",
            "sequence": 30,
            "landing_path": "questions.md",
            "page_paths": ["questions.md"],
            "parent_id": None,
        },
    ]
    navigation_jsonl = root / "navigation.jsonl"
    navigation_jsonl.write_text(
        "\n".join(json.dumps(value) for value in navigation_categories) + "\n",
        encoding="utf-8",
    )

    requirements = [unit["id"] for unit in units]
    manifest = {
        "version": 1,
        "course": {"id": "fixture-course"},
        "entry_contract": {
            "assumptions": [
                {
                    "id": "entry.reading",
                    "description": "Can read ordinary technical prose.",
                    "basis": "general_it",
                    "rationale": "The course itself teaches every assessed product concept.",
                }
            ],
            "assumed_certifications": [],
        },
        "lecture_policy": {"expected_count": 1, "require_service_sections": True},
        "service_curriculum_policy": {
            "require_top_level_category": True,
            "require_named_service_entries": True,
            "require_service_mention_links": True,
            "service_category_id": "category.services",
            "expected_navigation_category_count": 3,
            "expected_service_count": 1,
            "expected_named_service_count": 1,
            "minimum_named_service_profile_words": 80,
        },
        "navigation_categories": navigation_categories,
        "service_curriculum": [curriculum_unit],
        "service_entries": [service_entry],
        "lectures": [
            {
                "id": "lecture.cloud-storage",
                "path": "lectures.md",
                "sequence": 1,
                "service_section": {
                    "heading": "## Services and major features",
                    "service_unit_ids": ["service.object-storage"],
                    "evidence": {"path": "lectures.md", "content": service_section},
                },
            }
        ],
        "learning_units": units,
        "assessment_policy": {"expected_count": 1},
        "assessments": [
            {
                "id": "Q-001",
                "sequence": 100,
                "source": {"path": "questions.md", "content": source_marker},
                "requirements": requirements,
                "lecture_links": requirements,
                "services": ["Object Storage"],
                "artifact_types": ["policy-json"],
                "integration_patterns": ["web-request-path"],
                "service_curriculum_links": ["curriculum.object-storage"],
                "named_services": [entry_name],
                "service_entry_links": [service_entry["id"]],
            }
        ],
    }
    manifest["learning_units"][1]["curriculum_unit_id"] = "curriculum.object-storage"
    question_jsonl.write_text(json.dumps({
        "id": "Q-001",
        "stem": f"Which {entry_alias} design satisfies the requirement?",
        "options": {"A": f"Keep the {entry_alias} design.", "B": f"Replace the {entry_alias} design."},
        "correct_explanation": f"The {entry_alias} owns the required boundary.",
        "wrong_explanations": {"B": f"The alternative misuses the {entry_alias} boundary."},
        "learning_requirements": {
            key: manifest["assessments"][0][key]
            for key in ("requirements", "services", "artifact_types", "integration_patterns", "named_services")
        },
    }) + "\n", encoding="utf-8")
    manifest_path = root / "learning-contract.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["_fixture_outside_service_evidence"] = outside_service_evidence
    manifest["_fixture_service_alias"] = entry_alias
    return manifest_path, question_jsonl, lecture_jsonl, navigation_jsonl, manifest


def _codes(
    manifest: dict,
    root: Path,
    inventory: Path,
    lecture_inventory: Path | None,
    *,
    omit_navigation_inventory: bool = False,
) -> set[str]:
    path = root / "case.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {
        finding.code
        for finding in validate_manifest(
            path,
            root,
            [inventory],
            require_assessment_inventory=True,
            lecture_jsonl=[] if lecture_inventory is None else [lecture_inventory],
            require_service_sections=True,
            navigation_jsonl=[] if omit_navigation_inventory else [root / "navigation.jsonl"],
            require_service_curriculum=True,
            service_entry_jsonl=[root / "service-entries.jsonl"],
            require_named_service_entries=True,
            require_service_mention_links=True,
        )
    }


def main() -> int:
    assert _resolved_markdown_target(
        "questions/domain-1.md",
        "../services/compute-containers.md#service-amazon-eks",
    ) == ("services/compute-containers.md", "service-amazon-eks")
    assert _resolved_markdown_target(
        "lectures/domain/task.md",
        "../../services/compute-containers.md#service-amazon-eks",
    ) == ("services/compute-containers.md", "service-amazon-eks")
    assert _resolved_markdown_target(
        "questions/domain-1.md",
        "https://docs.example.test/eks",
    ) is None
    with TemporaryDirectory() as directory:
        root = Path(directory)
        manifest_path, inventory, lecture_inventory, navigation_inventory, valid = _write_fixture(root)
        outside_service_evidence = valid.pop("_fixture_outside_service_evidence")
        service_alias = valid.pop("_fixture_service_alias")
        original_entry_name = valid["service_entries"][0]["name"]
        manifest_path.write_text(json.dumps(valid, indent=2), encoding="utf-8")
        findings = validate_manifest(
            manifest_path,
            root,
            [inventory],
            require_assessment_inventory=True,
            lecture_jsonl=[lecture_inventory],
            require_service_sections=True,
            navigation_jsonl=[navigation_inventory],
            require_service_curriculum=True,
            service_entry_jsonl=[root / "service-entries.jsonl"],
            require_named_service_entries=True,
            require_service_mention_links=True,
        )
        assert not findings, findings

        omitted = copy.deepcopy(valid)
        omitted["assessments"][0]["requirements"] = ["entry.reading"]
        for key in ("lecture_links", "services", "artifact_types", "integration_patterns",
                    "service_curriculum_links", "named_services", "service_entry_links"):
            omitted["assessments"][0][key] = []
        assert "canonical-learning-requirements-mismatch" in _codes(omitted, root, inventory, lecture_inventory)

        canonical_text = inventory.read_text(encoding="utf-8")
        canonical = json.loads(canonical_text)
        both_omit = copy.deepcopy(canonical)
        both_omit["learning_requirements"] = {
            key: omitted["assessments"][0][key] for key in canonical["learning_requirements"]
        }
        inventory.write_text(json.dumps(both_omit) + "\n", encoding="utf-8")
        assert "canonical-service-mention-unbound" in _codes(omitted, root, inventory, lecture_inventory)
        # Observe each question surface, but protect code and URL text.
        for field in ("stem", "options", "correct_explanation", "wrong_explanations"):
            surface = copy.deepcopy(both_omit)
            surface.update(stem="A workload needs a design.", options={"A": "Keep it", "B": "Replace it"},
                           correct_explanation="This meets the requirement.", wrong_explanations={"B": "This changes the boundary."})
            surface[field] = canonical[field]
            inventory.write_text(json.dumps(surface) + "\n", encoding="utf-8")
            assert "canonical-service-mention-unbound" in _codes(omitted, root, inventory, lecture_inventory), field
        protected = copy.deepcopy(surface)
        protected["wrong_explanations"] = {"B": "Inspect `EKS` and https://example.test/EKS only."}
        inventory.write_text(json.dumps(protected) + "\n", encoding="utf-8")
        assert "canonical-service-mention-unbound" not in _codes(omitted, root, inventory, lecture_inventory)
        inventory.write_text('{"id":"Q-001"}\n', encoding="utf-8")
        assert "missing-canonical-learning-requirements" in _codes(valid, root, inventory, lecture_inventory)
        inventory.write_text(canonical_text, encoding="utf-8")

        legacy_compatible = copy.deepcopy(valid)
        legacy_compatible.pop("lecture_policy")
        legacy_compatible.pop("lectures")
        legacy_compatible.pop("service_curriculum_policy")
        legacy_compatible.pop("navigation_categories")
        legacy_compatible.pop("service_curriculum")
        legacy_compatible.pop("service_entries")
        legacy_compatible["learning_units"][1].pop("lecture_id")
        legacy_compatible["learning_units"][1].pop("curriculum_unit_id")
        legacy_compatible["assessments"][0].pop("service_curriculum_links")
        legacy_compatible["assessments"][0].pop("named_services")
        legacy_compatible["assessments"][0].pop("service_entry_links")
        legacy_path = root / "legacy-compatible.json"
        legacy_path.write_text(json.dumps(legacy_compatible, indent=2), encoding="utf-8")
        legacy_findings = validate_manifest(
            legacy_path,
            root,
            [inventory],
            require_assessment_inventory=True,
        )
        assert not legacy_findings, legacy_findings

        missing_dimension = copy.deepcopy(valid)
        missing_dimension["learning_units"][1]["evidence"] = missing_dimension["learning_units"][1]["evidence"][:-1]
        assert "missing-learning-dimensions" in _codes(missing_dimension, root, inventory, lecture_inventory)

        missing_artifact_dimension = copy.deepcopy(valid)
        missing_artifact_dimension["learning_units"][2]["evidence"] = missing_artifact_dimension["learning_units"][2]["evidence"][:-1]
        assert "missing-learning-dimensions" in _codes(missing_artifact_dimension, root, inventory, lecture_inventory)

        missing_integration_dimension = copy.deepcopy(valid)
        missing_integration_dimension["learning_units"][3]["evidence"] = missing_integration_dimension["learning_units"][3]["evidence"][:-1]
        assert "missing-learning-dimensions" in _codes(missing_integration_dimension, root, inventory, lecture_inventory)

        late_unit = copy.deepcopy(valid)
        late_unit["learning_units"][1]["sequence"] = 100
        assert "learning-unit-not-prior" in _codes(late_unit, root, inventory, lecture_inventory)

        hidden_evidence = copy.deepcopy(valid)
        hidden_evidence["learning_units"][2]["evidence"][0]["content"] = "This exact artifact explanation is not visible to the learner."
        assert "evidence-not-learner-visible" in _codes(hidden_evidence, root, inventory, lecture_inventory)

        reused_evidence = copy.deepcopy(valid)
        reused_evidence["learning_units"][1]["evidence"][1]["content"] = reused_evidence["learning_units"][1]["evidence"][0]["content"]
        assert "reused-learning-evidence" in _codes(reused_evidence, root, inventory, lecture_inventory)

        missing_artifact_binding = copy.deepcopy(valid)
        missing_artifact_binding["assessments"][0]["requirements"].remove("artifact.policy")
        assert "unbound-assessed-artifact" in _codes(missing_artifact_binding, root, inventory, lecture_inventory)

        assumed_certification = copy.deepcopy(valid)
        assumed_certification["entry_contract"]["assumed_certifications"] = [
            {"name": "Lower-level certification", "user_approved": False}
        ]
        assert "unapproved-assumed-certification" in _codes(assumed_certification, root, inventory, lecture_inventory)

        incomplete_inventory = copy.deepcopy(valid)
        incomplete_inventory["assessments"][0]["id"] = "Q-OTHER"
        incomplete_inventory["assessments"][0]["source"]["content"] = "Q-001 source marker for the canonical assessment."
        assert "assessment-inventory-mismatch" in _codes(incomplete_inventory, root, inventory, lecture_inventory)

        missing_service_section = copy.deepcopy(valid)
        missing_service_section["lectures"][0]["service_section"]["heading"] = "## Undeclared services"
        assert "missing-service-section" in _codes(missing_service_section, root, inventory, lecture_inventory)

        service_evidence_outside_section = copy.deepcopy(valid)
        service_evidence_outside_section["learning_units"][1]["evidence"][0]["content"] = outside_service_evidence
        assert "service-evidence-outside-service-section" in _codes(
            service_evidence_outside_section, root, inventory, lecture_inventory
        )

        unlisted_service_unit = copy.deepcopy(valid)
        unlisted_service_unit["lectures"][0]["service_section"]["service_unit_ids"] = []
        unlisted_codes = _codes(unlisted_service_unit, root, inventory, lecture_inventory)
        assert "empty-service-section" in unlisted_codes
        assert "service-unit-not-listed-in-section" in unlisted_codes

        assert "lecture-inventory-required" in _codes(valid, root, inventory, None)

        incomplete_lecture_inventory = root / "lectures-incomplete.jsonl"
        incomplete_lecture_inventory.write_text("", encoding="utf-8")
        assert "lecture-inventory-mismatch" in _codes(valid, root, inventory, incomplete_lecture_inventory)

        missing_service_category = copy.deepcopy(valid)
        missing_service_category["navigation_categories"] = [
            value
            for value in missing_service_category["navigation_categories"]
            if value["id"] != "category.services"
        ]
        assert "service-category-required" in _codes(
            missing_service_category, root, inventory, lecture_inventory
        )

        late_service_category = copy.deepcopy(valid)
        late_service_category["navigation_categories"][0]["sequence"] = 25
        assert "service-category-not-upper" in _codes(
            late_service_category, root, inventory, lecture_inventory
        )

        nested_service_category = copy.deepcopy(valid)
        nested_service_category["navigation_categories"][0]["parent_id"] = "category.lectures"
        assert "service-category-not-top-level" in _codes(
            nested_service_category, root, inventory, lecture_inventory
        )

        missing_curriculum_dimension = copy.deepcopy(valid)
        missing_curriculum_dimension["service_curriculum"][0]["evidence"] = (
            missing_curriculum_dimension["service_curriculum"][0]["evidence"][:-1]
        )
        assert "missing-service-curriculum-dimensions" in _codes(
            missing_curriculum_dimension, root, inventory, lecture_inventory
        )

        hidden_curriculum_evidence = copy.deepcopy(valid)
        hidden_curriculum_evidence["service_curriculum"][0]["evidence"][0]["content"] = (
            "This comprehensive Service explanation is declared but is not visible on the curriculum page."
        )
        assert "evidence-not-learner-visible" in _codes(
            hidden_curriculum_evidence, root, inventory, lecture_inventory
        )

        curriculum_outside_category = copy.deepcopy(valid)
        curriculum_outside_category["service_curriculum"][0]["path"] = "lectures.md"
        assert "service-curriculum-outside-category" in _codes(
            curriculum_outside_category, root, inventory, lecture_inventory
        )

        unbound_assessed_curriculum = copy.deepcopy(valid)
        unbound_assessed_curriculum["assessments"][0]["service_curriculum_links"] = []
        assert "unbound-assessed-service-curriculum" in _codes(
            unbound_assessed_curriculum, root, inventory, lecture_inventory
        )

        missing_local_curriculum_binding = copy.deepcopy(valid)
        missing_local_curriculum_binding["learning_units"][1].pop("curriculum_unit_id")
        assert "missing-service-curriculum-binding" in _codes(
            missing_local_curriculum_binding, root, inventory, lecture_inventory
        )

        assert "navigation-inventory-required" in _codes(
            valid,
            root,
            inventory,
            lecture_inventory,
            omit_navigation_inventory=True,
        )

        missing_service_entry = copy.deepcopy(valid)
        missing_service_entry["service_entries"] = []
        assert "named-service-count-mismatch" in _codes(
            missing_service_entry, root, inventory, lecture_inventory
        )

        shallow_service_entry = copy.deepcopy(valid)
        shallow_service_entry["service_entries"][0]["evidence"] = shallow_service_entry["service_entries"][0]["evidence"][:1]
        shallow_codes = _codes(shallow_service_entry, root, inventory, lecture_inventory)
        assert "service-entry-too-shallow" in shallow_codes
        assert "missing-service-entry-dimensions" in shallow_codes

        missing_service_entry_anchor = copy.deepcopy(valid)
        missing_service_entry_anchor["service_entries"][0]["anchor"] = "service-missing-anchor"
        assert "missing-service-entry-anchor" in _codes(
            missing_service_entry_anchor, root, inventory, lecture_inventory
        )

        unbound_named_service = copy.deepcopy(valid)
        unbound_named_service["assessments"][0]["service_entry_links"] = []
        assert "assessment-service-entry-binding-mismatch" in _codes(
            unbound_named_service, root, inventory, lecture_inventory
        )

        missing_service_aliases = copy.deepcopy(valid)
        missing_service_aliases["service_entries"][0].pop("aliases")
        assert "missing-service-entry-aliases" in _codes(
            missing_service_aliases, root, inventory, lecture_inventory
        )

        formal_name_not_alias = copy.deepcopy(valid)
        formal_name_not_alias["service_entries"][0]["aliases"] = ["Amazon EKS", service_alias]
        assert "service-entry-formal-name-not-alias" in _codes(
            formal_name_not_alias, root, inventory, lecture_inventory
        )

        missing_derived_alias = copy.deepcopy(valid)
        missing_derived_alias["service_entries"][0]["aliases"] = [original_entry_name]
        assert "missing-derived-service-entry-alias" in _codes(
            missing_derived_alias, root, inventory, lecture_inventory
        )

        duplicate_service_alias = copy.deepcopy(valid)
        duplicate_service_alias["service_entries"][0]["aliases"].append(service_alias.lower())
        assert "duplicate-service-entry-alias" in _codes(
            duplicate_service_alias, root, inventory, lecture_inventory
        )

        ambiguous_service_alias = copy.deepcopy(valid)
        ambiguous_entry = copy.deepcopy(ambiguous_service_alias["service_entries"][0])
        ambiguous_entry["id"] = "service-entry.archive-storage"
        ambiguous_entry["name"] = "Archive Storage Service"
        ambiguous_entry["aliases"] = ["Archive Storage Service", service_alias]
        ambiguous_entry["anchor"] = "service-archive-storage"
        ambiguous_entry["heading"] = "## Archive Storage Service"
        ambiguous_service_alias["service_entries"].append(ambiguous_entry)
        ambiguous_service_alias["service_curriculum_policy"]["expected_named_service_count"] = 2
        assert "ambiguous-service-entry-alias" in _codes(
            ambiguous_service_alias, root, inventory, lecture_inventory
        )

        original_lecture_text = (root / "lectures.md").read_text(encoding="utf-8")
        (root / "lectures.md").write_text(
            original_lecture_text + f"\n\nBare lecture mention: {service_alias} must be linked.",
            encoding="utf-8",
        )
        assert "unlinked-service-mention" in _codes(valid, root, inventory, lecture_inventory)
        (root / "lectures.md").write_text(original_lecture_text, encoding="utf-8")

        original_question_text = (root / "questions.md").read_text(encoding="utf-8")
        wrong_landing_link = original_question_text.replace(
            f"[{service_alias}](services.md#service-object-storage)",
            f"[{service_alias}](services.md)",
            1,
        )
        (root / "questions.md").write_text(wrong_landing_link, encoding="utf-8")
        assert "wrong-service-mention-link" in _codes(valid, root, inventory, lecture_inventory)

        wrong_external_link = original_question_text.replace(
            f"[{service_alias}](services.md#service-object-storage)",
            f"[{service_alias}](https://docs.example.test/oss)",
            1,
        )
        (root / "questions.md").write_text(wrong_external_link, encoding="utf-8")
        assert "wrong-service-mention-link" in _codes(valid, root, inventory, lecture_inventory)

        unlinked_option = original_question_text.replace(
            f"- B. Replace the [{service_alias}](services.md#service-object-storage) design.",
            f"- B. Replace the {service_alias} design.",
        )
        (root / "questions.md").write_text(unlinked_option, encoding="utf-8")
        assert "unlinked-service-mention" in _codes(valid, root, inventory, lecture_inventory)
        (root / "questions.md").write_text(original_question_text, encoding="utf-8")

        original_services = (root / "services.md").read_text(encoding="utf-8")
        original_inventory = (root / "service-entries.jsonl").read_text(encoding="utf-8")
        generic_name_substitution = copy.deepcopy(valid)
        second = copy.deepcopy(generic_name_substitution["service_entries"][0])
        second["id"] = "service-entry.archive-storage"
        second["name"] = "Archive Storage Service"
        second["aliases"] = ["Archive Storage Service", "ASS"]
        second["anchor"] = "service-archive-storage"
        second["heading"] = "## Archive Storage Service"
        second["sequence"] = 3
        second["index_evidence"]["content"] = "[Archive Storage Service](services.md#service-archive-storage)"
        for evidence in second["evidence"]:
            evidence["content"] = evidence["content"].replace(original_entry_name, "Archive Storage Service")
        generic_name_substitution["service_entries"].append(second)
        generic_name_substitution["service_curriculum"][0]["service_entry_ids"].append(second["id"])
        generic_name_substitution["service_curriculum_policy"]["expected_named_service_count"] = 2
        second_section = (
            "\n\n[Archive Storage Service](services.md#service-archive-storage)"
            '\n\n<a id="service-archive-storage"></a>\n\n## Archive Storage Service\n\n'
            + "\n\n".join(str(value["content"]) for value in second["evidence"])
        )
        (root / "services.md").write_text(original_services + second_section, encoding="utf-8")
        inventory_rows = [
            {key: value[key] for key in ("id", "name", "aliases", "kind", "curriculum_unit_id", "path", "anchor")}
            for value in generic_name_substitution["service_entries"]
        ]
        (root / "service-entries.jsonl").write_text(
            "".join(json.dumps(value) + "\n" for value in inventory_rows), encoding="utf-8"
        )
        assert "generic-name-substitution-service-entry" in _codes(
            generic_name_substitution, root, inventory, lecture_inventory
        )
        (root / "services.md").write_text(original_services, encoding="utf-8")
        (root / "service-entries.jsonl").write_text(original_inventory, encoding="utf-8")

    print("Learning contract regression tests: PASS (strict success, legacy compatibility, named-Service depth, and Service-mention link fixtures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
