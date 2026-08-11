#!/usr/bin/env python3
"""Validate lecture completeness and assessment prerequisite closure."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REQUIRED_DIMENSIONS: dict[str, set[str]] = {
    "foundation": {
        "plain_language_definition",
        "mechanism",
        "worked_example",
        "failure_or_misconception",
    },
    "service": {
        "purpose",
        "components",
        "mechanism",
        "configuration",
        "security",
        "reliability_and_failure",
        "observability",
        "cost_and_performance",
        "alternatives",
        "integrations",
        "worked_example",
    },
    "artifact": {
        "structure",
        "field_meaning",
        "normal_example",
        "failure_example",
        "decision_use",
    },
    "integration": {
        "service_roles",
        "request_or_event_flow",
        "identity_and_policy",
        "data_or_state_flow",
        "failure_and_recovery",
        "observability",
    },
}

ALLOWED_ASSUMPTION_BASES = {"general_it", "user_confirmed", "official_required"}
SERVICE_DEPENDENT_NAVIGATION_KINDS = {"lecture", "question", "mock"}
MARKDOWN_HEADING = re.compile(r"^(#{1,6})[ \t]+\S")
STABLE_ANCHOR = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MARKDOWN_LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\(([^)\n]+)\)")
MARKDOWN_IMAGE = re.compile(r"!\[[^\]\n]*\]\([^)\n]+\)")
HTML_LINK = re.compile(
    r"<a\b[^>]*\bhref=[\"']([^\"']+)[\"'][^>]*>([^<]+)</a>",
    flags=re.IGNORECASE,
)
HTML_TAG = re.compile(r"<[^>\n]+>")
RAW_URL = re.compile(r"https?://[^\s<>()]+", flags=re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    return data


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _resolve_content_path(root: Path, relative: Any) -> Path | None:
    if not _nonempty_string(relative):
        return None
    candidate = (root / str(relative)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _validate_exact_slice(
    *,
    owner: str,
    evidence: Any,
    root: Path,
    file_cache: dict[Path, str],
    findings: list[Finding],
    minimum_length: int,
) -> bool:
    if not isinstance(evidence, dict):
        findings.append(Finding("invalid-evidence", f"{owner}: evidence must be an object"))
        return False

    path = _resolve_content_path(root, evidence.get("path"))
    content = evidence.get("content")
    if path is None:
        findings.append(Finding("invalid-evidence-path", f"{owner}: evidence path is missing or outside content root"))
        return False
    if not _nonempty_string(content) or len(str(content).strip()) < minimum_length:
        findings.append(Finding("evidence-too-short", f"{owner}: exact evidence is missing or shorter than {minimum_length} characters"))
        return False
    if not path.is_file():
        findings.append(Finding("missing-evidence-file", f"{owner}: learner-visible file does not exist: {path}"))
        return False

    if path not in file_cache:
        file_cache[path] = _normalize(path.read_text(encoding="utf-8-sig"))
    if _normalize(str(content)) not in file_cache[path]:
        findings.append(Finding("evidence-not-learner-visible", f"{owner}: exact evidence is not present in {path}"))
        return False
    return True


def _read_question_ids(paths: Iterable[Path], findings: list[Finding]) -> set[str]:
    ids: set[str] = set()
    for path in paths:
        if not path.is_file():
            findings.append(Finding("missing-question-inventory", f"question inventory does not exist: {path}"))
            continue
        for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if not raw.strip():
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                findings.append(Finding("invalid-question-jsonl", f"{path}:{line_number}: {exc}"))
                continue
            question_id = item.get("id") if isinstance(item, dict) else None
            if not _nonempty_string(question_id):
                findings.append(Finding("missing-question-id", f"{path}:{line_number}: missing string id"))
                continue
            if question_id in ids:
                findings.append(Finding("duplicate-question-id", f"duplicate question id in inventory: {question_id}"))
            ids.add(str(question_id))
    return ids


def _read_lecture_inventory(paths: Iterable[Path], findings: list[Finding]) -> dict[str, str]:
    lectures: dict[str, str] = {}
    for path in paths:
        if not path.is_file():
            findings.append(Finding("missing-lecture-inventory", f"lecture inventory does not exist: {path}"))
            continue
        for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if not raw.strip():
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                findings.append(Finding("invalid-lecture-jsonl", f"{path}:{line_number}: {exc}"))
                continue
            lecture_id = item.get("id") if isinstance(item, dict) else None
            lecture_path = item.get("path") if isinstance(item, dict) else None
            if not _nonempty_string(lecture_id) or not _nonempty_string(lecture_path):
                findings.append(Finding("invalid-lecture-inventory-entry", f"{path}:{line_number}: string id and path are required"))
                continue
            lecture_id = str(lecture_id)
            if lecture_id in lectures:
                findings.append(Finding("duplicate-lecture-id", f"duplicate lecture id in inventory: {lecture_id}"))
            lectures[lecture_id] = str(lecture_path).replace("\\", "/")
    return lectures


def _navigation_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(item.get("id", "")),
        "kind": str(item.get("kind", "")),
        "label": str(item.get("label", "")),
        "sequence": item.get("sequence"),
        "landing_path": str(item.get("landing_path", "")).replace("\\", "/"),
        "page_paths": sorted(str(value).replace("\\", "/") for value in _list(item.get("page_paths"))),
        "parent_id": item.get("parent_id"),
    }


def _read_navigation_inventory(paths: Iterable[Path], findings: list[Finding]) -> dict[str, dict[str, Any]]:
    categories: dict[str, dict[str, Any]] = {}
    for path in paths:
        if not path.is_file():
            findings.append(Finding("missing-navigation-inventory", f"navigation inventory does not exist: {path}"))
            continue
        for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if not raw.strip():
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                findings.append(Finding("invalid-navigation-jsonl", f"{path}:{line_number}: {exc}"))
                continue
            if not isinstance(item, dict) or not _nonempty_string(item.get("id")):
                findings.append(Finding("invalid-navigation-inventory-entry", f"{path}:{line_number}: string id is required"))
                continue
            category_id = str(item["id"])
            if category_id in categories:
                findings.append(Finding("duplicate-navigation-category", f"duplicate category id in inventory: {category_id}"))
            categories[category_id] = _navigation_row(item)
    return categories


def _service_entry_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(item.get("id", "")),
        "name": str(item.get("name", "")),
        "kind": str(item.get("kind", "")),
        "curriculum_unit_id": str(item.get("curriculum_unit_id", "")),
        "path": str(item.get("path", "")).replace("\\", "/"),
        "anchor": str(item.get("anchor", "")),
        "aliases": sorted(str(value) for value in _list(item.get("aliases"))),
    }


def _read_service_entry_inventory(paths: Iterable[Path], findings: list[Finding]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for path in paths:
        if not path.is_file():
            findings.append(Finding("missing-service-entry-inventory", f"Service-entry inventory does not exist: {path}"))
            continue
        for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if not raw.strip():
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                findings.append(Finding("invalid-service-entry-jsonl", f"{path}:{line_number}: {exc}"))
                continue
            if not isinstance(item, dict) or not _nonempty_string(item.get("id")):
                findings.append(Finding("invalid-service-entry-inventory-entry", f"{path}:{line_number}: string id is required"))
                continue
            row = _service_entry_row(item)
            entry_id = row["id"]
            if entry_id in entries:
                findings.append(Finding("duplicate-service-entry-inventory-id", f"duplicate Service-entry id: {entry_id}"))
            entries[entry_id] = row
    return entries


def _mask_span(mask: list[bool], start: int, end: int) -> None:
    for index in range(max(0, start), min(len(mask), end)):
        mask[index] = True


def _markdown_prose_map(text: str) -> tuple[list[bool], list[tuple[int, int, str]]]:
    """Return excluded character positions and learner-visible link-label spans."""

    mask = [False] * len(text)
    links: list[tuple[int, int, str]] = []

    offset = 0
    fence_character: str | None = None
    fence_length = 0
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip(" ")
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if fence_character is None and marker is not None:
            token = marker.group(1)
            fence_character = token[0]
            fence_length = len(token)
            _mask_span(mask, offset, offset + len(line))
        elif fence_character is not None:
            _mask_span(mask, offset, offset + len(line))
            closing = re.match(rf"{re.escape(fence_character)}{{{fence_length},}}", stripped)
            if closing is not None:
                fence_character = None
                fence_length = 0
        offset += len(line)

    index = 0
    while index < len(text):
        if mask[index] or text[index] != "`":
            index += 1
            continue
        run_end = index + 1
        while run_end < len(text) and text[run_end] == "`":
            run_end += 1
        token = text[index:run_end]
        closing = text.find(token, run_end)
        if closing < 0:
            index = run_end
            continue
        _mask_span(mask, index, closing + len(token))
        index = closing + len(token)

    for match in MARKDOWN_IMAGE.finditer(text):
        if not any(mask[match.start():match.end()]):
            _mask_span(mask, match.start(), match.end())

    for match in MARKDOWN_LINK.finditer(text):
        if any(mask[match.start():match.end()]):
            continue
        links.append((match.start(1), match.end(1), match.group(2).strip()))
        _mask_span(mask, match.start(2), match.end(2))

    for match in HTML_LINK.finditer(text):
        if any(mask[match.start():match.end()]):
            continue
        links.append((match.start(2), match.end(2), match.group(1).strip()))
        _mask_span(mask, match.start(), match.start(2))
        _mask_span(mask, match.end(2), match.end())

    for pattern in (HTML_TAG, RAW_URL):
        for match in pattern.finditer(text):
            if not any(mask[match.start():match.end()]):
                _mask_span(mask, match.start(), match.end())

    return mask, links


def _resolved_markdown_target(surface_path: str, target: str) -> tuple[str, str] | None:
    candidate = target.strip()
    if candidate.startswith("<") and candidate.endswith(">"):
        candidate = candidate[1:-1].strip()
    if not candidate or re.match(r"^[a-z][a-z0-9+.-]*:", candidate, flags=re.IGNORECASE) or candidate.startswith("//"):
        return None
    if " " in candidate or "\t" in candidate:
        candidate = candidate.split()[0]
    path_part, separator, fragment = candidate.partition("#")
    if not separator or not fragment or "?" in path_part:
        return None
    if not path_part:
        resolved_path = surface_path
    elif path_part.startswith("/"):
        resolved_path = posixpath.normpath(path_part.lstrip("/"))
    else:
        resolved_path = posixpath.normpath(
            posixpath.join(posixpath.dirname(surface_path), path_part.replace("\\", "/"))
        )
    return resolved_path, fragment


def _validate_service_mentions(
    *,
    surface_path: str,
    text: str,
    alias_to_entry: dict[str, str],
    entries_by_id: dict[str, dict[str, Any]],
    findings: list[Finding],
) -> None:
    if not alias_to_entry:
        return
    mask, links = _markdown_prose_map(text)
    aliases = sorted(alias_to_entry, key=lambda value: (-len(value), value))
    pattern = re.compile(
        rf"(?<![\w])(?:{'|'.join(re.escape(alias) for alias in aliases)})(?![\w])",
        flags=re.UNICODE,
    )
    for match in pattern.finditer(text):
        if any(mask[match.start():match.end()]):
            continue
        alias = match.group(0)
        entry_id = alias_to_entry[alias]
        containing_links = [
            target
            for label_start, label_end, target in links
            if label_start <= match.start() and match.end() <= label_end
        ]
        if not containing_links:
            findings.append(
                Finding(
                    "unlinked-service-mention",
                    f"{surface_path}: learner-visible Service alias {alias!r} is not linked to {entry_id}",
                )
            )
            continue
        entry = entries_by_id.get(entry_id, {})
        expected = (
            str(entry.get("path", "")).replace("\\", "/"),
            str(entry.get("anchor", "")),
        )
        resolved = _resolved_markdown_target(surface_path, containing_links[0])
        if resolved != expected:
            findings.append(
                Finding(
                    "wrong-service-mention-link",
                    f"{surface_path}: alias {alias!r} links to {containing_links[0]!r}, expected {expected[0]}#{expected[1]}",
                )
            )


def _profile_fingerprint(name: str, contents: list[str]) -> str:
    text = _normalize(" ".join(contents)).lower()
    lowered_name = name.lower().strip()
    if lowered_name:
        text = text.replace(lowered_name, " service ")
    for token in sorted(set(re.findall(r"[a-z0-9]+", lowered_name)), key=len, reverse=True):
        if len(token) >= 3:
            text = re.sub(rf"\b{re.escape(token)}\b", " service ", text)
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _required_aliases_from_name(name: str) -> set[str]:
    required = {name}
    for parenthetical in re.findall(r"\(([^()]+)\)", name):
        phrase = parenthetical.strip()
        if phrase:
            required.add(phrase)
        for token in re.findall(r"\b[A-Z][A-Z0-9-]{1,9}\b", phrase):
            if token != "AWS":
                required.add(token)
    final_tokens = re.findall(r"[A-Za-z0-9-]+", name)
    if final_tokens:
        token = final_tokens[-1]
        if token != "AWS" and re.fullmatch(r"[A-Z][A-Z0-9-]{2,9}|[A-Z][A-Z0-9-]*\d[A-Z0-9-]*", token):
            required.add(token)
    return required


def _markdown_section(text: str, heading: str) -> tuple[str | None, str | None]:
    heading_match = MARKDOWN_HEADING.match(heading.strip())
    if heading_match is None:
        return None, "service section heading must be an explicit Markdown heading"
    normalized = _normalize(text)
    lines = normalized.splitlines()
    target = heading.strip()
    matches = [index for index, line in enumerate(lines) if line.strip() == target]
    if not matches:
        return None, "declared service section heading is not learner-visible"
    if len(matches) > 1:
        return None, "declared service section heading must be unique within the lecture"
    start = matches[0]
    level = len(heading_match.group(1))
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = MARKDOWN_HEADING.match(lines[index].strip())
        if match is not None and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end]).strip(), None


def validate_manifest(
    manifest_path: Path,
    content_root: Path,
    question_jsonl: Iterable[Path] = (),
    require_assessment_inventory: bool = False,
    lecture_jsonl: Iterable[Path] = (),
    require_service_sections: bool = False,
    navigation_jsonl: Iterable[Path] = (),
    require_service_curriculum: bool = False,
    service_entry_jsonl: Iterable[Path] = (),
    require_named_service_entries: bool = False,
    require_service_mention_links: bool = False,
) -> list[Finding]:
    findings: list[Finding] = []
    try:
        manifest = _load_json(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [Finding("invalid-manifest", f"cannot load manifest: {exc}")]

    content_root = content_root.resolve()
    if not content_root.is_dir():
        return [Finding("invalid-content-root", f"content root is not a directory: {content_root}")]
    if manifest.get("version") != 1:
        findings.append(Finding("unsupported-version", "manifest version must be 1"))

    entry_contract = manifest.get("entry_contract")
    if not isinstance(entry_contract, dict):
        findings.append(Finding("missing-entry-contract", "entry_contract must be an object"))
        entry_contract = {}

    assumptions_by_id: dict[str, dict[str, Any]] = {}
    for assumption in _list(entry_contract.get("assumptions")):
        if not isinstance(assumption, dict) or not _nonempty_string(assumption.get("id")):
            findings.append(Finding("invalid-entry-assumption", "every entry assumption needs a string id"))
            continue
        assumption_id = str(assumption["id"])
        if assumption_id in assumptions_by_id:
            findings.append(Finding("duplicate-entry-assumption", f"duplicate entry assumption: {assumption_id}"))
        assumptions_by_id[assumption_id] = assumption
        if assumption.get("basis") not in ALLOWED_ASSUMPTION_BASES:
            findings.append(Finding("invalid-assumption-basis", f"{assumption_id}: basis must be one of {sorted(ALLOWED_ASSUMPTION_BASES)}"))
        if not _nonempty_string(assumption.get("description")) or not _nonempty_string(assumption.get("rationale")):
            findings.append(Finding("incomplete-entry-assumption", f"{assumption_id}: description and rationale are required"))
        if assumption.get("basis") in {"user_confirmed", "official_required"} and not _nonempty_string(assumption.get("evidence")):
            findings.append(Finding("missing-assumption-evidence", f"{assumption_id}: confirmed or required assumptions need evidence"))

    assumed_certifications = _list(entry_contract.get("assumed_certifications"))
    for certification in assumed_certifications:
        if not isinstance(certification, dict) or not _nonempty_string(certification.get("name")):
            findings.append(Finding("invalid-assumed-certification", "assumed certification entries need a name"))
            continue
        name = str(certification["name"])
        if certification.get("user_approved") is not True or not _nonempty_string(certification.get("approval_reference")):
            findings.append(Finding("unapproved-assumed-certification", f"{name}: a lower or prior certification cannot be assumed without explicit user approval"))

    file_cache: dict[Path, str] = {}
    evidence_owners: dict[str, str] = {}
    units_by_id: dict[str, dict[str, Any]] = {}
    subject_to_units: dict[str, list[str]] = {}
    artifact_to_unit: dict[str, str] = {}
    pattern_to_unit: dict[str, str] = {}

    curriculum_policy = manifest.get("service_curriculum_policy")
    policy_requires_curriculum = (
        isinstance(curriculum_policy, dict)
        and curriculum_policy.get("require_top_level_category") is True
    )
    strict_service_curriculum = require_service_curriculum or policy_requires_curriculum
    if require_service_curriculum and not policy_requires_curriculum:
        findings.append(
            Finding(
                "service-curriculum-policy-required",
                "strict validation requires service_curriculum_policy.require_top_level_category=true",
            )
        )

    policy_requires_named_entries = (
        isinstance(curriculum_policy, dict)
        and curriculum_policy.get("require_named_service_entries") is True
    )
    strict_named_service_entries = require_named_service_entries or policy_requires_named_entries
    if require_named_service_entries and not policy_requires_named_entries:
        findings.append(
            Finding(
                "named-service-entry-policy-required",
                "strict validation requires service_curriculum_policy.require_named_service_entries=true",
            )
        )
    if strict_named_service_entries and not strict_service_curriculum:
        findings.append(
            Finding(
                "named-service-entry-requires-curriculum",
                "named Service entries require the top-level Service curriculum contract",
            )
        )

    policy_requires_mention_links = (
        isinstance(curriculum_policy, dict)
        and curriculum_policy.get("require_service_mention_links") is True
    )
    strict_service_mention_links = require_service_mention_links or policy_requires_mention_links
    if require_service_mention_links and not policy_requires_mention_links:
        findings.append(
            Finding(
                "service-mention-link-policy-required",
                "strict validation requires service_curriculum_policy.require_service_mention_links=true",
            )
        )
    if strict_service_mention_links and not strict_named_service_entries:
        findings.append(
            Finding(
                "service-mention-links-require-named-entries",
                "Service mention links require the named Service-entry contract",
            )
        )

    curriculum_units_by_id: dict[str, dict[str, Any]] = {}
    curriculum_subject_to_unit: dict[str, str] = {}
    service_entries_by_id: dict[str, dict[str, Any]] = {}
    service_entry_name_to_id: dict[str, str] = {}
    service_alias_to_entry: dict[str, str] = {}
    service_alias_casefold_owners: dict[str, tuple[str, str]] = {}
    navigation_categories_by_id: dict[str, dict[str, Any]] = {}
    service_category: dict[str, Any] | None = None
    if strict_service_curriculum:
        service_category_id = (
            str(curriculum_policy.get("service_category_id", ""))
            if isinstance(curriculum_policy, dict)
            else ""
        )
        if not service_category_id:
            findings.append(
                Finding(
                    "service-category-id-required",
                    "service_curriculum_policy.service_category_id is required",
                )
            )

        for category in _list(manifest.get("navigation_categories")):
            if not isinstance(category, dict) or not _nonempty_string(category.get("id")):
                findings.append(Finding("invalid-navigation-category", "every navigation category needs a string id"))
                continue
            normalized_category = _navigation_row(category)
            category_id = normalized_category["id"]
            if category_id in navigation_categories_by_id:
                findings.append(Finding("duplicate-navigation-category", f"duplicate navigation category: {category_id}"))
            navigation_categories_by_id[category_id] = normalized_category
            if not _nonempty_string(normalized_category["kind"]) or not _nonempty_string(normalized_category["label"]):
                findings.append(Finding("incomplete-navigation-category", f"{category_id}: kind and learner-visible label are required"))
            if not isinstance(normalized_category["sequence"], (int, float)):
                findings.append(Finding("missing-navigation-sequence", f"{category_id}: numeric sequence is required"))
            if not _nonempty_string(normalized_category["landing_path"]):
                findings.append(Finding("missing-navigation-landing", f"{category_id}: landing_path is required"))
            page_paths = normalized_category["page_paths"]
            if not page_paths:
                findings.append(Finding("empty-navigation-category", f"{category_id}: page_paths must not be empty"))
            if normalized_category["landing_path"] not in page_paths:
                findings.append(Finding("navigation-landing-unlisted", f"{category_id}: landing_path must be listed in page_paths"))
            for relative_path in page_paths:
                content_path = _resolve_content_path(content_root, relative_path)
                if content_path is None:
                    findings.append(Finding("invalid-navigation-page", f"{category_id}: page path is outside content root: {relative_path}"))
                elif not content_path.is_file():
                    findings.append(Finding("missing-navigation-page", f"{category_id}: learner-visible page is absent: {relative_path}"))

        expected_navigation_count = (
            curriculum_policy.get("expected_navigation_category_count")
            if isinstance(curriculum_policy, dict)
            else None
        )
        if not isinstance(expected_navigation_count, int) or expected_navigation_count < 2:
            findings.append(
                Finding(
                    "invalid-expected-navigation-count",
                    "service_curriculum_policy.expected_navigation_category_count must be an integer of at least two",
                )
            )
        elif expected_navigation_count != len(navigation_categories_by_id):
            findings.append(
                Finding(
                    "navigation-category-count-mismatch",
                    f"expected {expected_navigation_count} navigation categories, found {len(navigation_categories_by_id)}",
                )
            )

        service_category = navigation_categories_by_id.get(service_category_id)
        service_kind_categories = [
            value for value in navigation_categories_by_id.values() if value.get("kind") == "service"
        ]
        if service_category is None or service_category.get("kind") != "service" or len(service_kind_categories) != 1:
            findings.append(
                Finding(
                    "service-category-required",
                    "exactly one declared top-level Service navigation category is required",
                )
            )
        else:
            if service_category.get("parent_id") not in (None, ""):
                findings.append(
                    Finding(
                        "service-category-not-top-level",
                        f"{service_category_id}: Service category must not have a parent category",
                    )
                )
            dependent_categories = [
                value
                for value in navigation_categories_by_id.values()
                if value.get("kind") in SERVICE_DEPENDENT_NAVIGATION_KINDS
            ]
            if not dependent_categories:
                findings.append(
                    Finding(
                        "service-category-dependent-category-required",
                        "navigation inventory must include a lecture, question, or mock category after Services",
                    )
                )
            elif isinstance(service_category.get("sequence"), (int, float)):
                for category in dependent_categories:
                    if (
                        isinstance(category.get("sequence"), (int, float))
                        and service_category["sequence"] >= category["sequence"]
                    ):
                        findings.append(
                            Finding(
                                "service-category-not-upper",
                                f"{service_category_id}: Service category must precede {category['id']}",
                            )
                        )

        navigation_inventory_paths = [Path(path).resolve() for path in navigation_jsonl]
        if not navigation_inventory_paths:
            findings.append(
                Finding(
                    "navigation-inventory-required",
                    "strict Service-curriculum validation requires at least one canonical navigation JSONL",
                )
            )
        else:
            inventory_categories = _read_navigation_inventory(navigation_inventory_paths, findings)
            if inventory_categories != navigation_categories_by_id:
                findings.append(
                    Finding(
                        "navigation-inventory-mismatch",
                        "manifest navigation categories differ from the canonical navigation inventory",
                    )
                )

        curriculum_evidence_owners: dict[str, str] = {}
        for unit in _list(manifest.get("service_curriculum")):
            if not isinstance(unit, dict) or not _nonempty_string(unit.get("id")):
                findings.append(Finding("invalid-service-curriculum-unit", "every Service curriculum unit needs a string id"))
                continue
            unit_id = str(unit["id"])
            if unit_id in curriculum_units_by_id:
                findings.append(Finding("duplicate-service-curriculum-unit", f"duplicate Service curriculum unit: {unit_id}"))
            curriculum_units_by_id[unit_id] = unit
            subject = unit.get("subject")
            if not _nonempty_string(subject):
                findings.append(Finding("missing-service-curriculum-subject", f"{unit_id}: subject is required"))
            elif str(subject) in curriculum_subject_to_unit:
                findings.append(Finding("duplicate-service-curriculum-subject", f"duplicate Service curriculum subject: {subject}"))
            else:
                curriculum_subject_to_unit[str(subject)] = unit_id
            if not isinstance(unit.get("sequence"), (int, float)):
                findings.append(Finding("missing-service-curriculum-sequence", f"{unit_id}: numeric sequence is required"))
            relative_path = str(unit.get("path", "")).replace("\\", "/")
            curriculum_path = _resolve_content_path(content_root, relative_path)
            if curriculum_path is None:
                findings.append(Finding("invalid-service-curriculum-path", f"{unit_id}: path is missing or outside content root"))
            elif not curriculum_path.is_file():
                findings.append(Finding("missing-service-curriculum-page", f"{unit_id}: learner-visible page does not exist"))
            if service_category is not None and relative_path not in service_category.get("page_paths", []):
                findings.append(
                    Finding(
                        "service-curriculum-outside-category",
                        f"{unit_id}: curriculum page is not listed under the top-level Service category",
                    )
                )

            covered_dimensions: set[str] = set()
            for index, evidence in enumerate(_list(unit.get("evidence")), start=1):
                dimensions = _list(evidence.get("dimensions")) if isinstance(evidence, dict) else []
                if len(dimensions) != 1 or dimensions[0] not in REQUIRED_DIMENSIONS["service"]:
                    findings.append(
                        Finding(
                            "invalid-service-curriculum-dimension",
                            f"{unit_id} evidence {index}: provide exactly one valid Service dimension",
                        )
                    )
                else:
                    dimension = str(dimensions[0])
                    covered_dimensions.add(dimension)
                    content = evidence.get("content") if isinstance(evidence, dict) else None
                    if _nonempty_string(content):
                        key = _normalize(str(content)).strip()
                        owner = f"{unit_id}:{dimension}"
                        prior_owner = curriculum_evidence_owners.get(key)
                        if prior_owner is not None and prior_owner != owner:
                            findings.append(
                                Finding(
                                    "reused-service-curriculum-evidence",
                                    f"{owner}: exact evidence is already used by {prior_owner}",
                                )
                            )
                        else:
                            curriculum_evidence_owners[key] = owner
                visible = _validate_exact_slice(
                    owner=f"{unit_id} curriculum evidence {index}",
                    evidence=evidence,
                    root=content_root,
                    file_cache=file_cache,
                    findings=findings,
                    minimum_length=30,
                )
                if visible and isinstance(evidence, dict):
                    evidence_path = _resolve_content_path(content_root, evidence.get("path"))
                    if curriculum_path is not None and evidence_path != curriculum_path:
                        findings.append(
                            Finding(
                                "service-curriculum-evidence-outside-page",
                                f"{unit_id} evidence {index}: evidence must be inside its comprehensive Service lecture",
                            )
                        )
            missing_dimensions = REQUIRED_DIMENSIONS["service"] - covered_dimensions
            if missing_dimensions:
                findings.append(
                    Finding(
                        "missing-service-curriculum-dimensions",
                        f"{unit_id}: missing {sorted(missing_dimensions)}",
                    )
                )

        expected_curriculum_count = (
            curriculum_policy.get("expected_service_count")
            if isinstance(curriculum_policy, dict)
            else None
        )
        if not isinstance(expected_curriculum_count, int) or expected_curriculum_count < 1:
            findings.append(
                Finding(
                    "invalid-expected-service-curriculum-count",
                    "service_curriculum_policy.expected_service_count must be a positive integer",
                )
            )
        elif expected_curriculum_count != len(curriculum_units_by_id):
            findings.append(
                Finding(
                    "service-curriculum-count-mismatch",
                    f"expected {expected_curriculum_count} Service curriculum units, found {len(curriculum_units_by_id)}",
                )
            )

        if strict_named_service_entries:
            entry_evidence_owners: dict[str, str] = {}
            anchor_owners: dict[str, str] = {}
            profile_owners: dict[str, str] = {}
            entries_by_curriculum: dict[str, set[str]] = {}
            minimum_profile_words = (
                curriculum_policy.get("minimum_named_service_profile_words")
                if isinstance(curriculum_policy, dict)
                else None
            )
            if not isinstance(minimum_profile_words, int) or minimum_profile_words < 60:
                findings.append(
                    Finding(
                        "invalid-named-service-profile-minimum",
                        "service_curriculum_policy.minimum_named_service_profile_words must be an integer of at least 60",
                    )
                )
                minimum_profile_words = 60

            for entry in _list(manifest.get("service_entries")):
                if not isinstance(entry, dict) or not _nonempty_string(entry.get("id")):
                    findings.append(Finding("invalid-service-entry", "every named Service entry needs a string id"))
                    continue
                entry_id = str(entry["id"])
                if entry_id in service_entries_by_id:
                    findings.append(Finding("duplicate-service-entry", f"duplicate named Service entry: {entry_id}"))
                service_entries_by_id[entry_id] = entry

                name = entry.get("name")
                if not _nonempty_string(name):
                    findings.append(Finding("missing-service-entry-name", f"{entry_id}: formal learner-visible name is required"))
                    name = ""
                elif str(name) in service_entry_name_to_id:
                    findings.append(Finding("duplicate-service-entry-name", f"duplicate named Service entry: {name}"))
                else:
                    service_entry_name_to_id[str(name)] = entry_id
                if strict_service_mention_links:
                    aliases_value = entry.get("aliases")
                    if not isinstance(aliases_value, list) or not aliases_value:
                        findings.append(Finding("missing-service-entry-aliases", f"{entry_id}: aliases must be a non-empty list"))
                        aliases: list[str] = []
                    else:
                        aliases = []
                        local_alias_keys: set[str] = set()
                        for raw_alias in aliases_value:
                            if not isinstance(raw_alias, str) or not raw_alias.strip():
                                findings.append(Finding("invalid-service-entry-alias", f"{entry_id}: aliases must be non-empty strings"))
                                continue
                            alias = raw_alias
                            if alias != alias.strip() or "\n" in alias or "\r" in alias or any(token in alias for token in ("[", "]")):
                                findings.append(Finding("invalid-service-entry-alias", f"{entry_id}: alias {alias!r} contains whitespace or Markdown-link syntax"))
                                continue
                            alias_key = alias.casefold()
                            if alias_key in local_alias_keys:
                                findings.append(Finding("duplicate-service-entry-alias", f"{entry_id}: duplicate alias {alias!r}"))
                                continue
                            local_alias_keys.add(alias_key)
                            aliases.append(alias)
                            prior_owner = service_alias_casefold_owners.get(alias_key)
                            if prior_owner is not None and prior_owner[0] != entry_id:
                                findings.append(
                                    Finding(
                                        "ambiguous-service-entry-alias",
                                        f"{entry_id}: alias {alias!r} is already assigned to {prior_owner[0]} as {prior_owner[1]!r}",
                                    )
                                )
                                continue
                            service_alias_casefold_owners[alias_key] = (entry_id, alias)
                            service_alias_to_entry[alias] = entry_id
                    if _nonempty_string(name) and str(name) not in aliases:
                        findings.append(Finding("service-entry-formal-name-not-alias", f"{entry_id}: aliases must include the formal Service name"))
                    if _nonempty_string(name):
                        missing_derived_aliases = _required_aliases_from_name(str(name)) - set(aliases)
                        if missing_derived_aliases:
                            findings.append(
                                Finding(
                                    "missing-derived-service-entry-alias",
                                    f"{entry_id}: aliases omit formal-name abbreviation(s) {sorted(missing_derived_aliases)}",
                                )
                            )
                if not _nonempty_string(entry.get("kind")):
                    findings.append(Finding("missing-service-entry-kind", f"{entry_id}: kind is required"))
                if not isinstance(entry.get("sequence"), (int, float)):
                    findings.append(Finding("missing-service-entry-sequence", f"{entry_id}: numeric sequence is required"))

                curriculum_unit_id = entry.get("curriculum_unit_id")
                if not _nonempty_string(curriculum_unit_id):
                    findings.append(Finding("missing-service-entry-curriculum", f"{entry_id}: curriculum_unit_id is required"))
                    curriculum_unit_id = ""
                elif str(curriculum_unit_id) not in curriculum_units_by_id:
                    findings.append(Finding("unknown-service-entry-curriculum", f"{entry_id}: unknown curriculum unit {curriculum_unit_id}"))
                else:
                    entries_by_curriculum.setdefault(str(curriculum_unit_id), set()).add(entry_id)

                relative_path = str(entry.get("path", "")).replace("\\", "/")
                entry_path = _resolve_content_path(content_root, relative_path)
                if entry_path is None:
                    findings.append(Finding("invalid-service-entry-path", f"{entry_id}: path is missing or outside content root"))
                elif not entry_path.is_file():
                    findings.append(Finding("missing-service-entry-page", f"{entry_id}: learner-visible page does not exist"))
                if service_category is not None and relative_path not in service_category.get("page_paths", []):
                    findings.append(Finding("service-entry-outside-category", f"{entry_id}: page is not listed under the top-level Service category"))
                if _nonempty_string(curriculum_unit_id):
                    owner_unit = curriculum_units_by_id.get(str(curriculum_unit_id))
                    if owner_unit is not None and str(owner_unit.get("path", "")).replace("\\", "/") != relative_path:
                        findings.append(Finding("service-entry-page-mismatch", f"{entry_id}: entry and owning curriculum unit must share a page"))

                heading = entry.get("heading")
                entry_section: str | None = None
                if not _nonempty_string(heading):
                    findings.append(Finding("missing-service-entry-heading", f"{entry_id}: an explicit Markdown heading is required"))
                elif _nonempty_string(name) and str(name) not in str(heading):
                    findings.append(Finding("service-entry-heading-name-mismatch", f"{entry_id}: heading must contain the formal Service name"))
                elif entry_path is not None and entry_path.is_file():
                    if entry_path not in file_cache:
                        file_cache[entry_path] = _normalize(entry_path.read_text(encoding="utf-8-sig"))
                    entry_section, section_error = _markdown_section(file_cache[entry_path], str(heading))
                    if section_error is not None:
                        findings.append(Finding("missing-service-entry-section", f"{entry_id}: {section_error}"))

                anchor = entry.get("anchor")
                if not _nonempty_string(anchor) or STABLE_ANCHOR.fullmatch(str(anchor)) is None:
                    findings.append(Finding("invalid-service-entry-anchor", f"{entry_id}: stable lowercase hyphenated anchor is required"))
                else:
                    anchor = str(anchor)
                    prior_anchor_owner = anchor_owners.get(anchor)
                    if prior_anchor_owner is not None and prior_anchor_owner != entry_id:
                        findings.append(Finding("duplicate-service-entry-anchor", f"{entry_id}: anchor is already used by {prior_anchor_owner}"))
                    else:
                        anchor_owners[anchor] = entry_id
                    if entry_path is not None and entry_path.is_file() and f'<a id="{anchor}"></a>' not in file_cache[entry_path]:
                        findings.append(Finding("missing-service-entry-anchor", f"{entry_id}: declared anchor is not learner-visible"))

                index_evidence = entry.get("index_evidence")
                index_visible = _validate_exact_slice(
                    owner=f"{entry_id} landing index",
                    evidence=index_evidence,
                    root=content_root,
                    file_cache=file_cache,
                    findings=findings,
                    minimum_length=10,
                )
                if index_visible and isinstance(index_evidence, dict):
                    index_path = str(index_evidence.get("path", "")).replace("\\", "/")
                    expected_index_path = str(service_category.get("landing_path", "")) if service_category is not None else ""
                    if index_path != expected_index_path:
                        findings.append(Finding("service-entry-index-path-mismatch", f"{entry_id}: index evidence must be on the Service landing page"))
                    index_content = str(index_evidence.get("content", ""))
                    expected_fragment = f"#{anchor}" if _nonempty_string(anchor) else "#"
                    if (_nonempty_string(name) and str(name) not in index_content) or expected_fragment not in index_content:
                        findings.append(Finding("service-entry-index-link-mismatch", f"{entry_id}: landing link must contain the formal name and declared anchor"))

                covered_entry_dimensions: set[str] = set()
                profile_contents: list[str] = []
                evidence_rows = _list(entry.get("evidence"))
                if len(evidence_rows) < 6:
                    findings.append(Finding("service-entry-too-shallow", f"{entry_id}: at least six distinct teaching slices are required"))
                for index, evidence in enumerate(evidence_rows, start=1):
                    dimensions = _list(evidence.get("dimensions")) if isinstance(evidence, dict) else []
                    dimension_set = {str(value) for value in dimensions}
                    if not dimension_set or len(dimension_set) != len(dimensions) or not dimension_set <= REQUIRED_DIMENSIONS["service"]:
                        findings.append(Finding("invalid-service-entry-dimensions", f"{entry_id} evidence {index}: provide one or more unique valid Service dimensions"))
                    else:
                        covered_entry_dimensions.update(dimension_set)
                    content = evidence.get("content") if isinstance(evidence, dict) else None
                    if _nonempty_string(content):
                        normalized_content = _normalize(str(content)).strip()
                        profile_contents.append(normalized_content)
                        owner = f"{entry_id}:{','.join(sorted(dimension_set))}"
                        prior_owner = entry_evidence_owners.get(normalized_content)
                        family_owner = curriculum_evidence_owners.get(normalized_content)
                        if prior_owner is not None and prior_owner != owner:
                            findings.append(Finding("reused-service-entry-evidence", f"{owner}: exact evidence is already used by {prior_owner}"))
                        elif family_owner is not None:
                            findings.append(Finding("service-entry-reuses-family-evidence", f"{owner}: exact evidence is reused from {family_owner}"))
                        else:
                            entry_evidence_owners[normalized_content] = owner
                    evidence_visible = _validate_exact_slice(
                        owner=f"{entry_id} evidence {index}",
                        evidence=evidence,
                        root=content_root,
                        file_cache=file_cache,
                        findings=findings,
                        minimum_length=40,
                    )
                    if evidence_visible and isinstance(evidence, dict):
                        evidence_path = _resolve_content_path(content_root, evidence.get("path"))
                        evidence_content = _normalize(str(evidence.get("content", ""))).strip()
                        if entry_path is not None and evidence_path != entry_path:
                            findings.append(Finding("service-entry-evidence-outside-page", f"{entry_id} evidence {index}: evidence must be on the entry page"))
                        elif entry_section is not None and evidence_content not in entry_section:
                            findings.append(Finding("service-entry-evidence-outside-section", f"{entry_id} evidence {index}: evidence must be inside the named Service section"))

                missing_entry_dimensions = REQUIRED_DIMENSIONS["service"] - covered_entry_dimensions
                if missing_entry_dimensions:
                    findings.append(Finding("missing-service-entry-dimensions", f"{entry_id}: missing {sorted(missing_entry_dimensions)}"))
                word_count = len(re.findall(r"\b[\w'-]+\b", " ".join(profile_contents), flags=re.UNICODE))
                if word_count < int(minimum_profile_words):
                    findings.append(Finding("service-entry-profile-too-short", f"{entry_id}: profile has {word_count} words, requires {minimum_profile_words}"))
                if _nonempty_string(name) and str(name) not in " ".join(profile_contents):
                    findings.append(Finding("service-entry-name-absent-from-evidence", f"{entry_id}: formal name must appear in its teaching evidence"))
                if _nonempty_string(name) and profile_contents:
                    fingerprint = _profile_fingerprint(str(name), profile_contents)
                    prior_profile_owner = profile_owners.get(fingerprint)
                    if prior_profile_owner is not None and prior_profile_owner != entry_id:
                        findings.append(Finding("generic-name-substitution-service-entry", f"{entry_id}: profile becomes identical to {prior_profile_owner} after removing the Service name"))
                    else:
                        profile_owners[fingerprint] = entry_id

            expected_named_count = (
                curriculum_policy.get("expected_named_service_count")
                if isinstance(curriculum_policy, dict)
                else None
            )
            if not isinstance(expected_named_count, int) or expected_named_count < 1:
                findings.append(Finding("invalid-expected-named-service-count", "service_curriculum_policy.expected_named_service_count must be a positive integer"))
            elif expected_named_count != len(service_entries_by_id):
                findings.append(Finding("named-service-count-mismatch", f"expected {expected_named_count} named Service entries, found {len(service_entries_by_id)}"))

            for curriculum_unit_id, unit in curriculum_units_by_id.items():
                declared_entry_ids = {str(value) for value in _list(unit.get("service_entry_ids"))}
                actual_entry_ids = entries_by_curriculum.get(curriculum_unit_id, set())
                if declared_entry_ids != actual_entry_ids:
                    findings.append(Finding("service-entry-curriculum-membership-mismatch", f"{curriculum_unit_id}: declared entries differ from child entries"))

            service_entry_inventory_paths = [Path(path).resolve() for path in service_entry_jsonl]
            if not service_entry_inventory_paths:
                findings.append(Finding("service-entry-inventory-required", "strict named-Service validation requires at least one canonical Service-entry JSONL"))
            else:
                inventory_entries = _read_service_entry_inventory(service_entry_inventory_paths, findings)
                manifest_entries = {entry_id: _service_entry_row(entry) for entry_id, entry in service_entries_by_id.items()}
                if inventory_entries != manifest_entries:
                    findings.append(Finding("service-entry-inventory-mismatch", "manifest named Service entries differ from the canonical Service-entry inventory"))

    lecture_policy = manifest.get("lecture_policy")
    policy_requires_sections = isinstance(lecture_policy, dict) and lecture_policy.get("require_service_sections") is True
    strict_service_sections = require_service_sections or policy_requires_sections
    if require_service_sections and not policy_requires_sections:
        findings.append(Finding("service-section-policy-required", "strict validation requires lecture_policy.require_service_sections=true"))
    if strict_service_mention_links and not strict_service_sections:
        findings.append(
            Finding(
                "service-mention-links-require-lecture-surfaces",
                "Service mention links require the canonical lecture and Service-section contract",
            )
        )

    lectures_by_id: dict[str, dict[str, Any]] = {}
    lecture_relative_paths: dict[str, str] = {}
    lecture_sections: dict[str, tuple[Path, str, set[str]]] = {}
    if strict_service_sections:
        for lecture in _list(manifest.get("lectures")):
            if not isinstance(lecture, dict) or not _nonempty_string(lecture.get("id")):
                findings.append(Finding("invalid-lecture", "every lecture needs a string id"))
                continue
            lecture_id = str(lecture["id"])
            if lecture_id in lectures_by_id:
                findings.append(Finding("duplicate-lecture", f"duplicate lecture in manifest: {lecture_id}"))
            lectures_by_id[lecture_id] = lecture
            if not isinstance(lecture.get("sequence"), (int, float)):
                findings.append(Finding("missing-lecture-sequence", f"{lecture_id}: numeric sequence is required"))

            relative_path = lecture.get("path")
            lecture_path = _resolve_content_path(content_root, relative_path)
            if lecture_path is None:
                findings.append(Finding("invalid-lecture-path", f"{lecture_id}: path is missing or outside content root"))
                continue
            lecture_relative_paths[lecture_id] = str(relative_path).replace("\\", "/")
            if not lecture_path.is_file():
                findings.append(Finding("missing-lecture-file", f"{lecture_id}: learner-visible lecture does not exist: {lecture_path}"))
                continue
            if lecture_path not in file_cache:
                file_cache[lecture_path] = _normalize(lecture_path.read_text(encoding="utf-8-sig"))

            section = lecture.get("service_section")
            if not isinstance(section, dict):
                findings.append(Finding("missing-service-section", f"{lecture_id}: service_section must be an object"))
                continue
            heading = section.get("heading")
            if not _nonempty_string(heading):
                findings.append(Finding("missing-service-section-heading", f"{lecture_id}: service section needs a Markdown heading"))
                continue
            service_unit_ids = [str(item) for item in _list(section.get("service_unit_ids")) if _nonempty_string(item)]
            if not service_unit_ids:
                findings.append(Finding("empty-service-section", f"{lecture_id}: service section must list at least one service unit"))
            if len(service_unit_ids) != len(set(service_unit_ids)):
                findings.append(Finding("duplicate-service-section-unit", f"{lecture_id}: service_unit_ids must be unique"))

            evidence = section.get("evidence")
            _validate_exact_slice(
                owner=f"{lecture_id} service section",
                evidence=evidence,
                root=content_root,
                file_cache=file_cache,
                findings=findings,
                minimum_length=80,
            )
            evidence_path = _resolve_content_path(content_root, evidence.get("path")) if isinstance(evidence, dict) else None
            if evidence_path is not None and evidence_path != lecture_path:
                findings.append(Finding("service-section-path-mismatch", f"{lecture_id}: service section evidence must be in its lecture path"))
            evidence_content = evidence.get("content") if isinstance(evidence, dict) else None
            if _nonempty_string(evidence_content) and not _normalize(str(evidence_content)).lstrip().startswith(str(heading).strip()):
                findings.append(Finding("service-section-evidence-missing-heading", f"{lecture_id}: service section evidence must begin with the declared heading"))

            section_text, section_error = _markdown_section(file_cache[lecture_path], str(heading))
            if section_error is not None:
                findings.append(Finding("missing-service-section", f"{lecture_id}: {section_error}"))
                continue
            if _nonempty_string(evidence_content) and _normalize(str(evidence_content)).strip() not in str(section_text):
                findings.append(Finding("service-section-evidence-outside-section", f"{lecture_id}: declared section evidence is not inside the Markdown service section"))
            lecture_sections[lecture_id] = (lecture_path, str(section_text), set(service_unit_ids))

        expected_lecture_count = lecture_policy.get("expected_count") if isinstance(lecture_policy, dict) else None
        if not isinstance(expected_lecture_count, int) or expected_lecture_count < 1:
            findings.append(Finding("invalid-expected-lecture-count", "lecture_policy.expected_count must be a positive integer"))
        elif expected_lecture_count != len(lectures_by_id):
            findings.append(Finding("lecture-count-mismatch", f"expected {expected_lecture_count} lectures, found {len(lectures_by_id)}"))

        lecture_inventory_paths = [Path(path).resolve() for path in lecture_jsonl]
        if not lecture_inventory_paths:
            findings.append(Finding("lecture-inventory-required", "strict service-section validation requires at least one canonical lecture JSONL"))
        else:
            inventory_lectures = _read_lecture_inventory(lecture_inventory_paths, findings)
            if set(inventory_lectures) != set(lectures_by_id):
                findings.append(
                    Finding(
                        "lecture-inventory-mismatch",
                        f"manifest/lecture ID mismatch missing={sorted(set(inventory_lectures) - set(lectures_by_id))} extra={sorted(set(lectures_by_id) - set(inventory_lectures))}",
                    )
                )
            for lecture_id in set(inventory_lectures) & set(lecture_relative_paths):
                if inventory_lectures[lecture_id] != lecture_relative_paths[lecture_id]:
                    findings.append(Finding("lecture-path-mismatch", f"{lecture_id}: inventory path {inventory_lectures[lecture_id]} != manifest path {lecture_relative_paths[lecture_id]}"))

    for unit in _list(manifest.get("learning_units")):
        if not isinstance(unit, dict) or not _nonempty_string(unit.get("id")):
            findings.append(Finding("invalid-learning-unit", "every learning unit needs a string id"))
            continue
        unit_id = str(unit["id"])
        if unit_id in units_by_id:
            findings.append(Finding("duplicate-learning-unit", f"duplicate learning unit: {unit_id}"))
        if unit_id in assumptions_by_id:
            findings.append(Finding("duplicate-learning-contract-id", f"{unit_id}: ID is shared by an entry assumption and learning unit"))
        units_by_id[unit_id] = unit

        kind = unit.get("kind")
        if kind not in REQUIRED_DIMENSIONS:
            findings.append(Finding("invalid-learning-unit-kind", f"{unit_id}: kind must be one of {sorted(REQUIRED_DIMENSIONS)}"))
            continue
        if not isinstance(unit.get("sequence"), (int, float)):
            findings.append(Finding("missing-learning-sequence", f"{unit_id}: numeric sequence is required"))

        if kind == "service":
            subject = unit.get("subject")
            if not _nonempty_string(subject):
                findings.append(Finding("missing-service-subject", f"{unit_id}: service unit needs subject"))
            elif not strict_service_sections and str(subject) in subject_to_units:
                findings.append(Finding("duplicate-service-subject", f"service subject has multiple units: {subject}"))
            else:
                subject_to_units.setdefault(str(subject), []).append(unit_id)
            if strict_service_sections:
                lecture_id = unit.get("lecture_id")
                if not _nonempty_string(lecture_id):
                    findings.append(Finding("missing-service-lecture", f"{unit_id}: strict service unit needs lecture_id"))
                elif str(lecture_id) not in lectures_by_id:
                    findings.append(Finding("unknown-service-lecture", f"{unit_id}: unknown lecture_id {lecture_id}"))
            if strict_service_curriculum:
                curriculum_unit_id = unit.get("curriculum_unit_id")
                if not _nonempty_string(curriculum_unit_id):
                    findings.append(
                        Finding(
                            "missing-service-curriculum-binding",
                            f"{unit_id}: Service unit needs curriculum_unit_id",
                        )
                    )
                else:
                    curriculum_unit = curriculum_units_by_id.get(str(curriculum_unit_id))
                    if curriculum_unit is None:
                        findings.append(
                            Finding(
                                "unknown-service-curriculum-binding",
                                f"{unit_id}: unknown curriculum_unit_id {curriculum_unit_id}",
                            )
                        )
                    elif str(curriculum_unit.get("subject", "")) != str(subject or ""):
                        findings.append(
                            Finding(
                                "service-curriculum-subject-mismatch",
                                f"{unit_id}: page-local and comprehensive Service subjects differ",
                            )
                        )
        elif kind == "artifact":
            artifact_type = unit.get("artifact_type")
            if not _nonempty_string(artifact_type):
                findings.append(Finding("missing-artifact-type", f"{unit_id}: artifact unit needs artifact_type"))
            elif str(artifact_type) in artifact_to_unit:
                findings.append(Finding("duplicate-artifact-type", f"artifact type has multiple units: {artifact_type}"))
            else:
                artifact_to_unit[str(artifact_type)] = unit_id
        elif kind == "integration":
            pattern_id = unit.get("pattern_id")
            if not _nonempty_string(pattern_id):
                findings.append(Finding("missing-integration-pattern", f"{unit_id}: integration unit needs pattern_id"))
            elif str(pattern_id) in pattern_to_unit:
                findings.append(Finding("duplicate-integration-pattern", f"integration pattern has multiple units: {pattern_id}"))
            else:
                pattern_to_unit[str(pattern_id)] = unit_id

        covered_dimensions: set[str] = set()
        for index, evidence in enumerate(_list(unit.get("evidence")), start=1):
            dimensions = _list(evidence.get("dimensions")) if isinstance(evidence, dict) else []
            if len(dimensions) != 1 or dimensions[0] not in REQUIRED_DIMENSIONS[kind]:
                findings.append(Finding("invalid-evidence-dimension", f"{unit_id} evidence {index}: provide exactly one valid dimension"))
            else:
                covered_dimensions.add(str(dimensions[0]))
                content = evidence.get("content") if isinstance(evidence, dict) else None
                if _nonempty_string(content):
                    evidence_key = _normalize(str(content)).strip()
                    owner = f"{unit_id}:{dimensions[0]}"
                    prior_owner = evidence_owners.get(evidence_key)
                    if prior_owner is not None and prior_owner != owner:
                        findings.append(Finding("reused-learning-evidence", f"{owner}: exact evidence is already used by {prior_owner}"))
                    else:
                        evidence_owners[evidence_key] = owner
            evidence_is_visible = _validate_exact_slice(
                owner=f"{unit_id} evidence {index}",
                evidence=evidence,
                root=content_root,
                file_cache=file_cache,
                findings=findings,
                minimum_length=30,
            )
            if kind == "service" and strict_service_sections and evidence_is_visible:
                lecture_id = str(unit.get("lecture_id", ""))
                lecture_section = lecture_sections.get(lecture_id)
                if lecture_section is not None and isinstance(evidence, dict):
                    evidence_path = _resolve_content_path(content_root, evidence.get("path"))
                    evidence_content = evidence.get("content")
                    if evidence_path != lecture_section[0] or _normalize(str(evidence_content)).strip() not in lecture_section[1]:
                        findings.append(Finding("service-evidence-outside-service-section", f"{unit_id} evidence {index}: Service evidence must be inside its lecture's Service section"))
        missing_dimensions = REQUIRED_DIMENSIONS[kind] - covered_dimensions
        if missing_dimensions:
            findings.append(Finding("missing-learning-dimensions", f"{unit_id}: missing {sorted(missing_dimensions)}"))

    if strict_service_sections:
        for lecture_id, (_, _, section_unit_ids) in lecture_sections.items():
            for unit_id in sorted(section_unit_ids):
                unit = units_by_id.get(unit_id)
                if unit is None:
                    findings.append(Finding("unknown-service-section-unit", f"{lecture_id}: unknown service unit {unit_id}"))
                elif unit.get("kind") != "service":
                    findings.append(Finding("non-service-section-unit", f"{lecture_id}: {unit_id} is not a Service unit"))
                elif str(unit.get("lecture_id", "")) != lecture_id:
                    findings.append(Finding("service-unit-lecture-mismatch", f"{unit_id}: section is in {lecture_id}, unit belongs to {unit.get('lecture_id')}"))
        for unit_id, unit in units_by_id.items():
            if unit.get("kind") != "service":
                continue
            lecture_id = str(unit.get("lecture_id", ""))
            lecture_section = lecture_sections.get(lecture_id)
            if lecture_section is not None and unit_id not in lecture_section[2]:
                findings.append(Finding("service-unit-not-listed-in-section", f"{unit_id}: lecture {lecture_id} does not list this Service unit in its Service section"))

    assessments_by_id: dict[str, dict[str, Any]] = {}
    assessment_surface_paths: set[str] = set()
    for assessment in _list(manifest.get("assessments")):
        if not isinstance(assessment, dict) or not _nonempty_string(assessment.get("id")):
            findings.append(Finding("invalid-assessment", "every assessment needs a string id"))
            continue
        assessment_id = str(assessment["id"])
        if assessment_id in assessments_by_id:
            findings.append(Finding("duplicate-assessment", f"duplicate assessment: {assessment_id}"))
        assessments_by_id[assessment_id] = assessment
        assessment_sequence = assessment.get("sequence")
        if not isinstance(assessment_sequence, (int, float)):
            findings.append(Finding("missing-assessment-sequence", f"{assessment_id}: numeric sequence is required"))

        assessment_source = assessment.get("source")
        _validate_exact_slice(
            owner=f"{assessment_id} source",
            evidence=assessment_source,
            root=content_root,
            file_cache=file_cache,
            findings=findings,
            minimum_length=1,
        )
        if isinstance(assessment_source, dict) and _nonempty_string(assessment_source.get("path")):
            assessment_surface_paths.add(str(assessment_source["path"]).replace("\\", "/"))

        requirements = _list(assessment.get("requirements"))
        links = set(str(item) for item in _list(assessment.get("lecture_links")))
        if not requirements:
            findings.append(Finding("missing-assessment-requirements", f"{assessment_id}: at least one prerequisite is required"))
        for requirement in requirements:
            requirement_id = str(requirement)
            if requirement_id in assumptions_by_id:
                continue
            unit = units_by_id.get(requirement_id)
            if unit is None:
                findings.append(Finding("unknown-assessment-requirement", f"{assessment_id}: unknown requirement {requirement_id}"))
                continue
            if requirement_id not in links:
                findings.append(Finding("missing-lecture-link", f"{assessment_id}: missing lecture link for {requirement_id}"))
            unit_sequence = unit.get("sequence")
            if isinstance(unit_sequence, (int, float)) and isinstance(assessment_sequence, (int, float)) and unit_sequence >= assessment_sequence:
                findings.append(Finding("learning-unit-not-prior", f"{assessment_id}: {requirement_id} is not taught before assessment"))

        for key in ("services", "artifact_types", "integration_patterns"):
            if key not in assessment or not isinstance(assessment.get(key), list):
                findings.append(Finding("missing-assessment-inventory-field", f"{assessment_id}: {key} must be present as a list, even when empty"))

        requirement_set = set(str(item) for item in requirements)
        for service in _list(assessment.get("services")):
            unit_ids = subject_to_units.get(str(service), [])
            if not unit_ids:
                findings.append(Finding("uncovered-assessed-service", f"{assessment_id}: no service unit for {service}"))
            elif not any(unit_id in requirement_set for unit_id in unit_ids):
                findings.append(Finding("unbound-assessed-service", f"{assessment_id}: service {service} is not listed in requirements"))
        if strict_service_curriculum:
            curriculum_links_value = assessment.get("service_curriculum_links")
            if not isinstance(curriculum_links_value, list):
                findings.append(
                    Finding(
                        "missing-assessment-service-curriculum-links",
                        f"{assessment_id}: service_curriculum_links must be present as a list",
                    )
                )
                curriculum_links: set[str] = set()
            else:
                curriculum_links = {str(value) for value in curriculum_links_value}
            assessed_services = {str(value) for value in _list(assessment.get("services"))}
            expected_curriculum_links = {
                curriculum_subject_to_unit[subject]
                for subject in assessed_services
                if subject in curriculum_subject_to_unit
            }
            for subject in assessed_services:
                curriculum_unit_id = curriculum_subject_to_unit.get(subject)
                if curriculum_unit_id is None:
                    findings.append(
                        Finding(
                            "uncovered-assessed-service-curriculum",
                            f"{assessment_id}: no comprehensive Service curriculum unit for {subject}",
                        )
                    )
                elif curriculum_unit_id not in curriculum_links:
                    findings.append(
                        Finding(
                            "unbound-assessed-service-curriculum",
                            f"{assessment_id}: comprehensive Service unit {curriculum_unit_id} is not linked",
                        )
                    )
            for curriculum_unit_id in curriculum_links:
                curriculum_unit = curriculum_units_by_id.get(curriculum_unit_id)
                if curriculum_unit is None:
                    findings.append(
                        Finding(
                            "unknown-assessment-service-curriculum-link",
                            f"{assessment_id}: unknown comprehensive Service unit {curriculum_unit_id}",
                        )
                    )
                    continue
                if curriculum_unit_id not in expected_curriculum_links:
                    findings.append(
                        Finding(
                            "unrelated-assessment-service-curriculum-link",
                            f"{assessment_id}: {curriculum_unit_id} does not match an assessed Service",
                        )
                    )
                curriculum_sequence = curriculum_unit.get("sequence")
                if (
                    isinstance(curriculum_sequence, (int, float))
                    and isinstance(assessment_sequence, (int, float))
                    and curriculum_sequence >= assessment_sequence
                ):
                    findings.append(
                        Finding(
                            "service-curriculum-not-prior",
                            f"{assessment_id}: {curriculum_unit_id} is not taught before assessment",
                        )
                    )
        if strict_named_service_entries:
            named_services_value = assessment.get("named_services")
            service_entry_links_value = assessment.get("service_entry_links")
            if not isinstance(named_services_value, list):
                findings.append(Finding("missing-assessment-named-services", f"{assessment_id}: named_services must be present as a list"))
                named_services: set[str] = set()
            else:
                named_services = {str(value) for value in named_services_value}
                if len(named_services) != len(named_services_value):
                    findings.append(Finding("duplicate-assessment-named-service", f"{assessment_id}: named_services must be unique"))
            if not isinstance(service_entry_links_value, list):
                findings.append(Finding("missing-assessment-service-entry-links", f"{assessment_id}: service_entry_links must be present as a list"))
                service_entry_links: set[str] = set()
            else:
                service_entry_links = {str(value) for value in service_entry_links_value}
                if len(service_entry_links) != len(service_entry_links_value):
                    findings.append(Finding("duplicate-assessment-service-entry-link", f"{assessment_id}: service_entry_links must be unique"))

            expected_service_entry_links: set[str] = set()
            for name in named_services:
                entry_id = service_entry_name_to_id.get(name)
                if entry_id is None:
                    findings.append(Finding("uncovered-assessment-named-service", f"{assessment_id}: no named Service entry for {name}"))
                else:
                    expected_service_entry_links.add(entry_id)
            if service_entry_links != expected_service_entry_links:
                findings.append(Finding("assessment-service-entry-binding-mismatch", f"{assessment_id}: named_services and service_entry_links differ"))
            for entry_id in service_entry_links:
                entry = service_entries_by_id.get(entry_id)
                if entry is None:
                    findings.append(Finding("unknown-assessment-service-entry-link", f"{assessment_id}: unknown named Service entry {entry_id}"))
                    continue
                entry_sequence = entry.get("sequence")
                if (
                    isinstance(entry_sequence, (int, float))
                    and isinstance(assessment_sequence, (int, float))
                    and entry_sequence >= assessment_sequence
                ):
                    findings.append(Finding("service-entry-not-prior", f"{assessment_id}: {entry_id} is not taught before assessment"))
        for artifact_type in _list(assessment.get("artifact_types")):
            unit_id = artifact_to_unit.get(str(artifact_type))
            if unit_id is None:
                findings.append(Finding("uncovered-assessed-artifact", f"{assessment_id}: no artifact unit for {artifact_type}"))
            elif unit_id not in requirement_set:
                findings.append(Finding("unbound-assessed-artifact", f"{assessment_id}: artifact {artifact_type} is not listed in requirements"))
        for pattern in _list(assessment.get("integration_patterns")):
            unit_id = pattern_to_unit.get(str(pattern))
            if unit_id is None:
                findings.append(Finding("uncovered-assessed-integration", f"{assessment_id}: no integration unit for {pattern}"))
            elif unit_id not in requirement_set:
                findings.append(Finding("unbound-assessed-integration", f"{assessment_id}: integration {pattern} is not listed in requirements"))

    if strict_service_mention_links:
        mention_surface_paths = set(lecture_relative_paths.values()) | assessment_surface_paths
        if not mention_surface_paths:
            findings.append(Finding("service-mention-surfaces-required", "strict Service mention validation requires lecture and assessment pages"))
        for relative_path in sorted(mention_surface_paths):
            surface = _resolve_content_path(content_root, relative_path)
            if surface is None:
                findings.append(Finding("invalid-service-mention-surface", f"Service mention page is outside content root: {relative_path}"))
                continue
            if not surface.is_file():
                findings.append(Finding("missing-service-mention-surface", f"Service mention page does not exist: {relative_path}"))
                continue
            if surface.suffix.lower() not in {".md", ".markdown", ".html", ".htm"}:
                findings.append(Finding("unsupported-service-mention-surface", f"Service mention page must be Markdown or HTML: {relative_path}"))
                continue
            if surface not in file_cache:
                file_cache[surface] = _normalize(surface.read_text(encoding="utf-8-sig"))
            _validate_service_mentions(
                surface_path=relative_path,
                text=file_cache[surface],
                alias_to_entry=service_alias_to_entry,
                entries_by_id=service_entries_by_id,
                findings=findings,
            )

    assessment_policy = manifest.get("assessment_policy")
    expected_count = assessment_policy.get("expected_count") if isinstance(assessment_policy, dict) else None
    if not isinstance(expected_count, int) or expected_count < 1:
        findings.append(Finding("invalid-expected-assessment-count", "assessment_policy.expected_count must be a positive integer"))
    elif expected_count != len(assessments_by_id):
        findings.append(Finding("assessment-count-mismatch", f"expected {expected_count} assessments, found {len(assessments_by_id)}"))

    inventory_paths = [Path(path).resolve() for path in question_jsonl]
    if require_assessment_inventory and not inventory_paths:
        findings.append(Finding("assessment-inventory-required", "strict validation requires at least one canonical question JSONL"))
    if inventory_paths:
        inventory_ids = _read_question_ids(inventory_paths, findings)
        assessment_ids = set(assessments_by_id)
        if inventory_ids != assessment_ids:
            findings.append(
                Finding(
                    "assessment-inventory-mismatch",
                    f"manifest/question ID mismatch missing={sorted(inventory_ids - assessment_ids)} extra={sorted(assessment_ids - inventory_ids)}",
                )
            )

    return findings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--content-root", required=True, type=Path)
    parser.add_argument("--question-jsonl", action="append", default=[], type=Path)
    parser.add_argument("--require-assessment-inventory", action="store_true")
    parser.add_argument("--lecture-jsonl", action="append", default=[], type=Path)
    parser.add_argument("--require-service-sections", action="store_true")
    parser.add_argument("--navigation-jsonl", action="append", default=[], type=Path)
    parser.add_argument("--require-service-curriculum", action="store_true")
    parser.add_argument("--service-entry-jsonl", action="append", default=[], type=Path)
    parser.add_argument("--require-named-service-entries", action="store_true")
    parser.add_argument("--require-service-mention-links", action="store_true")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    findings = validate_manifest(
        args.manifest,
        args.content_root,
        args.question_jsonl,
        args.require_assessment_inventory,
        args.lecture_jsonl,
        args.require_service_sections,
        args.navigation_jsonl,
        args.require_service_curriculum,
        args.service_entry_jsonl,
        args.require_named_service_entries,
        args.require_service_mention_links,
    )
    if findings:
        for finding in findings:
            print(f"ERROR [{finding.code}] {finding.message}")
        print(f"Learning contract validation failed: {len(findings)} error(s)")
        return 1
    print(
        "Learning contract validation passed: prerequisite closure, top-level Service curriculum, "
        "in-lecture Service sections, named-Service mention links, and learner-visible evidence are complete"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
