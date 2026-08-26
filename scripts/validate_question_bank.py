#!/usr/bin/env python3
"""Validate a normalized IT-certification question bank JSONL."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import median
from typing import Any, Iterable
from urllib.parse import urlparse


REQUIRED_FIELDS = (
    "id",
    "objective",
    "difficulty",
    "cognitive_type",
    "stem",
    "options",
    "correct",
    "correct_explanation",
    "wrong_explanations",
    "links",
)
COMPLETE_REVIEW_STATUSES = {"PASS", "FIXED"}
QUESTION_TYPE_ALIASES = {
    "single": "single_choice",
    "single-choice": "single_choice",
    "single_choice": "single_choice",
    "mc": "single_choice",
    "multiple": "multiple_response",
    "multiple-response": "multiple_response",
    "multiple_response": "multiple_response",
    "mr": "multiple_response",
    "true-false": "true_false",
    "true_false": "true_false",
    "ordering": "ordering",
    "matching": "matching",
}
STANDARD_QUESTION_TOTALS = {
    "associate-equivalent": 500,
    "professional-equivalent": 1000,
}
COURSE_COUNT_MODES = {
    "standard",
    "user-specified-total",
    "user-specified-increment",
    "retained-overage",
    "scope-exempt-existing",
}
COURSE_WORK_MODES = {"new", "existing"}
ARTIFACT_TYPES = {
    "code",
    "command",
    "configuration",
    "structured_data",
    "table_io",
    "logs_metrics",
    "diagram_ui",
}
MAX_ARTIFACT_SOURCE_LINE_LENGTH = 100
ARTIFACT_SELECTION_TASK = "select_correct_artifact"
ARTIFACT_VALIDATION_METHODS = {
    "shared_fixture",
    "schema_or_dry_run",
    "derived_result_check",
}
ARTIFACT_STEM_SCENARIO_FIELDS = (
    "context",
    "input_or_state",
    "expected_observation",
)
MIN_ARTIFACT_BINDING_LENGTH = 4
ARTIFACT_EVIDENCE_KINDS = {
    "exam_guide",
    "official_sample",
    "official_practice",
    "user_observation",
}
ARTIFACT_EVIDENCE_STATUSES = {
    "current",
    "outdated",
    "login_required",
    "not_found",
    "reported",
}
ARTIFACT_CODE_SIGNAL_PATTERN = re.compile(
    r"(?:\b(?:SELECT|WITH|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|MERGE|def|class|return|import|from|if|for|while|try|except|lambda|function|public|private|new)\b"
    r"|\b[A-Za-z_][\w.]*\s*\([^\n)]*\)"
    r"|\b[A-Za-z_][\w.]*\s*=(?!=)"
    r"|=>|->|==|!=|<=|>=|&&|\|\|)",
    re.IGNORECASE,
)
ARTIFACT_COMMAND_SIGNAL_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:\$|>|PS>\s*)?[A-Za-z][\w.-]*(?:\s+--?[\w-]+|\s+[A-Za-z0-9_./:-]+)",
)
ARTIFACT_KEY_VALUE_PATTERN = re.compile(
    r"(?:^|\n)\s*[\"']?[A-Za-z_][\w.-]*[\"']?\s*[:=]\s*\S+",
)
ARTIFACT_LOG_SIGNAL_PATTERN = re.compile(
    r"(?:\b(?:TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL)\b|\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}|\b[A-Za-z_][\w.-]*\s*[=:]\s*-?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
MARKDOWN_FENCE_PATTERN = re.compile(
    r"^\s*```(?P<language>[A-Za-z0-9_+.-]*)\s*\n(?P<body>.*)\n```\s*$",
    re.DOTALL,
)
MERMAID_DECLARATION_PATTERN = re.compile(
    r"^\s*(?:flowchart|graph|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|journey|gantt|pie|mindmap|timeline|quadrantChart|xychart-beta)\b",
    re.IGNORECASE,
)
DECORATIVE_WRAPPER_FIELD_PATTERN = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?[\"']?(services|operations|controls|flow)[\"']?\s*:",
)
DEFAULT_CUE_TERMS = (
    "必ず",
    "絶対",
    "常に",
    "のみ",
    "決して",
    "always",
    "never",
    "must",
    "only",
)
DEFAULT_FORBIDDEN_EXPLANATIONS = (
    "要件を満たさない",
    "要件を満たさず",
    "リスクが増える",
    "リスクが増えます",
    "条件に合わない",
    "条件に合わず",
    "不正解です",
    "不正解である",
    "does not meet the requirements",
    "increases risk",
    "incorrect",
    "not correct",
)
BOILERPLATE_CONNECTORS = (
    "この選択肢は",
    "その選択肢は",
    "当該選択肢は",
    "この回答は",
    "その回答は",
    "当該回答は",
    "この内容は",
    "その内容は",
    "当該内容は",
    "thisoption",
    "thatoption",
    "thisanswer",
    "thatanswer",
    "thisresponse",
    "thatresponse",
    "という",
    "こと",
    "そのため",
    "したがって",
    "さらに",
    "そして",
    "また",
    "かつ",
    "ためです",
    "ため",
    "ので",
    "から",
    "理由です",
    "理由",
    "です",
    "ます",
    "であり",
    "and",
    "also",
    "therefore",
    "because",
    "so",
)
MIN_BOILERPLATE_RESIDUE_LENGTH = 12
UNRESOLVED_PLACEHOLDER_PATTERN = re.compile(
    r"(?:"
    r"\b(?:TODO|TBD|FIXME|REPLACE_ME|INSERT_HERE|PLACEHOLDER)\b"
    r"|__PLACEHOLDER__"
    r"|\{\{\s*(?:TODO|TBD|FIXME|PLACEHOLDER|REPLACE|INSERT|ここに|未設定|要置換)[^{}\n]*\}\}"
    r"|\$\{\s*(?:TODO|TBD|FIXME|PLACEHOLDER|REPLACE|INSERT|未設定|要置換)[^{}\n]*\}"
    r"|\[\[\s*(?:TODO|TBD|FIXME|PLACEHOLDER|REPLACE|INSERT|ここに|未設定|要置換)[^\]\n]*\]\]"
    r"|(?:ここに|後で)(?:入力|記入|作成|置換)"
    r")",
    re.IGNORECASE,
)
HTML_TAG_PATTERN = re.compile(
    r"</?(?:a|abbr|aside|b|blockquote|br|code|dd|details|div|dl|dt|em|figcaption|figure|h[1-6]|hr|i|img|kbd|li|mark|ol|p|pre|s|small|span|strong|sub|summary|sup|table|tbody|td|tfoot|th|thead|tr|u|ul)\b[^>]*>",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class TextEntry:
    question_id: str
    label: str
    exact_normalized: str
    fuzzy_normalized: str
    grams: frozenset[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("questions", type=Path, help="UTF-8 JSONL question export")
    parser.add_argument("--targets", type=Path, help="JSON with total, course count policy, objective, question-type, difficulty, cognitive-type, and artifact targets")
    parser.add_argument("--require-metadata-targets", action="store_true", help="require allowed/count targets for question type, difficulty, and cognitive type")
    parser.add_argument("--require-course-count-policy", action="store_true", help="require question-set metadata and validate practice-bank level/count policy")
    parser.add_argument(
        "--require-question-source-profile",
        action="store_true",
        help=(
            "require a pre-authoring source profile with question-format and decision-pattern distributions, "
            "official and observed scope analysis, and independent stem/option artifact counts and rates"
        ),
    )
    parser.add_argument(
        "--require-artifact-policy",
        action="store_true",
        help=(
            "require official evidence and source-profile minimums for native, readable "
            "option-artifact questions with artifact-specific stem and explanation bindings on "
            "every assessment surface; enforce artifact_target_ratio only when explicitly declared"
        ),
    )
    parser.add_argument("--review-ledger", type=Path, help="semantic CSV with id,status,reviewer,notes[,question_hash]")
    parser.add_argument("--independent-review-ledger", type=Path, help="independent review CSV with the same columns")
    parser.add_argument("--require-independent-review", action="store_true")
    parser.add_argument("--require-review-hashes", action="store_true")
    parser.add_argument("--hash-report", type=Path, help="write current id,question_hash CSV")
    parser.add_argument("--baseline-hash-report", type=Path, help="pre-change CSV produced by --hash-report")
    parser.add_argument("--baseline-change-log", type=Path, help="CSV with id,action,reason,approval_ref for changed or removed baseline questions")
    parser.add_argument("--require-baseline-protection", action="store_true", help="require a baseline hash report and account for every changed or removed baseline question")
    parser.add_argument("--allowlist", type=Path, help="CSV with kind,id1[,label1],id2[,label2],reason")
    parser.add_argument("--require-sources", action="store_true")
    parser.add_argument("--official-source-host", action="append", default=[], help="allowed official host; repeatable")
    parser.add_argument("--max-source-age-days", type=int, help="warn when source_reviewed_at is older")
    parser.add_argument("--check-answer-cues", action="store_true")
    parser.add_argument("--cue-term", action="append", default=[], help="additional lexical cue; repeatable")
    parser.add_argument("--placeholder-pattern", action="append", default=[], help="additional unresolved-placeholder regex; repeatable")
    parser.add_argument("--forbidden-explanation", action="append", default=[], help="additional boilerplate explanation fragment; repeatable")
    parser.add_argument("--length-cue-ratio", type=float, default=1.50)
    parser.add_argument("--length-cue-min-difference", type=int, default=20)
    parser.add_argument("--length-cue-share", type=float, default=0.30)
    parser.add_argument("--cue-min-occurrences", type=int, default=5)
    parser.add_argument("--cue-dominance", type=float, default=0.90)
    parser.add_argument("--answer-position-min-cohort", type=int, default=8)
    parser.add_argument("--stem-similarity", type=float, default=0.82)
    parser.add_argument("--explanation-similarity", type=float, default=0.90)
    parser.add_argument("--min-correct-explanation", type=int, default=80)
    parser.add_argument("--min-wrong-explanation", type=int, default=50)
    parser.add_argument("--fail-on-warnings", action="store_true")
    parser.add_argument("--max-findings", type=int, default=200)
    return parser.parse_args()


def _replace_operators(value: str) -> str:
    replacements = (
        (r"!=", " notequal "),
        (r"==", " equal "),
        (r"<=", " lessequal "),
        (r">=", " greaterequal "),
        (r"<", " less "),
        (r">", " greater "),
        (r"=", " equal "),
    )
    text = value
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text


def _normalized_characters(value: str) -> str:
    return "".join(
        character
        for character in value
        if character.isalnum() or unicodedata.category(character).startswith("M")
    )


def normalize_exact_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).casefold()
    text = HTML_TAG_PATTERN.sub(" ", text)
    text = re.sub(r"https?://\S+", " url ", text)
    text = _replace_operators(text)
    return _normalized_characters(text)


def normalize_text(value: str) -> str:
    """Normalize for fuzzy similarity while preserving semantic operators."""
    text = unicodedata.normalize("NFKC", value).casefold()
    text = HTML_TAG_PATTERN.sub(" ", text)
    text = re.sub(r"https?://\S+", " url ", text)
    text = _replace_operators(text)
    text = re.sub(r"\d+(?:[.,]\d+)*", " 0 ", text)
    return _normalized_characters(text)


def visible_length(value: str) -> int:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    text = HTML_TAG_PATTERN.sub("", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    text = re.sub(r"[`*_#\[\](){}|~-]", "", text)
    return len("".join(character for character in text if not character.isspace()))


def char_ngrams(value: str, size: int = 5) -> frozenset[str]:
    if not value:
        return frozenset()
    if len(value) <= size:
        return frozenset({value})
    return frozenset(value[index : index + size] for index in range(len(value) - size + 1))


def make_text_entry(question_id: str, label: str, value: str) -> TextEntry:
    fuzzy = normalize_text(value)
    return TextEntry(question_id, label, normalize_exact_text(value), fuzzy, char_ngrams(fuzzy))


def similarity(left: TextEntry, right: TextEntry) -> float:
    if not left.grams or not right.grams:
        return 0.0
    intersection = len(left.grams & right.grams)
    union = len(left.grams | right.grams)
    return intersection / union if union else 0.0


def normalize_question_type(value: Any) -> str:
    raw = str(value).strip().casefold().replace(" ", "_")
    return QUESTION_TYPE_ALIASES.get(raw, raw.replace("-", "_"))


def resolved_question_type(question: dict[str, Any]) -> str:
    if isinstance(question.get("question_type"), str) and question["question_type"].strip():
        return normalize_question_type(question["question_type"])
    correct = question.get("correct")
    if isinstance(correct, list):
        return "multiple_response"
    if isinstance(correct, dict):
        return "matching"
    return "single_choice"


def normalized_response(value: Any, question_type: str) -> Any:
    if question_type == "multiple_response" and isinstance(value, list):
        return sorted(str(item) for item in value)
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, dict):
        return {str(key): str(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    return str(value)


def _canonicalize_hash_value(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))
    if isinstance(value, list):
        return [_canonicalize_hash_value(item) for item in value]
    if isinstance(value, dict):
        return {
            unicodedata.normalize("NFC", str(key)): _canonicalize_hash_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    return value


def canonical_question(question: dict[str, Any]) -> bytes:
    payload = {key: value for key, value in question.items() if not key.startswith("_")}
    if resolved_question_type(question) == "multiple_response" and isinstance(payload.get("correct"), list):
        payload["correct"] = sorted(unicodedata.normalize("NFC", str(item)) for item in payload["correct"])
        if isinstance(payload.get("rendered_correct"), list):
            payload["rendered_correct"] = sorted(unicodedata.normalize("NFC", str(item)) for item in payload["rendered_correct"])
    canonical = _canonicalize_hash_value(payload)
    rendered = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return rendered.encode("utf-8")


def question_hash(question: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_question(question)).hexdigest()
    return f"sha256:qbank-v1:{digest}"


def load_jsonl(path: Path, findings: list[Finding]) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        findings.append(Finding("ERROR", "invalid-encoding", f"{path}: expected UTF-8: {error}"))
        return questions
    except OSError as error:
        findings.append(Finding("ERROR", "questions-unreadable", f"{path}: {error}"))
        return questions
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            value = json.loads(raw_line)
        except json.JSONDecodeError as error:
            findings.append(Finding("ERROR", "invalid-json", f"line {line_number}: {error}"))
            continue
        if not isinstance(value, dict):
            findings.append(Finding("ERROR", "invalid-record", f"line {line_number}: object required"))
            continue
        value["_line"] = line_number
        questions.append(value)
    return questions


def load_allowlist(path: Path | None, findings: list[Finding]) -> set[tuple[str, str, str, str, str]]:
    allowed: set[tuple[str, str, str, str, str]] = set()
    if path is None:
        return allowed
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        findings.append(Finding("ERROR", "invalid-allowlist-encoding", f"{path}: expected UTF-8: {error}"))
        return allowed
    except OSError as error:
        findings.append(Finding("ERROR", "invalid-allowlist", f"{path}: {error}"))
        return allowed
    reader = csv.DictReader(io.StringIO(text, newline=""))
    required = {"kind", "id1", "id2", "reason"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        findings.append(Finding("ERROR", "invalid-allowlist", "allowlist columns must be kind,id1,id2,reason"))
        return allowed
    for row_number, row in enumerate(reader, start=2):
        kind = csv_cell(row, "kind").lower()
        id1 = csv_cell(row, "id1")
        id2 = csv_cell(row, "id2")
        label1 = csv_cell(row, "label1")
        label2 = csv_cell(row, "label2")
        reason = csv_cell(row, "reason")
        if kind not in {"stem", "explanation"} or not id1 or not id2 or not reason:
            findings.append(Finding("ERROR", "invalid-allowlist-row", f"allowlist line {row_number} is incomplete"))
            continue
        if kind == "stem":
            label1 = label1 or "stem"
            label2 = label2 or "stem"
            if label1 != "stem" or label2 != "stem":
                findings.append(Finding("ERROR", "invalid-allowlist-row", f"allowlist line {row_number}: stem labels must both be 'stem'"))
                continue
        elif not label1 or not label2:
            findings.append(Finding("ERROR", "invalid-allowlist-row", f"allowlist line {row_number}: explanation rows require label1 and label2"))
            continue
        first, second = sorted(((id1, label1), (id2, label2)))
        allowed.add((kind, first[0], first[1], second[0], second[1]))
    return allowed


def is_allowed(
    kind: str,
    left: TextEntry,
    right: TextEntry,
    allowed: set[tuple[str, str, str, str, str]],
) -> bool:
    first, second = sorted(((left.question_id, left.label), (right.question_id, right.label)))
    return (kind, first[0], first[1], second[0], second[1]) in allowed


def csv_cell(row: dict[str, str | None], key: str) -> str:
    value = row.get(key)
    return value.strip() if isinstance(value, str) else ""


def reviewer_identity(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalized.split())


def validate_text_hygiene(
    question_id: str,
    label: str,
    value: str,
    args: argparse.Namespace,
    findings: list[Finding],
    *,
    explanation: bool = False,
) -> None:
    patterns: tuple[re.Pattern[str], ...] = getattr(
        args, "compiled_placeholder_patterns", (UNRESOLVED_PLACEHOLDER_PATTERN,)
    )
    for pattern in patterns:
        if pattern.search(value):
            findings.append(Finding("ERROR", "unresolved-placeholder", f"{question_id}/{label}: unresolved placeholder matches {pattern.pattern!r}"))
            break
    if explanation:
        forbidden: tuple[str, ...] = getattr(
            args,
            "normalized_forbidden_explanations",
            tuple(sorted((normalize_exact_text(item) for item in DEFAULT_FORBIDDEN_EXPLANATIONS), key=len, reverse=True)),
        )
        residue = normalize_exact_text(value)
        matched_forbidden = False
        for phrase in forbidden:
            if phrase and phrase in residue:
                matched_forbidden = True
                residue = residue.replace(phrase, "")
        if matched_forbidden:
            for connector in sorted((normalize_exact_text(item) for item in BOILERPLATE_CONNECTORS), key=len, reverse=True):
                if connector:
                    residue = residue.replace(connector, "")
        if matched_forbidden and len(residue) <= MIN_BOILERPLATE_RESIDUE_LENGTH:
            findings.append(Finding("ERROR", "forbidden-boilerplate", f"{question_id}/{label}: explanation is only a forbidden boilerplate phrase"))


def validate_nested_text_hygiene(
    question_id: str,
    label: str,
    value: Any,
    args: argparse.Namespace,
    findings: list[Finding],
) -> None:
    if isinstance(value, str):
        validate_text_hygiene(question_id, label, value, args, findings)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            validate_nested_text_hygiene(question_id, f"{label}-{index}", item, args, findings)
    elif isinstance(value, dict):
        for key, item in value.items():
            validate_nested_text_hygiene(question_id, f"{label}-{key}", item, args, findings)


def _validate_correct(
    question_id: str,
    question_type: str,
    correct: Any,
    option_keys: set[str],
    findings: list[Finding],
) -> set[str] | None:
    if question_type == "single_choice":
        if not isinstance(correct, str) or correct not in option_keys:
            findings.append(Finding("ERROR", "invalid-correct", f"{question_id}: single_choice correct must be one option key"))
            return None
        return {correct}
    if question_type == "true_false":
        if len(option_keys) != 2 or not isinstance(correct, str) or correct not in option_keys:
            findings.append(Finding("ERROR", "invalid-correct", f"{question_id}: true_false requires exactly 2 options and one correct key"))
            return None
        return {correct}
    if question_type == "multiple_response":
        if not isinstance(correct, list) or len(correct) < 2:
            findings.append(Finding("ERROR", "invalid-correct", f"{question_id}: multiple_response correct must be a list with at least 2 keys"))
            return None
        keys = [str(item) for item in correct]
        if len(keys) != len(set(keys)) or not set(keys).issubset(option_keys) or set(keys) == option_keys:
            findings.append(Finding("ERROR", "invalid-correct", f"{question_id}: multiple_response keys must be unique option keys and leave at least one distractor"))
            return None
        return set(keys)
    if question_type == "ordering":
        if not isinstance(correct, list):
            findings.append(Finding("ERROR", "invalid-correct", f"{question_id}: ordering correct must be an ordered list"))
            return None
        keys = [str(item) for item in correct]
        if len(keys) != len(set(keys)) or set(keys) != option_keys:
            findings.append(Finding("ERROR", "invalid-correct", f"{question_id}: ordering must contain every option key exactly once"))
            return None
        return set(keys)
    if question_type == "matching":
        if not isinstance(correct, dict):
            findings.append(Finding("ERROR", "invalid-correct", f"{question_id}: matching correct must be an object"))
            return None
        mapping = {str(key): value for key, value in correct.items()}
        if set(mapping) != option_keys or any(not isinstance(value, str) or not value.strip() for value in mapping.values()):
            findings.append(Finding("ERROR", "invalid-correct", f"{question_id}: matching must map every option key to non-empty text"))
            return None
        normalized_destinations = {normalize_exact_text(value) for value in mapping.values()}
        if len(mapping) > 1 and len(normalized_destinations) < 2:
            findings.append(Finding("ERROR", "degenerate-matching", f"{question_id}: matching must use at least two distinct destinations"))
            return None
        return set(mapping)
    findings.append(Finding("ERROR", "unsupported-question-type", f"{question_id}: unsupported question_type {question_type!r}"))
    return None


def validate_structure(
    questions: list[dict[str, Any]], args: argparse.Namespace, findings: list[Finding]
) -> tuple[list[dict[str, Any]], list[TextEntry], list[TextEntry]]:
    valid: list[dict[str, Any]] = []
    stems: list[TextEntry] = []
    explanations: list[TextEntry] = []
    seen_ids: set[str] = set()

    for question in questions:
        line = question.get("_line", "?")
        missing = [field for field in REQUIRED_FIELDS if field not in question]
        if missing:
            findings.append(Finding("ERROR", "missing-field", f"line {line}: missing {', '.join(missing)}"))
            continue

        question_id = str(question["id"]).strip()
        if not question_id:
            findings.append(Finding("ERROR", "empty-id", f"line {line}: id is empty"))
            continue
        if question_id in seen_ids:
            findings.append(Finding("ERROR", "duplicate-id", f"{question_id}: duplicate id"))
            continue
        seen_ids.add(question_id)

        scalar_fields = ("objective", "difficulty", "cognitive_type", "stem", "correct_explanation")
        for field in scalar_fields:
            if not isinstance(question[field], str) or not question[field].strip():
                findings.append(Finding("ERROR", "empty-field", f"{question_id}: {field} must be non-empty text"))
        if isinstance(question["stem"], str):
            validate_text_hygiene(question_id, "stem", question["stem"], args, findings)

        options = question["options"]
        wrong = question["wrong_explanations"]
        if not isinstance(options, dict) or len(options) < 2:
            findings.append(Finding("ERROR", "invalid-options", f"{question_id}: options must be an object with at least 2 entries"))
            continue
        raw_option_keys = [str(key) for key in options]
        option_keys = set(raw_option_keys)
        normalized_labels = [unicodedata.normalize("NFKC", key).strip().casefold() for key in raw_option_keys]
        if any(not key or key != key.strip() for key in raw_option_keys):
            findings.append(Finding("ERROR", "invalid-option-label", f"{question_id}: option labels must be non-empty and unpadded"))
        if len(normalized_labels) != len(set(normalized_labels)):
            findings.append(Finding("ERROR", "option-label-collision", f"{question_id}: option labels collide after normalization"))
        if any(not isinstance(value, str) or not value.strip() for value in options.values()):
            findings.append(Finding("ERROR", "empty-option", f"{question_id}: every option must contain text"))
        for key, value in options.items():
            if isinstance(value, str):
                validate_text_hygiene(question_id, f"option-{key}", value, args, findings)
        normalized_option_text = [normalize_exact_text(str(value)) for value in options.values()]
        if len(normalized_option_text) != len(set(normalized_option_text)):
            findings.append(Finding("ERROR", "duplicate-option-text", f"{question_id}: option text is duplicated"))

        question_type = resolved_question_type(question)
        if question_type == "multiple_response" and isinstance(question.get("selection_instruction"), str):
            validate_text_hygiene(
                question_id,
                "selection-instruction",
                question["selection_instruction"],
                args,
                findings,
            )
        if question_type == "matching":
            validate_nested_text_hygiene(question_id, "matching-target", question["correct"], args, findings)
        if "rendered_correct" in question:
            validate_nested_text_hygiene(question_id, "rendered-correct", question["rendered_correct"], args, findings)
        correct_keys = _validate_correct(question_id, question_type, question["correct"], option_keys, findings)
        if correct_keys is None:
            continue
        if question_type == "multiple_response":
            selection_instruction = question.get("selection_instruction")
            if "select_count" in question:
                select_count = question["select_count"]
                if isinstance(select_count, bool) or not isinstance(select_count, int) or select_count != len(correct_keys):
                    findings.append(Finding("ERROR", "selection-count-mismatch", f"{question_id}: select_count must equal the number of correct keys"))
            elif not isinstance(selection_instruction, str) or not selection_instruction.strip():
                findings.append(Finding("ERROR", "missing-selection-instruction", f"{question_id}: multiple_response requires select_count or a non-empty selection_instruction"))
        if "rendered_correct" in question and normalized_response(question["rendered_correct"], question_type) != normalized_response(question["correct"], question_type):
            findings.append(Finding("ERROR", "rendered-correct-mismatch", f"{question_id}: rendered_correct differs from correct"))

        if not isinstance(wrong, dict):
            findings.append(Finding("ERROR", "invalid-wrong-explanations", f"{question_id}: wrong_explanations must be an object"))
            continue
        links = question["links"]
        if not isinstance(links, list) or not links or any(not isinstance(link, str) or not link.strip() for link in links):
            findings.append(Finding("ERROR", "invalid-links", f"{question_id}: links must be a non-empty list of text links"))

        actual_wrong = {str(key) for key in wrong}
        if question_type in {"single_choice", "true_false", "multiple_response"}:
            expected_wrong = option_keys - correct_keys
            for key in sorted(expected_wrong - actual_wrong):
                findings.append(Finding("ERROR", "missing-wrong-explanation", f"{question_id}: missing explanation for {key}"))
            for key in sorted(actual_wrong - expected_wrong):
                findings.append(Finding("WARNING", "extra-wrong-explanation", f"{question_id}: unexpected explanation for {key}"))

        correct_explanation = str(question["correct_explanation"])
        validate_text_hygiene(question_id, "correct", correct_explanation, args, findings, explanation=True)
        if visible_length(correct_explanation) < args.min_correct_explanation:
            findings.append(Finding("WARNING", "short-correct-explanation", f"{question_id}: correct explanation is shorter than {args.min_correct_explanation}"))
        stems.append(make_text_entry(question_id, "stem", str(question["stem"])))
        explanations.append(make_text_entry(question_id, "correct", correct_explanation))

        for key in sorted(actual_wrong):
            explanation = wrong[key]
            if not isinstance(explanation, str) or not explanation.strip():
                findings.append(Finding("ERROR", "empty-wrong-explanation", f"{question_id}: explanation for {key} is empty"))
                continue
            validate_text_hygiene(question_id, f"wrong-{key}", explanation, args, findings, explanation=True)
            if visible_length(explanation) < args.min_wrong_explanation:
                findings.append(Finding("WARNING", "short-wrong-explanation", f"{question_id}: explanation for {key} is shorter than {args.min_wrong_explanation}"))
            explanations.append(make_text_entry(question_id, f"wrong-{key}", explanation))

        valid.append(question)

    return valid, stems, explanations


def find_similar_pairs(
    entries: list[TextEntry],
    kind: str,
    threshold: float,
    allowed: set[tuple[str, str, str, str, str]],
    findings: list[Finding],
) -> None:
    exact_groups: dict[str, list[TextEntry]] = defaultdict(list)
    for entry in entries:
        if entry.exact_normalized:
            exact_groups[entry.exact_normalized].append(entry)

    exact_pairs: set[tuple[str, str]] = set()
    for group in exact_groups.values():
        for left_index, left in enumerate(group):
            for right in group[left_index + 1 :]:
                left_key = f"{left.question_id}/{left.label}"
                right_key = f"{right.question_id}/{right.label}"
                exact_pairs.add(tuple(sorted((left_key, right_key))))
                if left.question_id != right.question_id and is_allowed(kind, left, right, allowed):
                    continue
                severity = "ERROR" if kind == "stem" else "WARNING"
                findings.append(Finding(severity, f"duplicate-{kind}", f"{left_key} and {right_key}: normalized {kind} is identical"))

    for left_index, left in enumerate(entries):
        for right in entries[left_index + 1 :]:
            if kind == "stem" and left.question_id == right.question_id:
                continue
            left_key = f"{left.question_id}/{left.label}"
            right_key = f"{right.question_id}/{right.label}"
            pair = tuple(sorted((left_key, right_key)))
            if pair in exact_pairs:
                continue
            if left.question_id != right.question_id and is_allowed(kind, left, right, allowed):
                continue
            smaller = min(len(left.grams), len(right.grams))
            larger = max(len(left.grams), len(right.grams))
            if not larger or smaller / larger < threshold:
                continue
            score = similarity(left, right)
            if score >= threshold:
                findings.append(Finding("WARNING", f"similar-{kind}", f"{left.question_id}/{left.label} and {right.question_id}/{right.label}: similarity={score:.3f}"))


def validate_category_targets(
    targets: dict[str, Any],
    target_key: str,
    question_field: str,
    code_label: str,
    questions: list[dict[str, Any]],
    required: bool,
    findings: list[Finding],
) -> None:
    raw = targets.get(target_key)
    if raw is None:
        if required:
            findings.append(Finding("ERROR", "missing-metadata-targets", f"targets.{target_key} is required"))
        return
    if not isinstance(raw, dict) or not raw:
        findings.append(Finding("ERROR", "invalid-targets", f"targets.{target_key} must be a non-empty object"))
        return
    expected: dict[str, int] = {}
    for key, count in raw.items():
        category = str(key).strip()
        if not category or isinstance(count, bool) or not isinstance(count, int) or count < 0:
            findings.append(Finding("ERROR", "invalid-targets", f"targets.{target_key} must map non-empty labels to non-negative integers"))
            return
        expected[category] = count
    actual = Counter(str(question.get(question_field, "")).strip() for question in questions)
    for category, expected_count in expected.items():
        actual_count = actual.get(category, 0)
        if actual_count != expected_count:
            findings.append(Finding("ERROR", f"{code_label}-count-mismatch", f"{category}: expected {expected_count}, found {actual_count}"))
    for category in sorted(set(actual) - set(expected)):
        findings.append(Finding("ERROR", f"unexpected-{code_label}", f"{category}: absent from targets.{target_key}"))
    if sum(expected.values()) != len(questions):
        findings.append(Finding("ERROR", f"{code_label}-target-total-mismatch", f"targets.{target_key} sums to {sum(expected.values())}, expected {len(questions)}"))


def _is_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_positive_int(value: Any) -> bool:
    return _is_non_negative_int(value) and value > 0


def validate_course_count_policy(
    targets: dict[str, Any],
    required: bool,
    official_source_hosts: Iterable[str],
    findings: list[Finding],
) -> None:
    policy_keys = {
        "question_set",
        "work_mode",
        "credential_level",
        "credential_level_source",
        "credential_level_reviewed_at",
        "count_mode",
        "requested_total",
        "baseline_total",
        "requested_increment",
    }
    if not required and not any(key in targets for key in policy_keys):
        return

    question_set = targets.get("question_set")
    if question_set not in {"practice", "mock"}:
        findings.append(Finding("ERROR", "invalid-course-count-policy", "targets.question_set must be 'practice' or 'mock'"))
        return
    if question_set == "mock":
        unexpected = sorted(key for key in policy_keys - {"question_set"} if key in targets)
        if unexpected:
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-course-count-policy",
                    f"mock targets must not contain practice-bank policy fields: {unexpected}",
                )
            )
        return

    work_mode = targets.get("work_mode")
    if work_mode not in COURSE_WORK_MODES:
        findings.append(
            Finding(
                "ERROR",
                "invalid-course-count-policy",
                f"targets.work_mode must be one of {sorted(COURSE_WORK_MODES)}",
            )
        )
        return

    credential_level = targets.get("credential_level")
    allowed_levels = {*STANDARD_QUESTION_TOTALS, "not-applicable"}
    if credential_level not in allowed_levels:
        findings.append(
            Finding(
                "ERROR",
                "invalid-course-count-policy",
                "targets.credential_level must be 'associate-equivalent', 'professional-equivalent', or 'not-applicable'",
            )
        )
        return

    credential_level_source = targets.get("credential_level_source")
    parsed_source = urlparse(credential_level_source) if isinstance(credential_level_source, str) else None
    if parsed_source is None or parsed_source.scheme != "https" or not parsed_source.netloc:
        findings.append(Finding("ERROR", "invalid-course-count-policy", "targets.credential_level_source must be an https URL"))
    else:
        source_host = (parsed_source.hostname or "").casefold().rstrip(".")
        allowed_hosts = {host.strip().casefold().rstrip(".") for host in official_source_hosts if host.strip()}
        if required and not allowed_hosts:
            findings.append(
                Finding(
                    "ERROR",
                    "official-source-host-required",
                    "--require-course-count-policy requires at least one --official-source-host for credential level evidence",
                )
            )
        if allowed_hosts and not _host_allowed(source_host, allowed_hosts):
            findings.append(
                Finding(
                    "ERROR",
                    "unofficial-credential-level-source",
                    f"credential level source host {source_host} is not an allowed official host",
                )
            )
    reviewed_at = targets.get("credential_level_reviewed_at")
    try:
        reviewed_date = date.fromisoformat(reviewed_at) if isinstance(reviewed_at, str) else None
    except ValueError:
        reviewed_date = None
    if reviewed_date is None:
        findings.append(Finding("ERROR", "invalid-course-count-policy", "targets.credential_level_reviewed_at must be YYYY-MM-DD"))
    elif reviewed_date > date.today():
        findings.append(Finding("ERROR", "invalid-course-count-policy", "targets.credential_level_reviewed_at must not be in the future"))

    count_mode = targets.get("count_mode")
    if count_mode not in COURSE_COUNT_MODES:
        findings.append(
            Finding(
                "ERROR",
                "invalid-course-count-policy",
                f"targets.count_mode must be one of {sorted(COURSE_COUNT_MODES)}",
            )
        )
        return

    total = targets.get("total")
    if not _is_positive_int(total):
        findings.append(Finding("ERROR", "invalid-course-count-policy", "targets.total must be a positive integer for a practice question bank"))
        return

    override_fields = {"requested_total", "baseline_total", "requested_increment"}
    allowed_override_fields = {
        "standard": {"baseline_total"},
        "user-specified-total": {"requested_total", "baseline_total"},
        "user-specified-increment": {"baseline_total", "requested_increment"},
        "retained-overage": {"baseline_total"},
        "scope-exempt-existing": {"baseline_total"},
    }
    unexpected = sorted(
        key for key in override_fields - allowed_override_fields[count_mode] if key in targets
    )
    if unexpected:
        findings.append(
            Finding(
                "ERROR",
                "conflicting-course-count-policy",
                f"{count_mode} mode must not contain fields {unexpected}",
            )
        )

    baseline_total = targets.get("baseline_total")
    if work_mode == "existing" and not _is_positive_int(baseline_total):
        findings.append(
            Finding(
                "ERROR",
                "invalid-course-count-policy",
                "existing work_mode requires a positive baseline_total",
            )
        )
    if work_mode == "new" and baseline_total is not None and baseline_total != 0:
        findings.append(
            Finding(
                "ERROR",
                "invalid-course-count-policy",
                "new work_mode must omit baseline_total or set it to 0",
            )
        )
    if work_mode == "new" and count_mode in {"user-specified-increment", "retained-overage", "scope-exempt-existing"}:
        findings.append(
            Finding(
                "ERROR",
                "invalid-course-count-policy",
                f"{count_mode} mode requires work_mode 'existing'",
            )
        )

    if count_mode == "standard":
        standard_total = STANDARD_QUESTION_TOTALS.get(credential_level)
        if standard_total is None:
            findings.append(Finding("ERROR", "invalid-course-count-policy", "standard mode requires an Associate- or Professional-equivalent credential"))
            return
        if total != standard_total:
            findings.append(
                Finding(
                    "ERROR",
                    "course-count-policy-mismatch",
                    f"{credential_level} standard requires {standard_total} questions, found target total {total}",
                )
            )
        if baseline_total is not None and (not _is_non_negative_int(baseline_total) or baseline_total > standard_total):
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-course-count-policy",
                    f"standard mode baseline_total must be an integer from 0 through {standard_total}",
                )
            )
        return

    if count_mode == "user-specified-total":
        requested_total = targets.get("requested_total")
        if not _is_positive_int(requested_total):
            findings.append(Finding("ERROR", "invalid-course-count-policy", "user-specified-total mode requires a positive requested_total"))
        elif total != requested_total:
            findings.append(
                Finding(
                    "ERROR",
                    "course-count-policy-mismatch",
                    f"target total {total} does not match requested_total {requested_total}",
                )
            )
        if baseline_total is not None and not _is_non_negative_int(baseline_total):
            findings.append(Finding("ERROR", "invalid-course-count-policy", "user-specified-total baseline_total must be a non-negative integer"))
        return

    if count_mode == "user-specified-increment":
        requested_increment = targets.get("requested_increment")
        if not _is_non_negative_int(baseline_total) or not _is_positive_int(requested_increment):
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-course-count-policy",
                    "user-specified-increment mode requires a non-negative baseline_total and positive requested_increment",
                )
            )
        elif total != baseline_total + requested_increment:
            findings.append(
                Finding(
                    "ERROR",
                    "course-count-policy-mismatch",
                    f"target total {total} does not equal baseline_total {baseline_total} plus requested_increment {requested_increment}",
                )
            )
        return

    if count_mode == "scope-exempt-existing":
        if not _is_positive_int(baseline_total):
            findings.append(Finding("ERROR", "invalid-course-count-policy", "scope-exempt-existing mode requires a positive baseline_total"))
        elif total != baseline_total:
            findings.append(
                Finding(
                    "ERROR",
                    "course-count-policy-mismatch",
                    f"scope-exempt-existing target total {total} must preserve baseline_total {baseline_total}",
                )
            )
        return

    standard_total = STANDARD_QUESTION_TOTALS.get(credential_level)
    if standard_total is None:
        findings.append(Finding("ERROR", "invalid-course-count-policy", "retained-overage mode requires an Associate- or Professional-equivalent credential"))
    elif not _is_positive_int(baseline_total) or baseline_total <= standard_total:
        findings.append(
            Finding(
                "ERROR",
                "invalid-course-count-policy",
                f"retained-overage mode baseline_total must be greater than the {standard_total}-question standard",
            )
        )
    elif total != baseline_total:
        findings.append(
            Finding(
                "ERROR",
                "course-count-policy-mismatch",
                f"retained-overage target total {total} must preserve baseline_total {baseline_total}",
            )
        )


def validate_targets(
    path: Path | None,
    questions: list[dict[str, Any]],
    require_metadata_targets: bool,
    require_course_count_policy: bool,
    official_source_hosts: Iterable[str],
    findings: list[Finding],
) -> dict[str, Any] | None:
    if path is None:
        severity = "ERROR" if require_metadata_targets or require_course_count_policy else "WARNING"
        findings.append(Finding(severity, "targets-not-provided", "no targets file was provided"))
        return
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            targets = json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        findings.append(Finding("ERROR", "invalid-targets", f"{path}: {error}"))
        return
    if not isinstance(targets, dict):
        findings.append(Finding("ERROR", "invalid-targets", "targets must be an object"))
        return

    validate_course_count_policy(targets, require_course_count_policy, official_source_hosts, findings)
    target_question_set = targets.get("question_set")
    if target_question_set in {"practice", "mock"}:
        for question in questions:
            question_set = question.get("question_set")
            if question_set != target_question_set:
                findings.append(
                    Finding(
                        "ERROR",
                        "question-set-mismatch",
                        f"{question.get('id', '?')}: expected question_set {target_question_set!r}, found {question_set!r}",
                    )
                )

    expected_total = targets.get("total")
    if expected_total is None:
        if require_course_count_policy:
            findings.append(Finding("ERROR", "missing-course-count-policy", "targets.total is required"))
    elif isinstance(expected_total, bool) or not isinstance(expected_total, int) or expected_total < 0:
        findings.append(Finding("ERROR", "invalid-targets", "targets.total must be a non-negative integer"))
    elif expected_total != len(questions):
        findings.append(Finding("ERROR", "total-mismatch", f"expected {expected_total} questions, found {len(questions)}"))
    expected_objectives = targets.get("objectives")
    if not isinstance(expected_objectives, dict) or not expected_objectives:
        findings.append(Finding("ERROR", "invalid-targets", "targets.objectives must be a non-empty object"))
    else:
        actual_objectives = Counter(str(question.get("objective", "")) for question in questions)
        for objective, expected_count in expected_objectives.items():
            actual_count = actual_objectives.get(str(objective), 0)
            if actual_count != expected_count:
                findings.append(Finding("ERROR", "objective-count-mismatch", f"{objective}: expected {expected_count}, found {actual_count}"))
        for objective in sorted(set(actual_objectives) - {str(key) for key in expected_objectives}):
            findings.append(Finding("ERROR", "unexpected-objective", f"{objective}: absent from targets"))

    allowed_types_raw = targets.get("allowed_question_types")
    expected_types_raw = targets.get("question_types")
    if require_metadata_targets and allowed_types_raw is None:
        findings.append(Finding("ERROR", "missing-metadata-targets", "targets.allowed_question_types is required"))
    if require_metadata_targets and expected_types_raw is None:
        findings.append(Finding("ERROR", "missing-metadata-targets", "targets.question_types is required"))
    if allowed_types_raw is not None or expected_types_raw is not None:
        for question in questions:
            if not isinstance(question.get("question_type"), str) or not question["question_type"].strip():
                findings.append(Finding("ERROR", "missing-question-type", f"{question.get('id', '?')}: question_type is required by targets"))
    actual_types = Counter(resolved_question_type(question) for question in questions)
    if allowed_types_raw is not None:
        if not isinstance(allowed_types_raw, list) or not allowed_types_raw:
            findings.append(Finding("ERROR", "invalid-targets", "targets.allowed_question_types must be a non-empty list"))
        else:
            allowed_types = {normalize_question_type(value) for value in allowed_types_raw}
            for question_type in sorted(set(actual_types) - allowed_types):
                findings.append(Finding("ERROR", "unsupported-question-type", f"{question_type}: absent from allowed_question_types"))
    if expected_types_raw is not None:
        if not isinstance(expected_types_raw, dict) or not expected_types_raw:
            findings.append(Finding("ERROR", "invalid-targets", "targets.question_types must be a non-empty object"))
        else:
            expected_types = {normalize_question_type(key): value for key, value in expected_types_raw.items()}
            for question_type, expected_count in expected_types.items():
                actual_count = actual_types.get(question_type, 0)
                if actual_count != expected_count:
                    findings.append(Finding("ERROR", "question-type-count-mismatch", f"{question_type}: expected {expected_count}, found {actual_count}"))
            for question_type in sorted(set(actual_types) - set(expected_types)):
                findings.append(Finding("ERROR", "unexpected-question-type", f"{question_type}: absent from question_types"))

    validate_category_targets(targets, "difficulties", "difficulty", "difficulty", questions, require_metadata_targets, findings)
    validate_category_targets(targets, "cognitive_types", "cognitive_type", "cognitive-type", questions, require_metadata_targets, findings)
    return targets


def _host_allowed(host: str, allowed_hosts: set[str]) -> bool:
    return any(host == allowed or host.endswith(f".{allowed}") for allowed in allowed_hosts)


def _artifact_location_text(question: dict[str, Any], location: str) -> str | None:
    if location == "stem":
        stem = question.get("stem")
        return stem if isinstance(stem, str) else None
    if location.startswith("option:"):
        option_key = location.removeprefix("option:")
        options = question.get("options")
        if isinstance(options, dict):
            option = options.get(option_key)
            return option if isinstance(option, str) else None
    return None


def _artifact_explanation_text(question: dict[str, Any], option_key: str) -> str | None:
    correct = question.get("correct")
    correct_keys = {correct} if isinstance(correct, str) else (
        {str(key) for key in correct} if isinstance(correct, list) else set()
    )
    if option_key in correct_keys:
        explanation = question.get("correct_explanation")
        return explanation if isinstance(explanation, str) else None
    wrong = question.get("wrong_explanations")
    if not isinstance(wrong, dict):
        return None
    explanation = wrong.get(option_key)
    return explanation if isinstance(explanation, str) else None


def _artifact_stem_contract_signature(question: dict[str, Any]) -> str | None:
    selection = question.get("artifact_selection")
    contract = selection.get("stem_contract") if isinstance(selection, dict) else None
    scenario = contract.get("scenario") if isinstance(contract, dict) else None
    if not isinstance(scenario, dict):
        return None
    parts: list[str] = []
    for field in ARTIFACT_STEM_SCENARIO_FIELDS:
        value = scenario.get(field)
        if not isinstance(value, str) or not value.strip():
            return None
        if field == "expected_observation":
            parts.append(value)
    constraints = scenario.get("hard_constraints")
    if (
        not isinstance(constraints, list)
        or not constraints
        or any(not isinstance(item, str) or not item.strip() for item in constraints)
    ):
        return None
    parts.extend(str(item) for item in constraints)
    axes = selection.get("decision_axes")
    if isinstance(axes, list):
        for axis in axes:
            if not isinstance(axis, dict):
                continue
            name = axis.get("name")
            if isinstance(name, str):
                parts.append(name)
            option_values = axis.get("option_values")
            if isinstance(option_values, dict):
                parts.extend(
                    str(value)
                    for _, value in sorted(option_values.items(), key=lambda pair: str(pair[0]))
                )
    validation = selection.get("validation")
    candidate_results = validation.get("candidate_results") if isinstance(validation, dict) else None
    if isinstance(candidate_results, dict):
        parts.extend(
            str(value)
            for _, value in sorted(candidate_results.items(), key=lambda pair: str(pair[0]))
        )
    signature = normalize_text("\n".join(parts))
    return signature or None


def _validate_artifact_stem_contract(
    question: dict[str, Any],
    selection: dict[str, Any],
    findings: list[Finding],
) -> bool:
    question_id = str(question.get("id", "?"))
    stem = question.get("stem")
    contract = selection.get("stem_contract")
    if not isinstance(contract, dict):
        findings.append(
            Finding(
                "ERROR",
                "missing-artifact-stem-contract",
                f"{question_id}: artifact_selection.stem_contract must bind an artifact-specific prompt and scenario to the learner-visible stem",
            )
        )
        return False

    valid = True
    artifact_request = contract.get("artifact_request")
    if (
        not isinstance(artifact_request, str)
        or len(normalize_exact_text(artifact_request)) < MIN_ARTIFACT_BINDING_LENGTH
        or not isinstance(stem, str)
        or artifact_request not in stem
    ):
        findings.append(
            Finding(
                "ERROR",
                "artifact-stem-contract-not-visible",
                f"{question_id}: stem_contract.artifact_request must be a substantive exact substring that asks the learner to select an artifact candidate",
            )
        )
        valid = False

    scenario = contract.get("scenario")
    if not isinstance(scenario, dict):
        findings.append(
            Finding(
                "ERROR",
                "missing-artifact-stem-scenario",
                f"{question_id}: stem_contract.scenario must identify context, input/state, hard constraints, and expected observation",
            )
        )
        valid = False
    else:
        for field in ARTIFACT_STEM_SCENARIO_FIELDS:
            value = scenario.get(field)
            if (
                not isinstance(value, str)
                or len(normalize_exact_text(value)) < MIN_ARTIFACT_BINDING_LENGTH
                or not isinstance(stem, str)
                or value not in stem
            ):
                findings.append(
                    Finding(
                        "ERROR",
                        "artifact-stem-scenario-not-visible",
                        f"{question_id}: stem_contract.scenario.{field} must be a substantive exact substring of the learner-visible stem",
                    )
                )
                valid = False
        constraints = scenario.get("hard_constraints")
        if not isinstance(constraints, list) or not constraints:
            findings.append(
                Finding(
                    "ERROR",
                    "missing-artifact-stem-constraints",
                    f"{question_id}: stem_contract.scenario.hard_constraints must contain at least one learner-visible constraint",
                )
            )
            valid = False
        else:
            normalized_constraints: set[str] = set()
            for index, constraint in enumerate(constraints, start=1):
                normalized = normalize_exact_text(constraint) if isinstance(constraint, str) else ""
                if (
                    not isinstance(constraint, str)
                    or len(normalized) < MIN_ARTIFACT_BINDING_LENGTH
                    or not isinstance(stem, str)
                    or constraint not in stem
                ):
                    findings.append(
                        Finding(
                            "ERROR",
                            "artifact-stem-constraint-not-visible",
                            f"{question_id}: hard_constraints[{index}] must be a substantive exact substring of the learner-visible stem",
                        )
                    )
                    valid = False
                elif normalized in normalized_constraints:
                    findings.append(
                        Finding(
                            "ERROR",
                            "duplicate-artifact-stem-constraint",
                            f"{question_id}: hard_constraints[{index}] duplicates another constraint",
                        )
                    )
                    valid = False
                else:
                    normalized_constraints.add(normalized)

    deletion_test = contract.get("deletion_test")
    if not isinstance(deletion_test, dict):
        findings.append(
            Finding(
                "ERROR",
                "missing-artifact-deletion-test",
                f"{question_id}: stem_contract.deletion_test must record the artifact-candidate deletion review",
            )
        )
        valid = False
    else:
        if deletion_test.get("artifact_candidates_required") is not True:
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-deletion-test-failed",
                    f"{question_id}: deletion_test.artifact_candidates_required must be true",
                )
            )
            valid = False
        reference = deletion_test.get("review_reference")
        if not isinstance(reference, str) or not reference.strip():
            findings.append(
                Finding(
                    "ERROR",
                    "missing-artifact-deletion-test-reference",
                    f"{question_id}: deletion_test.review_reference must identify the recorded review or fixture",
                )
            )
            valid = False
    return valid


def _artifact_fence(content: str) -> tuple[str, str]:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    match = MARKDOWN_FENCE_PATTERN.fullmatch(normalized)
    if match is None:
        return "", normalized
    return match.group("language").casefold(), match.group("body")


def _decorative_artifact_wrapper(content: str) -> str | None:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    folded = normalized.casefold()
    if re.search(r"(?im)^\s*apiVersion\s*:\s*course(?:\.|/)", normalized):
        return "a course-invented apiVersion is not a vendor or language-native artifact"
    if re.search(r"(?im)^\s*kind\s*:\s*(?:architecture|implementation|configuration|decision)candidate\b", normalized):
        return "a generic Candidate kind only serializes the prose answer"
    wrapper_fields = {match.group(1).casefold() for match in DECORATIVE_WRAPPER_FIELD_PATTERN.finditer(normalized)}
    mermaid_wrapper_fields = {
        field
        for field in ("services", "operations", "controls", "flow")
        if re.search(rf"(?i)[\"']?{field}\s*:", normalized)
    }
    if len(wrapper_fields | mermaid_wrapper_fields) >= 3:
        return "generic services/operations/controls/flow fields serialize prose instead of testing a native artifact"
    if "not-specified" in folded and (wrapper_fields or mermaid_wrapper_fields):
        return "placeholder values do not form an implementation or product artifact"
    return None


def _artifact_candidate_issues(artifact_type: str, content: str) -> list[tuple[str, str]]:
    language, body = _artifact_fence(content)
    issues: list[tuple[str, str]] = []
    for line_number, line in enumerate(body.splitlines(), start=1):
        visible_length = len(line.expandtabs(4))
        if visible_length > MAX_ARTIFACT_SOURCE_LINE_LENGTH:
            issues.append(
                (
                    "artifact-line-too-long",
                    f"line {line_number} has {visible_length} characters; split the artifact semantically at or before {MAX_ARTIFACT_SOURCE_LINE_LENGTH}",
                )
            )

    wrapper_reason = _decorative_artifact_wrapper(body)
    if wrapper_reason is not None:
        issues.append(("artifact-decorative-wrapper", wrapper_reason))

    mermaid_source = bool(MERMAID_DECLARATION_PATTERN.search(body))
    if artifact_type == "diagram_ui" and mermaid_source and language != "mermaid":
        issues.append(
            (
                "mermaid-artifact-not-renderable",
                "Mermaid source must use a mermaid fence and render as a diagram, not appear as a text/code block",
            )
        )
    if language == "mermaid" and not mermaid_source:
        issues.append(("invalid-mermaid-artifact", "mermaid fence does not start with a supported diagram declaration"))

    try:
        if language in {"python", "py"}:
            ast.parse(body)
        elif language == "json":
            json.loads(body)
    except (SyntaxError, json.JSONDecodeError) as error:
        issues.append(("artifact-native-syntax-invalid", f"{language} candidate does not parse: {error}"))
    return issues


def _has_artifact_structure(artifact_type: str, content: str) -> bool:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    if artifact_type == "code":
        return bool(ARTIFACT_CODE_SIGNAL_PATTERN.search(normalized))
    if artifact_type == "command":
        return bool(ARTIFACT_COMMAND_SIGNAL_PATTERN.search(normalized))
    if artifact_type in {"configuration", "structured_data"}:
        return bool(
            ARTIFACT_KEY_VALUE_PATTERN.search(normalized)
            or ("{" in normalized and "}" in normalized and ":" in normalized)
            or ("<" in normalized and ">" in normalized and "</" in normalized)
        )
    if artifact_type == "table_io":
        lines = [line for line in normalized.splitlines() if line.strip()]
        markdown_table = len(lines) >= 2 and "|" in lines[0] and "|" in lines[1]
        delimited_rows = len(lines) >= 2 and any(delimiter in lines[0] for delimiter in (",", "\t"))
        return markdown_table or delimited_rows
    if artifact_type == "logs_metrics":
        return bool(ARTIFACT_LOG_SIGNAL_PATTERN.search(normalized))
    if artifact_type == "diagram_ui":
        return bool(
            re.search(r"(?:```mermaid|!\[[^\]]*\]\([^)]*\)|(?:-->|==>|->)|\[[^\]]+\]\s*[-=]+)", normalized)
        )
    return False


def validate_question_artifact_evidence(
    question: dict[str, Any], findings: list[Finding]
) -> set[str]:
    """Return types backed by atomic option, stem, validation, and explanation contracts."""
    question_id = str(question.get("id", "?"))
    artifact_types = question.get("artifact_types")
    if not isinstance(artifact_types, list):
        findings.append(Finding("ERROR", "missing-artifact-types", f"{question_id}: artifact_types must be an explicit list, using [] when none"))
        return set()
    if any(not isinstance(item, str) or not item.strip() for item in artifact_types):
        findings.append(Finding("ERROR", "invalid-artifact-types", f"{question_id}: artifact_types must contain only non-empty strings"))
        return set()

    normalized_types = [item.strip() for item in artifact_types]
    if len(set(normalized_types)) != len(normalized_types):
        findings.append(Finding("ERROR", "duplicate-artifact-type", f"{question_id}: artifact_types contains duplicates"))
    unsupported = sorted(set(normalized_types) - ARTIFACT_TYPES)
    if unsupported:
        findings.append(
            Finding(
                "ERROR",
                "unsupported-artifact-type",
                f"{question_id}: unsupported artifact_types {unsupported}; allowed values are {sorted(ARTIFACT_TYPES)}",
            )
        )

    evidence = question.get("artifact_evidence")
    if not isinstance(evidence, list):
        findings.append(
            Finding(
                "ERROR",
                "missing-artifact-evidence",
                f"{question_id}: artifact_evidence must be an explicit list, using [] when artifact_types is []",
            )
        )
        return set()

    evidence_pairs: list[tuple[str, str]] = []
    valid_evidence_by_type: dict[str, dict[str, str]] = defaultdict(dict)
    for index, item in enumerate(evidence, start=1):
        label = f"{question_id}/artifact_evidence[{index}]"
        if not isinstance(item, dict):
            findings.append(Finding("ERROR", "invalid-question-artifact-evidence", f"{label} must be an object"))
            continue
        artifact_type = item.get("type")
        if not isinstance(artifact_type, str) or artifact_type not in ARTIFACT_TYPES:
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-question-artifact-evidence-type",
                    f"{label}.type must be one of {sorted(ARTIFACT_TYPES)}",
                )
            )
            continue
        location = item.get("location")
        if not isinstance(location, str) or _artifact_location_text(question, location) is None:
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-artifact-evidence-location",
                    f"{label}.location must be 'option:<existing option key>'",
                )
            )
            continue
        if not location.startswith("option:"):
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-evidence-location-not-option",
                    f"{label}.location must point to an option; stem-only artifacts do not count toward the Artifact ratio policy",
                )
            )
            continue
        option_key = location.removeprefix("option:")
        evidence_pairs.append((artifact_type, option_key))
        location_text = _artifact_location_text(question, location)
        content = item.get("content")
        if not isinstance(content, str) or not content.strip():
            findings.append(Finding("ERROR", "empty-artifact-evidence-content", f"{label}.content must be non-empty text"))
            continue
        if content not in str(location_text):
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-evidence-not-learner-visible",
                    f"{label}.content is not an exact substring of learner-visible {location}",
                )
            )
            continue
        if not _has_artifact_structure(artifact_type, content):
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-evidence-not-structural",
                    f"{label}.content does not contain recognizable {artifact_type} structure",
                )
            )
            continue
        candidate_issues = _artifact_candidate_issues(artifact_type, content)
        if candidate_issues:
            for code, message in candidate_issues:
                findings.append(Finding("ERROR", code, f"{label}: {message}"))
            continue
        decision_binding = item.get("decision_binding")
        if not isinstance(decision_binding, str) or not decision_binding.strip():
            findings.append(
                Finding(
                    "ERROR",
                    "missing-artifact-decision-binding",
                    f"{label}.decision_binding must name the line, field, operator, value, or relation needed to answer",
                )
            )
            continue
        valid_evidence_by_type[artifact_type][option_key] = content

    if len(evidence_pairs) != len(set(evidence_pairs)):
        findings.append(
            Finding(
                "ERROR",
                "duplicate-artifact-evidence-location",
                f"{question_id}: artifact_evidence contains duplicate type/location pairs",
            )
        )
    declared_valid_types = set(normalized_types) & ARTIFACT_TYPES
    evidence_type_set = {artifact_type for artifact_type, _ in evidence_pairs}
    if evidence_type_set != declared_valid_types:
        findings.append(
            Finding(
                "ERROR",
                "artifact-evidence-type-mismatch",
                f"{question_id}: artifact_types {sorted(declared_valid_types)} do not match artifact_evidence types {sorted(evidence_type_set)}",
            )
        )

    if not declared_valid_types:
        if evidence:
            findings.append(
                Finding(
                    "ERROR",
                    "unexpected-artifact-evidence",
                    f"{question_id}: artifact_evidence must be [] when artifact_types is []",
                )
            )
        if question.get("artifact_selection") is not None:
            findings.append(
                Finding(
                    "ERROR",
                    "unexpected-artifact-selection",
                    f"{question_id}: artifact_selection is only valid for an option-artifact question",
                )
            )
        return set()

    options = question.get("options")
    option_keys = {str(key) for key in options} if isinstance(options, dict) else set()
    question_type = resolved_question_type(question)
    if question_type not in {"single_choice", "multiple_response"}:
        findings.append(
            Finding(
                "ERROR",
                "artifact-selection-question-type",
                f"{question_id}: the option-artifact ratio policy only counts single_choice or multiple_response questions",
            )
        )

    complete_types: set[str] = set()
    for artifact_type in sorted(declared_valid_types):
        covered_keys = set(valid_evidence_by_type.get(artifact_type, {}))
        missing_keys = sorted(option_keys - covered_keys)
        extra_keys = sorted(covered_keys - option_keys)
        if missing_keys or extra_keys:
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-option-coverage-mismatch",
                    f"{question_id}/{artifact_type}: every option must contain a validated candidate; missing {missing_keys}, extra {extra_keys}",
                )
            )
            continue
        normalized_candidates = {
            normalize_exact_text(content)
            for content in valid_evidence_by_type.get(artifact_type, {}).values()
        }
        if len(normalized_candidates) < 2:
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-candidates-not-distinct",
                    f"{question_id}/{artifact_type}: option artifacts are identical after normalization",
                )
            )
            continue
        complete_types.add(artifact_type)

    selection = question.get("artifact_selection")
    selection_valid = True
    if not isinstance(selection, dict):
        findings.append(
            Finding(
                "ERROR",
                "missing-artifact-selection",
                f"{question_id}: artifact_selection must prove that the learner selects the correct artifact candidate",
            )
        )
        selection_valid = False
    else:
        if selection.get("task") != ARTIFACT_SELECTION_TASK:
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-artifact-selection-task",
                    f"{question_id}: artifact_selection.task must be {ARTIFACT_SELECTION_TASK!r}",
                )
            )
            selection_valid = False
        requirement = selection.get("requirement")
        if not isinstance(requirement, str) or not requirement.strip():
            findings.append(
                Finding(
                    "ERROR",
                    "missing-artifact-selection-requirement",
                    f"{question_id}: artifact_selection.requirement must state the required behavior or result",
                )
            )
            selection_valid = False
        if not _validate_artifact_stem_contract(question, selection, findings):
            selection_valid = False

        axes = selection.get("decision_axes")
        has_distinct_axis = False
        if not isinstance(axes, list) or not axes:
            findings.append(
                Finding(
                    "ERROR",
                    "missing-artifact-decision-axes",
                    f"{question_id}: artifact_selection.decision_axes must identify exact option differences",
                )
            )
            selection_valid = False
        else:
            for index, axis in enumerate(axes, start=1):
                axis_label = f"{question_id}/artifact_selection.decision_axes[{index}]"
                if not isinstance(axis, dict):
                    findings.append(Finding("ERROR", "invalid-artifact-decision-axis", f"{axis_label} must be an object"))
                    selection_valid = False
                    continue
                name = axis.get("name")
                option_values = axis.get("option_values")
                if not isinstance(name, str) or not name.strip():
                    findings.append(Finding("ERROR", "invalid-artifact-decision-axis", f"{axis_label}.name must be non-empty text"))
                    selection_valid = False
                if not isinstance(option_values, dict) or {str(key) for key in option_values} != option_keys:
                    findings.append(
                        Finding(
                            "ERROR",
                            "artifact-decision-axis-coverage",
                            f"{axis_label}.option_values must contain every option key exactly once",
                        )
                    )
                    selection_valid = False
                    continue
                normalized_values: set[str] = set()
                for raw_key, raw_value in option_values.items():
                    key = str(raw_key)
                    if not isinstance(raw_value, str) or not raw_value.strip():
                        findings.append(Finding("ERROR", "invalid-artifact-decision-axis", f"{axis_label}.option_values[{key!r}] must be non-empty text"))
                        selection_valid = False
                        continue
                    candidate_artifacts = [
                        candidates[key]
                        for candidates in valid_evidence_by_type.values()
                        if key in candidates
                    ]
                    if not any(raw_value in artifact for artifact in candidate_artifacts):
                        findings.append(
                            Finding(
                                "ERROR",
                                "artifact-decision-axis-not-visible",
                                f"{axis_label}.option_values[{key!r}] is not an exact substring of option {key}'s validated artifact candidate",
                            )
                        )
                        selection_valid = False
                        continue
                    normalized_values.add(normalize_exact_text(raw_value))
                has_distinct_axis = has_distinct_axis or len(normalized_values) >= 2
        if isinstance(axes, list) and axes and not has_distinct_axis:
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-decision-axes-not-distinct",
                    f"{question_id}: decision axes do not expose a substantive candidate difference",
                )
            )
            selection_valid = False

        validation = selection.get("validation")
        if not isinstance(validation, dict):
            findings.append(
                Finding(
                    "ERROR",
                    "missing-artifact-candidate-validation",
                    f"{question_id}: artifact_selection.validation must record a shared candidate check",
                )
            )
            selection_valid = False
        else:
            method = validation.get("method")
            if method not in ARTIFACT_VALIDATION_METHODS:
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-artifact-validation-method",
                        f"{question_id}: validation.method must be one of {sorted(ARTIFACT_VALIDATION_METHODS)}",
                    )
                )
                selection_valid = False
            if "code" in declared_valid_types and method != "shared_fixture":
                findings.append(
                    Finding(
                        "ERROR",
                        "code-artifact-requires-shared-fixture",
                        f"{question_id}: code candidates must be checked by the same executable or stubbed fixture",
                    )
                )
                selection_valid = False
            reference = validation.get("reference")
            if not isinstance(reference, str) or not reference.strip():
                findings.append(
                    Finding(
                        "ERROR",
                        "missing-artifact-validation-reference",
                        f"{question_id}: validation.reference must identify the executed fixture, schema, dry run, or derivation check",
                    )
                )
                selection_valid = False

            correct = question.get("correct")
            if isinstance(correct, str):
                expected_correct = {correct}
            elif isinstance(correct, list):
                expected_correct = {str(key) for key in correct}
            else:
                expected_correct = set()
            validated_correct = validation.get("validated_correct")
            actual_validated = (
                {str(key) for key in validated_correct}
                if isinstance(validated_correct, list)
                else set()
            )
            if actual_validated != expected_correct:
                findings.append(
                    Finding(
                        "ERROR",
                        "artifact-validated-correct-mismatch",
                        f"{question_id}: validation.validated_correct {sorted(actual_validated)} does not match keyed correct {sorted(expected_correct)}",
                    )
                )
                selection_valid = False

            candidate_results = validation.get("candidate_results")
            if not isinstance(candidate_results, dict) or {str(key) for key in candidate_results} != option_keys:
                findings.append(
                    Finding(
                        "ERROR",
                        "artifact-candidate-result-coverage",
                        f"{question_id}: validation.candidate_results must contain every option key exactly once",
                    )
                )
                selection_valid = False
            else:
                normalized_results: set[str] = set()
                for raw_key, result in candidate_results.items():
                    if not isinstance(result, str) or not result.strip():
                        findings.append(
                            Finding(
                                "ERROR",
                                "invalid-artifact-candidate-result",
                                f"{question_id}: candidate result for {str(raw_key)!r} must be non-empty text",
                            )
                        )
                        selection_valid = False
                    else:
                        normalized_results.add(normalize_exact_text(result))
                if len(normalized_results) < 2:
                    findings.append(
                        Finding(
                            "ERROR",
                            "artifact-candidate-results-not-distinct",
                            f"{question_id}: candidate validation reports no meaningful behavioral or result difference",
                        )
                    )
                    selection_valid = False

        explanation_bindings = selection.get("explanation_bindings")
        if not isinstance(explanation_bindings, dict) or {
            str(key) for key in explanation_bindings
        } != option_keys:
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-explanation-binding-coverage",
                    f"{question_id}: artifact_selection.explanation_bindings must contain every option key exactly once",
                )
            )
            selection_valid = False
        else:
            axis_values_by_option: dict[str, list[str]] = defaultdict(list)
            raw_axes = selection.get("decision_axes")
            if isinstance(raw_axes, list):
                for axis in raw_axes:
                    option_values = axis.get("option_values") if isinstance(axis, dict) else None
                    if isinstance(option_values, dict):
                        for raw_key, raw_value in option_values.items():
                            if isinstance(raw_value, str) and raw_value.strip():
                                axis_values_by_option[str(raw_key)].append(raw_value)
            raw_validation = selection.get("validation")
            raw_results = raw_validation.get("candidate_results") if isinstance(raw_validation, dict) else None
            artifact_excerpts: set[str] = set()
            result_excerpts: set[str] = set()
            for raw_key, raw_binding in explanation_bindings.items():
                key = str(raw_key)
                label = f"{question_id}/artifact_selection.explanation_bindings[{key!r}]"
                if not isinstance(raw_binding, dict):
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-artifact-explanation-binding",
                            f"{label} must be an object",
                        )
                    )
                    selection_valid = False
                    continue
                artifact_excerpt = raw_binding.get("artifact_excerpt")
                result_excerpt = raw_binding.get("result_excerpt")
                explanation_excerpt = raw_binding.get("explanation_excerpt")
                fields = {
                    "artifact_excerpt": artifact_excerpt,
                    "result_excerpt": result_excerpt,
                    "explanation_excerpt": explanation_excerpt,
                }
                if any(
                    not isinstance(value, str)
                    or len(normalize_exact_text(value)) < MIN_ARTIFACT_BINDING_LENGTH
                    for value in fields.values()
                ):
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-artifact-explanation-binding",
                            f"{label} must contain substantive artifact_excerpt, result_excerpt, and explanation_excerpt text",
                        )
                    )
                    selection_valid = False
                    continue

                candidate_artifacts = [
                    candidates[key]
                    for candidates in valid_evidence_by_type.values()
                    if key in candidates
                ]
                if not any(str(artifact_excerpt) in artifact for artifact in candidate_artifacts):
                    findings.append(
                        Finding(
                            "ERROR",
                            "artifact-explanation-binding-artifact-not-visible",
                            f"{label}.artifact_excerpt is not an exact substring of option {key}'s validated artifact",
                        )
                    )
                    selection_valid = False
                if str(artifact_excerpt) not in axis_values_by_option.get(key, []):
                    findings.append(
                        Finding(
                            "ERROR",
                            "artifact-explanation-binding-not-decisive",
                            f"{label}.artifact_excerpt must equal one declared decision-axis value for option {key}",
                        )
                    )
                    selection_valid = False

                candidate_result = raw_results.get(key) if isinstance(raw_results, dict) else None
                if not isinstance(candidate_result, str) or str(result_excerpt) not in candidate_result:
                    findings.append(
                        Finding(
                            "ERROR",
                            "artifact-explanation-binding-result-not-validated",
                            f"{label}.result_excerpt is not an exact substring of option {key}'s validated candidate result",
                        )
                    )
                    selection_valid = False

                explanation = _artifact_explanation_text(question, key)
                if not isinstance(explanation, str) or str(explanation_excerpt) not in explanation:
                    findings.append(
                        Finding(
                            "ERROR",
                            "artifact-explanation-binding-not-visible",
                            f"{label}.explanation_excerpt is not an exact substring of the keyed learner-visible explanation",
                        )
                    )
                    selection_valid = False
                elif (
                    str(artifact_excerpt) not in str(explanation_excerpt)
                    or str(result_excerpt) not in str(explanation_excerpt)
                ):
                    findings.append(
                        Finding(
                            "ERROR",
                            "artifact-explanation-binding-incomplete",
                            f"{label}.explanation_excerpt must include both the decisive artifact slice and validated result slice",
                        )
                    )
                    selection_valid = False

                artifact_excerpts.add(normalize_exact_text(str(artifact_excerpt)))
                result_excerpts.add(normalize_exact_text(str(result_excerpt)))

            if len(artifact_excerpts) != len(option_keys):
                findings.append(
                    Finding(
                        "ERROR",
                        "artifact-explanation-artifacts-not-distinct",
                        f"{question_id}: each option explanation must cite a distinct decisive artifact slice",
                    )
                )
                selection_valid = False
            if len(result_excerpts) != len(option_keys):
                findings.append(
                    Finding(
                        "ERROR",
                        "artifact-explanation-results-not-distinct",
                        f"{question_id}: each option explanation must cite a distinct validated candidate result",
                    )
                )
                selection_valid = False

    if question_type not in {"single_choice", "multiple_response"} or not selection_valid:
        return set()
    return complete_types


def _validate_artifact_surface_policy(
    policy: dict[str, Any],
    questions: list[dict[str, Any]],
    validated_types: list[set[str]],
    target_ratio: float | None,
    findings: list[Finding],
) -> None:
    raw_surfaces = policy.get("assessment_surfaces")
    if not isinstance(raw_surfaces, dict) or not raw_surfaces:
        findings.append(
            Finding(
                "ERROR",
                "missing-artifact-assessment-surfaces",
                "artifact_policy.assessment_surfaces must declare every independently presented practice bank and exam form",
            )
        )
        return

    grouped_indexes: dict[str, list[int]] = defaultdict(list)
    for index, question in enumerate(questions):
        question_id = str(question.get("id", "?"))
        surface = question.get("assessment_surface")
        if not isinstance(surface, str) or not surface.strip():
            findings.append(
                Finding(
                    "ERROR",
                    "missing-question-assessment-surface",
                    f"{question_id}: assessment_surface must identify the independently presented practice bank or exam form",
                )
            )
            continue
        normalized_surface = surface.strip()
        if normalized_surface not in raw_surfaces:
            findings.append(
                Finding(
                    "ERROR",
                    "undeclared-question-assessment-surface",
                    f"{question_id}: assessment_surface {normalized_surface!r} is absent from artifact_policy.assessment_surfaces",
                )
            )
            continue
        grouped_indexes[normalized_surface].append(index)

    for raw_surface, raw_config in raw_surfaces.items():
        surface = str(raw_surface).strip()
        label = f"artifact_policy.assessment_surfaces[{surface!r}]"
        if not surface:
            findings.append(Finding("ERROR", "invalid-artifact-assessment-surface", f"{label}: surface id must be non-empty"))
            continue
        if not isinstance(raw_config, dict):
            findings.append(Finding("ERROR", "invalid-artifact-assessment-surface", f"{label} must be an object"))
            continue
        total = raw_config.get("total")
        minimum = raw_config.get("minimum_questions_with_artifacts")
        if isinstance(total, bool) or not isinstance(total, int) or total <= 0:
            findings.append(Finding("ERROR", "invalid-artifact-surface-total", f"{label}.total must be a positive integer"))
            continue
        indexes = grouped_indexes.get(surface, [])
        if len(indexes) != total:
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-surface-total-mismatch",
                    f"{surface}: declared total {total}, found {len(indexes)} questions",
                )
            )
        floor = math.ceil(total * target_ratio) if target_ratio is not None else 0
        if isinstance(minimum, bool) or not isinstance(minimum, int) or not 0 <= minimum <= total:
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-artifact-surface-minimum",
                    f"{label}.minimum_questions_with_artifacts must be between 0 and {total}",
                )
            )
            effective_minimum = floor
        else:
            effective_minimum = max(floor, minimum)
            if target_ratio is not None and minimum < floor:
                findings.append(
                    Finding(
                        "ERROR",
                        "artifact-surface-minimum-below-floor",
                        f"{surface}: minimum must be at least {floor} ({target_ratio:.0%} of {total}), found {minimum}",
                    )
                )
        artifact_count = sum(1 for index in indexes if validated_types[index])
        if artifact_count < effective_minimum:
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-surface-count-below-minimum",
                    f"{surface}: minimum {effective_minimum} option-artifact questions, found {artifact_count}",
                )
            )

        raw_type_minimums = raw_config.get("minimum_by_type", {})
        if not isinstance(raw_type_minimums, dict):
            findings.append(Finding("ERROR", "invalid-artifact-surface-minimums", f"{label}.minimum_by_type must be an object"))
            continue
        actual_by_type: Counter[str] = Counter()
        for index in indexes:
            actual_by_type.update(validated_types[index])
        for raw_type, raw_count in raw_type_minimums.items():
            artifact_type = str(raw_type)
            if artifact_type not in ARTIFACT_TYPES:
                findings.append(
                    Finding(
                        "ERROR",
                        "unsupported-artifact-type",
                        f"{label}.minimum_by_type contains unsupported type {artifact_type!r}",
                    )
                )
                continue
            if isinstance(raw_count, bool) or not isinstance(raw_count, int) or not 0 <= raw_count <= total:
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-artifact-surface-minimums",
                        f"{label}.minimum_by_type[{artifact_type!r}] must be between 0 and {total}",
                    )
                )
                continue
            if actual_by_type.get(artifact_type, 0) < raw_count:
                findings.append(
                    Finding(
                        "ERROR",
                        "artifact-surface-type-count-below-minimum",
                        f"{surface}/{artifact_type}: minimum {raw_count}, found {actual_by_type.get(artifact_type, 0)}",
                    )
                )


def validate_question_source_profile(
    targets: dict[str, Any] | None,
    required: bool,
    findings: list[Finding],
) -> None:
    if targets is None:
        if required:
            findings.append(
                Finding(
                    "ERROR",
                    "question-source-profile-targets-not-provided",
                    "--require-question-source-profile requires --targets",
                )
            )
        return

    profile = targets.get("question_source_profile")
    if profile is None:
        if required:
            findings.append(
                Finding(
                    "ERROR",
                    "missing-question-source-profile",
                    "targets.question_source_profile is required",
                )
            )
        return
    if not isinstance(profile, dict):
        findings.append(
            Finding(
                "ERROR",
                "invalid-question-source-profile",
                "targets.question_source_profile must be an object",
            )
        )
        return

    if profile.get("analyzed_before_authoring") is not True:
        findings.append(
            Finding(
                "ERROR",
                "question-source-profile-not-pre-authoring",
                "question_source_profile.analyzed_before_authoring must be true",
            )
        )

    sample_size = profile.get("sample_size")
    if isinstance(sample_size, bool) or not isinstance(sample_size, int) or sample_size < 0:
        findings.append(
            Finding(
                "ERROR",
                "invalid-question-source-sample-size",
                "question_source_profile.sample_size must be a non-negative integer",
            )
        )
        return

    def validate_primary_distribution(raw_value: Any, field: str) -> dict[str, int]:
        label = f"question_source_profile.{field}"
        if not isinstance(raw_value, dict) or (sample_size > 0 and not raw_value):
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-question-source-distribution",
                    f"{label} must be a non-empty object when sample_size is positive",
                )
            )
            return {}
        validated: dict[str, int] = {}
        for raw_key, raw_count in raw_value.items():
            key = str(raw_key).strip()
            if not key or isinstance(raw_count, bool) or not isinstance(raw_count, int) or raw_count < 0:
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-question-source-distribution",
                        f"{label} must contain non-empty labels with non-negative integer counts",
                    )
                )
                continue
            validated[key] = raw_count
        if sum(validated.values()) != sample_size:
            findings.append(
                Finding(
                    "ERROR",
                    "question-source-distribution-total-mismatch",
                    f"{label} must total sample_size {sample_size}, found {sum(validated.values())}",
                )
            )
        return validated

    validate_primary_distribution(
        profile.get("observed_question_type_counts"),
        "observed_question_type_counts",
    )
    validate_primary_distribution(
        profile.get("observed_primary_decision_pattern_counts"),
        "observed_primary_decision_pattern_counts",
    )

    scope_analysis = profile.get("scope_analysis")
    if not isinstance(scope_analysis, dict):
        findings.append(
            Finding(
                "ERROR",
                "invalid-question-source-scope-analysis",
                "question_source_profile.scope_analysis must be an object",
            )
        )
    else:
        weight_status = scope_analysis.get("official_weight_status")
        raw_weights = scope_analysis.get("official_domain_weights")
        if weight_status not in {"published", "not_published"} or not isinstance(raw_weights, dict):
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-question-source-official-scope",
                    "scope_analysis must declare official_weight_status and official_domain_weights",
                )
            )
        elif weight_status == "published":
            valid_weights = [
                float(value)
                for key, value in raw_weights.items()
                if str(key).strip()
                and not isinstance(value, bool)
                and isinstance(value, (int, float))
                and 0 < float(value) <= 1
            ]
            if len(valid_weights) != len(raw_weights) or not valid_weights or not math.isclose(
                sum(valid_weights), 1.0, rel_tol=0.0, abs_tol=0.0005
            ):
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-question-source-official-weights",
                        "published official_domain_weights must contain positive values totaling 1",
                    )
                )
        elif raw_weights:
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-question-source-official-weights",
                    "official_domain_weights must be empty when official_weight_status is not_published",
                )
            )

        raw_objectives = scope_analysis.get("official_objectives")
        official_objectives: set[str] = set()
        if not isinstance(raw_objectives, list) or not raw_objectives:
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-question-source-official-scope",
                    "scope_analysis.official_objectives must be a non-empty list",
                )
            )
        else:
            objective_values = [str(value).strip() for value in raw_objectives]
            official_objectives = {value for value in objective_values if value}
            if len(official_objectives) != len(objective_values):
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-question-source-official-scope",
                        "scope_analysis.official_objectives must contain unique non-empty values",
                    )
                )

        objective_counts = validate_primary_distribution(
            scope_analysis.get("observed_primary_objective_counts"),
            "scope_analysis.observed_primary_objective_counts",
        )
        unexpected_objectives = sorted(set(objective_counts) - official_objectives - {"unmapped"})
        if unexpected_objectives:
            findings.append(
                Finding(
                    "ERROR",
                    "question-source-objective-outside-official-scope",
                    f"observed objectives are absent from official_objectives: {unexpected_objectives}",
                )
            )

        validate_primary_distribution(
            scope_analysis.get("observed_primary_content_family_counts"),
            "scope_analysis.observed_primary_content_family_counts",
        )

        for field in (
            "observed_service_feature_counts",
            "observed_integration_pattern_counts",
            "observed_lifecycle_stage_counts",
            "observed_constraint_counts",
        ):
            raw_inventory = scope_analysis.get(field)
            label = f"question_source_profile.scope_analysis.{field}"
            if not isinstance(raw_inventory, dict):
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-question-source-scope-inventory",
                        f"{label} must be an object",
                    )
                )
                continue
            if field == "observed_service_feature_counts" and sample_size > 0 and not raw_inventory:
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-question-source-scope-inventory",
                        f"{label} must be non-empty when sample_size is positive",
                    )
                )
            for raw_key, raw_count in raw_inventory.items():
                if (
                    not str(raw_key).strip()
                    or isinstance(raw_count, bool)
                    or not isinstance(raw_count, int)
                    or not 0 <= raw_count <= sample_size
                ):
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-question-source-scope-inventory",
                            f"{label} must contain non-empty labels with counts between 0 and sample_size",
                        )
                    )

        scope_gaps = scope_analysis.get("scope_gaps")
        if not isinstance(scope_gaps, list) or any(not isinstance(item, str) or not item.strip() for item in scope_gaps):
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-question-source-scope-gaps",
                    "scope_analysis.scope_gaps must be a list of non-empty strings",
                )
            )

        authoring_decisions = scope_analysis.get("authoring_scope_decisions")
        if (
            not isinstance(authoring_decisions, list)
            or not authoring_decisions
            or any(not isinstance(item, str) or not item.strip() for item in authoring_decisions)
        ):
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-question-source-authoring-decisions",
                    "scope_analysis.authoring_scope_decisions must be a non-empty list of decisions",
                )
            )

        raw_patterns = scope_analysis.get("scope_selection_patterns")
        pattern_ids: set[str] = set()
        if not isinstance(raw_patterns, list) or (sample_size > 0 and not raw_patterns):
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-question-source-selection-patterns",
                    "scope_analysis.scope_selection_patterns must be a non-empty list when source questions exist",
                )
            )
        else:
            for index, raw_pattern in enumerate(raw_patterns, start=1):
                label = f"question_source_profile.scope_analysis.scope_selection_patterns[{index}]"
                if not isinstance(raw_pattern, dict):
                    findings.append(
                        Finding("ERROR", "invalid-question-source-selection-patterns", f"{label} must be an object")
                    )
                    continue
                pattern_id = str(raw_pattern.get("id", "")).strip()
                description = raw_pattern.get("description")
                transformation = raw_pattern.get("question_transformation")
                observed_count = raw_pattern.get("observed_count")
                if not pattern_id or pattern_id in pattern_ids:
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-question-source-selection-patterns",
                            f"{label}.id must be unique and non-empty",
                        )
                    )
                else:
                    pattern_ids.add(pattern_id)
                if not isinstance(description, str) or not description.strip():
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-question-source-selection-patterns",
                            f"{label}.description must be non-empty",
                        )
                    )
                if not isinstance(transformation, str) or not transformation.strip():
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-question-source-selection-patterns",
                            f"{label}.question_transformation must explain how primary information becomes a question",
                        )
                    )
                if (
                    isinstance(observed_count, bool)
                    or not isinstance(observed_count, int)
                    or not 1 <= observed_count <= sample_size
                ):
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-question-source-selection-patterns",
                            f"{label}.observed_count must be between 1 and sample_size",
                        )
                    )

        raw_extrapolations = scope_analysis.get("official_scope_extrapolations")
        adopted_objectives: set[str] = set()
        if not isinstance(raw_extrapolations, list) or (pattern_ids and not raw_extrapolations):
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-question-source-scope-extrapolations",
                    "scope_analysis.official_scope_extrapolations must be non-empty when selection patterns exist",
                )
            )
        else:
            for index, raw_item in enumerate(raw_extrapolations, start=1):
                label = f"question_source_profile.scope_analysis.official_scope_extrapolations[{index}]"
                if not isinstance(raw_item, dict):
                    findings.append(
                        Finding("ERROR", "invalid-question-source-scope-extrapolations", f"{label} must be an object")
                    )
                    continue
                objective = str(raw_item.get("objective", "")).strip()
                status = raw_item.get("authoring_status")
                confidence = raw_item.get("confidence")
                reasoning = raw_item.get("reasoning")
                if objective not in official_objectives:
                    findings.append(
                        Finding(
                            "ERROR",
                            "question-source-extrapolation-outside-official-scope",
                            f"{label}.objective must be present in official_objectives",
                        )
                    )
                if status not in {"adopted", "rejected", "deferred"}:
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-question-source-scope-extrapolations",
                            f"{label}.authoring_status must be adopted, rejected, or deferred",
                        )
                    )
                elif status == "adopted" and objective:
                    adopted_objectives.add(objective)
                if confidence not in {"low", "medium", "high"}:
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-question-source-scope-extrapolations",
                            f"{label}.confidence must be low, medium, or high",
                        )
                    )
                if not isinstance(reasoning, str) or not reasoning.strip():
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-question-source-scope-extrapolations",
                            f"{label}.reasoning must be non-empty",
                        )
                    )
                for field in ("primary_source_topics", "inferred_question_patterns", "basis_pattern_ids"):
                    raw_values = raw_item.get(field)
                    if (
                        not isinstance(raw_values, list)
                        or not raw_values
                        or any(not isinstance(value, str) or not value.strip() for value in raw_values)
                    ):
                        findings.append(
                            Finding(
                                "ERROR",
                                "invalid-question-source-scope-extrapolations",
                                f"{label}.{field} must be a non-empty list of strings",
                            )
                        )
                    elif field == "basis_pattern_ids":
                        unknown_patterns = sorted(set(raw_values) - pattern_ids)
                        if unknown_patterns:
                            findings.append(
                                Finding(
                                    "ERROR",
                                    "question-source-extrapolation-unknown-pattern",
                                    f"{label}.basis_pattern_ids contains unknown ids: {unknown_patterns}",
                                )
                            )
                raw_urls = raw_item.get("primary_source_urls")
                if (
                    not isinstance(raw_urls, list)
                    or not raw_urls
                    or any(
                        not isinstance(url, str)
                        or urlparse(url).scheme != "https"
                        or not urlparse(url).hostname
                        for url in raw_urls
                    )
                ):
                    findings.append(
                        Finding(
                            "ERROR",
                            "invalid-question-source-extrapolation-sources",
                            f"{label}.primary_source_urls must contain at least one HTTPS primary-source URL",
                        )
                    )

        unobserved_objectives = {
            objective
            for objective in official_objectives
            if objective_counts.get(objective, 0) == 0
        }
        missing_adopted_extrapolations = sorted(unobserved_objectives - adopted_objectives)
        if pattern_ids and missing_adopted_extrapolations:
            findings.append(
                Finding(
                    "ERROR",
                    "question-source-unobserved-objective-not-extrapolated",
                    "every official objective absent from the source must have an adopted, primary-source-based "
                    f"extrapolation: {missing_adopted_extrapolations}",
                )
            )

    count_keys = (
        "stem_artifact_questions",
        "option_artifact_questions",
        "both_stem_and_option_artifact_questions",
        "neither_artifact_questions",
    )
    raw_counts = profile.get("artifact_location_counts")
    counts: dict[str, int] = {}
    if not isinstance(raw_counts, dict):
        findings.append(
            Finding(
                "ERROR",
                "invalid-question-source-artifact-counts",
                "question_source_profile.artifact_location_counts must be an object",
            )
        )
    else:
        for key in count_keys:
            value = raw_counts.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= sample_size:
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-question-source-artifact-counts",
                        f"question_source_profile.artifact_location_counts.{key} must be between 0 and sample_size",
                    )
                )
            else:
                counts[key] = value

    if len(counts) == len(count_keys):
        stem_count = counts["stem_artifact_questions"]
        option_count = counts["option_artifact_questions"]
        both_count = counts["both_stem_and_option_artifact_questions"]
        neither_count = counts["neither_artifact_questions"]
        expected_neither = sample_size - stem_count - option_count + both_count
        if both_count > stem_count or both_count > option_count or expected_neither != neither_count:
            findings.append(
                Finding(
                    "ERROR",
                    "question-source-artifact-overlap-mismatch",
                    "source artifact counts must satisfy both <= stem and option, and "
                    "neither = sample_size - stem - option + both",
                )
            )

    rate_to_count = {
        "stem_artifact_rate": "stem_artifact_questions",
        "option_artifact_rate": "option_artifact_questions",
        "both_stem_and_option_artifact_rate": "both_stem_and_option_artifact_questions",
        "neither_artifact_rate": "neither_artifact_questions",
    }
    raw_rates = profile.get("artifact_location_rates")
    if not isinstance(raw_rates, dict):
        findings.append(
            Finding(
                "ERROR",
                "invalid-question-source-artifact-rates",
                "question_source_profile.artifact_location_rates must be an object",
            )
        )
    else:
        for rate_key, count_key in rate_to_count.items():
            value = raw_rates.get(rate_key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-question-source-artifact-rates",
                        f"question_source_profile.artifact_location_rates.{rate_key} must be between 0 and 1",
                    )
                )
                continue
            if count_key in counts:
                expected_rate = counts[count_key] / sample_size if sample_size else 0.0
                if not math.isclose(float(value), expected_rate, rel_tol=0.0, abs_tol=0.000005):
                    findings.append(
                        Finding(
                            "ERROR",
                            "question-source-artifact-rate-mismatch",
                            f"{rate_key}: expected {expected_rate:.6f} from counts, found {float(value):.6f}",
                        )
                    )

    for field, count_key in (
        ("stem_artifact_by_type", "stem_artifact_questions"),
        ("option_artifact_by_type", "option_artifact_questions"),
    ):
        raw_by_type = profile.get(field)
        if not isinstance(raw_by_type, dict):
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-question-source-artifact-types",
                    f"question_source_profile.{field} must be an object",
                )
            )
            continue
        location_total = counts.get(count_key, sample_size)
        for raw_type, raw_count in raw_by_type.items():
            artifact_type = str(raw_type)
            if artifact_type not in ARTIFACT_TYPES:
                findings.append(
                    Finding(
                        "ERROR",
                        "unsupported-question-source-artifact-type",
                        f"question_source_profile.{field} contains unsupported type {artifact_type!r}",
                    )
                )
            if isinstance(raw_count, bool) or not isinstance(raw_count, int) or not 0 <= raw_count <= location_total:
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-question-source-artifact-types",
                        f"question_source_profile.{field}[{artifact_type!r}] must be between 0 and its location total",
                    )
                )

    classification_rule = profile.get("classification_rule")
    if (
        not isinstance(classification_rule, dict)
        or classification_rule.get("mention_only_is_artifact") is not False
        or classification_rule.get("requires_learner_visible_material_and_decision_dependency") is not True
    ):
        findings.append(
            Finding(
                "ERROR",
                "invalid-question-source-classification-rule",
                "question_source_profile.classification_rule must reject mention-only prose and require "
                "learner-visible material plus decision dependency",
            )
        )


def validate_artifact_policy(
    targets: dict[str, Any] | None,
    questions: list[dict[str, Any]],
    required: bool,
    official_source_hosts: Iterable[str],
    findings: list[Finding],
) -> None:
    if targets is None:
        if required:
            findings.append(Finding("ERROR", "artifact-policy-targets-not-provided", "--require-artifact-policy requires --targets"))
        return

    policy = targets.get("artifact_policy")
    if policy is None:
        if required:
            findings.append(Finding("ERROR", "missing-artifact-policy", "targets.artifact_policy is required"))
        return
    if not isinstance(policy, dict):
        findings.append(Finding("ERROR", "invalid-artifact-policy", "targets.artifact_policy must be an object"))
        return

    raw_target_ratio = policy.get("artifact_target_ratio")
    target_ratio: float | None = None
    if raw_target_ratio is not None:
        if (
            isinstance(raw_target_ratio, bool)
            or not isinstance(raw_target_ratio, (int, float))
            or not 0 <= float(raw_target_ratio) <= 1
        ):
            findings.append(
                Finding(
                    "ERROR",
                    "invalid-artifact-target-ratio",
                    "artifact_policy.artifact_target_ratio must be between 0 and 1 when declared",
                )
            )
        else:
            target_ratio = float(raw_target_ratio)

    allowed_hosts = {host.strip().casefold().rstrip(".") for host in official_source_hosts if host.strip()}
    if required and not allowed_hosts:
        findings.append(
            Finding(
                "ERROR",
                "artifact-policy-official-source-host-required",
                "--require-artifact-policy requires at least one --official-source-host for official evidence",
            )
        )

    evidence = policy.get("calibration_evidence")
    has_exam_guide = False
    has_official_question_evidence = False
    if not isinstance(evidence, list) or not evidence:
        findings.append(
            Finding(
                "ERROR",
                "invalid-artifact-evidence",
                "targets.artifact_policy.calibration_evidence must be a non-empty list",
            )
        )
    else:
        for index, item in enumerate(evidence, start=1):
            label = f"artifact_policy.calibration_evidence[{index}]"
            if not isinstance(item, dict):
                findings.append(Finding("ERROR", "invalid-artifact-evidence", f"{label} must be an object"))
                continue
            kind = item.get("kind")
            status = item.get("status")
            if kind not in ARTIFACT_EVIDENCE_KINDS:
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-artifact-evidence-kind",
                        f"{label}.kind must be one of {sorted(ARTIFACT_EVIDENCE_KINDS)}",
                    )
                )
            else:
                has_exam_guide = has_exam_guide or kind == "exam_guide"
                has_official_question_evidence = has_official_question_evidence or kind in {"official_sample", "official_practice"}
            if status not in ARTIFACT_EVIDENCE_STATUSES:
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-artifact-evidence-status",
                        f"{label}.status must be one of {sorted(ARTIFACT_EVIDENCE_STATUSES)}",
                    )
                )
            if kind == "user_observation" and status != "reported":
                findings.append(Finding("ERROR", "invalid-artifact-evidence-status", f"{label}: user_observation status must be 'reported'"))
            if kind != "user_observation" and status == "reported":
                findings.append(Finding("ERROR", "invalid-artifact-evidence-status", f"{label}: 'reported' is only valid for user_observation"))

            reviewed_at = item.get("reviewed_at")
            try:
                reviewed_date = date.fromisoformat(reviewed_at) if isinstance(reviewed_at, str) else None
            except ValueError:
                reviewed_date = None
            if reviewed_date is None:
                findings.append(Finding("ERROR", "invalid-artifact-evidence-date", f"{label}.reviewed_at must be YYYY-MM-DD"))
            elif reviewed_date > date.today():
                findings.append(Finding("ERROR", "invalid-artifact-evidence-date", f"{label}.reviewed_at must not be in the future"))

            url = item.get("url")
            url_required = kind != "user_observation" and status in {"current", "outdated"}
            if url_required and (not isinstance(url, str) or not url.strip()):
                findings.append(Finding("ERROR", "missing-artifact-evidence-url", f"{label}.url is required for status {status!r}"))
            if url is not None:
                parsed = urlparse(url) if isinstance(url, str) else None
                host = (parsed.hostname or "").casefold().rstrip(".") if parsed is not None else ""
                if parsed is None or parsed.scheme != "https" or not host:
                    findings.append(Finding("ERROR", "invalid-artifact-evidence-url", f"{label}.url must be an https URL"))
                elif kind != "user_observation" and allowed_hosts and not _host_allowed(host, allowed_hosts):
                    findings.append(
                        Finding(
                            "ERROR",
                            "unofficial-artifact-evidence-host",
                            f"{label}: {host} is not an allowed official host",
                        )
                    )
            if kind == "user_observation" and not isinstance(item.get("reference"), str):
                findings.append(Finding("ERROR", "missing-user-observation-reference", f"{label}.reference is required"))

        if not has_exam_guide:
            findings.append(Finding("ERROR", "missing-exam-guide-evidence", "artifact policy must record current official exam-guide research"))
        if not has_official_question_evidence:
            findings.append(
                Finding(
                    "ERROR",
                    "missing-official-question-evidence",
                    "artifact policy must record research into an official sample or practice exam, including unavailable or outdated status",
                )
            )

    calibration_note = policy.get("calibration_note")
    if not isinstance(calibration_note, str) or not calibration_note.strip():
        findings.append(Finding("ERROR", "missing-artifact-calibration-note", "targets.artifact_policy.calibration_note is required"))

    minimum_any = policy.get("minimum_questions_with_artifacts")
    global_floor = math.ceil(len(questions) * target_ratio) if target_ratio is not None else 0
    if isinstance(minimum_any, bool) or not isinstance(minimum_any, int) or not 0 <= minimum_any <= len(questions):
        findings.append(
            Finding(
                "ERROR",
                "invalid-artifact-minimum",
                "artifact_policy.minimum_questions_with_artifacts must be a non-negative integer no greater than total questions",
            )
        )
        minimum_any = None
    elif target_ratio is not None and minimum_any < global_floor:
        findings.append(
            Finding(
                "ERROR",
                "artifact-minimum-below-global-floor",
                f"artifact_policy.minimum_questions_with_artifacts must be at least {global_floor} "
                f"({target_ratio:.0%} of {len(questions)} questions), found {minimum_any}",
            )
        )

    minimum_by_type = policy.get("minimum_by_type")
    validated_minimums: dict[str, int] = {}
    if not isinstance(minimum_by_type, dict):
        findings.append(Finding("ERROR", "invalid-artifact-minimums", "artifact_policy.minimum_by_type must be an object"))
    elif not minimum_by_type and max(global_floor, minimum_any or 0) > 0:
        findings.append(
            Finding(
                "ERROR",
                "invalid-artifact-minimums",
                "artifact_policy.minimum_by_type must be non-empty when the option-artifact minimum is greater than zero",
            )
        )
    else:
        for raw_type, count in minimum_by_type.items():
            artifact_type = str(raw_type)
            if artifact_type not in ARTIFACT_TYPES:
                findings.append(
                    Finding(
                        "ERROR",
                        "unsupported-artifact-type",
                        f"artifact policy type {artifact_type!r} must be one of {sorted(ARTIFACT_TYPES)}",
                    )
                )
                continue
            if isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= len(questions):
                findings.append(
                    Finding(
                        "ERROR",
                        "invalid-artifact-minimums",
                        f"artifact_policy.minimum_by_type[{artifact_type!r}] must be between 0 and total questions",
                    )
                )
                continue
            validated_minimums[artifact_type] = count

    actual_by_type: Counter[str] = Counter()
    questions_with_artifacts = 0
    validated_types: list[set[str]] = []
    scenario_contracts: dict[str, list[str]] = defaultdict(list)
    for question in questions:
        valid_types = validate_question_artifact_evidence(question, findings)
        validated_types.append(valid_types)
        if valid_types:
            questions_with_artifacts += 1
            actual_by_type.update(valid_types)
            signature = _artifact_stem_contract_signature(question)
            if signature is not None:
                scenario_contracts[signature].append(str(question.get("id", "?")))

    for question_ids in scenario_contracts.values():
        if len(question_ids) > 1:
            ordered_ids = sorted(question_ids)
            preview = ordered_ids[:10]
            suffix = f" (+{len(ordered_ids) - len(preview)} more)" if len(ordered_ids) > len(preview) else ""
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-scenario-contract-reused",
                    "artifact-native questions reuse the same normalized "
                    f"constraints/observation/decision/results contract: {preview}{suffix}",
                )
            )

    effective_minimum = max(global_floor, minimum_any or 0)
    if questions_with_artifacts < effective_minimum:
        floor_note = f" ({target_ratio:.0%} global floor)" if target_ratio is not None else ""
        findings.append(
            Finding(
                "ERROR",
                "artifact-question-count-below-minimum",
                f"option-artifact selection questions: minimum {effective_minimum}"
                f"{floor_note}, found {questions_with_artifacts}",
            )
        )
    for artifact_type, expected_count in validated_minimums.items():
        actual_count = actual_by_type.get(artifact_type, 0)
        if actual_count < expected_count:
            findings.append(
                Finding(
                    "ERROR",
                    "artifact-type-count-below-minimum",
                    f"{artifact_type}: minimum {expected_count}, found {actual_count}",
                )
            )
    _validate_artifact_surface_policy(
        policy, questions, validated_types, target_ratio, findings
    )


def validate_sources(questions: list[dict[str, Any]], args: argparse.Namespace, findings: list[Finding]) -> None:
    allowed_hosts = {host.strip().casefold().rstrip(".") for host in args.official_source_host if host.strip()}
    today = date.today()
    for question in questions:
        question_id = str(question["id"])
        sources = question.get("sources")
        reviewed_at = question.get("source_reviewed_at")
        if args.require_sources and (not isinstance(sources, list) or not sources):
            findings.append(Finding("ERROR", "missing-sources", f"{question_id}: sources are required"))
        if sources is not None:
            if not isinstance(sources, list) or not sources or any(not isinstance(source, str) or not source.strip() for source in sources):
                findings.append(Finding("ERROR", "invalid-sources", f"{question_id}: sources must be a non-empty list of URLs"))
            else:
                for source in sources:
                    parsed = urlparse(source)
                    host = (parsed.hostname or "").casefold().rstrip(".")
                    if parsed.scheme != "https" or not host:
                        findings.append(Finding("ERROR", "invalid-source-url", f"{question_id}: source must be an https URL: {source}"))
                    elif allowed_hosts and not _host_allowed(host, allowed_hosts):
                        findings.append(Finding("ERROR", "unofficial-source-host", f"{question_id}: {host} is not an allowed official host"))
        if args.require_sources and not reviewed_at:
            findings.append(Finding("ERROR", "missing-source-review-date", f"{question_id}: source_reviewed_at is required"))
        if reviewed_at is not None:
            try:
                reviewed_date = date.fromisoformat(str(reviewed_at))
            except ValueError:
                findings.append(Finding("ERROR", "invalid-source-review-date", f"{question_id}: source_reviewed_at must be YYYY-MM-DD"))
                continue
            age_days = (today - reviewed_date).days
            if age_days < 0:
                findings.append(Finding("ERROR", "future-source-review-date", f"{question_id}: source_reviewed_at is in the future"))
            elif args.max_source_age_days is not None and age_days > args.max_source_age_days:
                findings.append(Finding("WARNING", "stale-source-review", f"{question_id}: source review is {age_days} days old"))


def write_hash_report(path: Path | None, questions: list[dict[str, Any]], hashes: dict[str, str]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("id", "question_hash"))
        for question_id in sorted(hashes, key=lambda value: (value.casefold(), value)):
            writer.writerow((question_id, hashes[question_id]))


def _load_baseline_hashes(path: Path, findings: list[Finding]) -> dict[str, str]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not {"id", "question_hash"}.issubset(reader.fieldnames):
                findings.append(Finding("ERROR", "invalid-baseline-hash-report", f"{path}: id and question_hash columns are required"))
                return {}
            hashes: dict[str, str] = {}
            for row in reader:
                question_id = csv_cell(row, "id")
                recorded_hash = csv_cell(row, "question_hash").casefold()
                if not question_id or not recorded_hash:
                    findings.append(Finding("ERROR", "invalid-baseline-hash-report", f"{path}: every row requires id and question_hash"))
                    continue
                if question_id in hashes:
                    findings.append(Finding("ERROR", "duplicate-baseline-hash", f"{question_id}: duplicate baseline row"))
                    continue
                hashes[question_id] = recorded_hash
            return hashes
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        findings.append(Finding("ERROR", "baseline-hash-report-unreadable", f"{path}: {error}"))
        return {}


def _load_baseline_change_log(path: Path | None, findings: list[Finding]) -> dict[str, tuple[str, str, str]]:
    if path is None:
        return {}
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not {"id", "action", "reason", "approval_ref"}.issubset(reader.fieldnames):
                findings.append(Finding("ERROR", "invalid-baseline-change-log", f"{path}: id, action, reason, and approval_ref columns are required"))
                return {}
            changes: dict[str, tuple[str, str, str]] = {}
            for row in reader:
                question_id = csv_cell(row, "id")
                action = csv_cell(row, "action").casefold()
                reason = csv_cell(row, "reason")
                approval_ref = csv_cell(row, "approval_ref")
                if not question_id or action not in {"changed", "removed"} or not reason:
                    findings.append(Finding("ERROR", "invalid-baseline-change-log", f"{path}: every row requires id, changed/removed action, and reason"))
                    continue
                if action == "removed" and not approval_ref:
                    findings.append(Finding("ERROR", "missing-removal-approval", f"{question_id}: removed baseline question requires approval_ref"))
                    continue
                if question_id in changes:
                    findings.append(Finding("ERROR", "duplicate-baseline-change", f"{question_id}: duplicate baseline change row"))
                    continue
                changes[question_id] = (action, reason, approval_ref)
            return changes
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        findings.append(Finding("ERROR", "baseline-change-log-unreadable", f"{path}: {error}"))
        return {}


def validate_baseline_protection(
    baseline_path: Path | None,
    change_log_path: Path | None,
    current_hashes: dict[str, str],
    expected_baseline_total: int | None,
    required: bool,
    findings: list[Finding],
) -> None:
    if baseline_path is None:
        if required:
            findings.append(Finding("ERROR", "baseline-hash-report-not-provided", "a pre-change --baseline-hash-report is required"))
        if change_log_path is not None:
            findings.append(Finding("ERROR", "baseline-hash-report-not-provided", "--baseline-change-log requires --baseline-hash-report"))
        return

    baseline_hashes = _load_baseline_hashes(baseline_path, findings)
    if expected_baseline_total is not None and len(baseline_hashes) != expected_baseline_total:
        findings.append(
            Finding(
                "ERROR",
                "baseline-total-mismatch",
                f"baseline hash report contains {len(baseline_hashes)} questions, expected baseline_total {expected_baseline_total}",
            )
        )
    changes = _load_baseline_change_log(change_log_path, findings)
    actual_changes: dict[str, str] = {}
    for question_id, baseline_hash in baseline_hashes.items():
        current_hash = current_hashes.get(question_id)
        if current_hash is None:
            actual_changes[question_id] = "removed"
        elif current_hash.casefold() != baseline_hash:
            actual_changes[question_id] = "changed"

    for question_id, action in actual_changes.items():
        recorded = changes.get(question_id)
        if recorded is None or recorded[0] != action:
            findings.append(
                Finding(
                    "ERROR",
                    "unaccounted-baseline-change",
                    f"{question_id}: baseline question was {action} without a matching change-log row",
                )
            )
    for question_id, (action, _, _) in changes.items():
        if actual_changes.get(question_id) != action:
            findings.append(
                Finding(
                    "ERROR",
                    "stale-baseline-change-log",
                    f"{question_id}: logged action {action!r} does not match the current baseline comparison",
                )
            )


def validate_review_ledger(
    path: Path | None,
    label: str,
    question_ids: set[str],
    hashes: dict[str, str],
    require_hashes: bool,
    required: bool,
    findings: list[Finding],
) -> dict[str, str]:
    if path is None:
        severity = "ERROR" if required else "WARNING"
        findings.append(Finding(severity, f"{label}-review-ledger-not-provided", f"no {label} review ledger was provided"))
        return {}
    records: dict[str, dict[str, str]] = {}
    reviewers: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        findings.append(Finding("ERROR", f"invalid-{label}-review-encoding", f"{path}: expected UTF-8: {error}"))
        return reviewers
    except OSError as error:
        findings.append(Finding("ERROR", f"invalid-{label}-review-ledger", f"{path}: {error}"))
        return reviewers
    reader = csv.DictReader(io.StringIO(text, newline=""))
    required_columns = {"id", "status", "reviewer", "notes"}
    if require_hashes:
        required_columns.add("question_hash")
    if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
        columns = ",".join(sorted(required_columns))
        findings.append(Finding("ERROR", f"invalid-{label}-review-ledger", f"{label} review ledger columns must include {columns}"))
        return reviewers
    has_hash_column = "question_hash" in reader.fieldnames
    for row_number, row in enumerate(reader, start=2):
        question_id = csv_cell(row, "id")
        if not question_id:
            findings.append(Finding("ERROR", "empty-review-id", f"{label} review ledger line {row_number}: id is empty"))
            continue
        if question_id in records:
            findings.append(Finding("ERROR", "duplicate-review", f"{question_id}: duplicate {label} review ledger row"))
            continue
        records[question_id] = row
        status = csv_cell(row, "status").upper()
        reviewer = csv_cell(row, "reviewer")
        notes = csv_cell(row, "notes")
        reviewers[question_id] = reviewer
        if status not in COMPLETE_REVIEW_STATUSES:
            findings.append(Finding("ERROR", "incomplete-review", f"{question_id}: {label} status {status!r} is not complete"))
        if not reviewer:
            findings.append(Finding("ERROR", "missing-reviewer", f"{question_id}: {label} reviewer is empty"))
        if status == "FIXED" and not notes:
            findings.append(Finding("ERROR", "missing-fix-note", f"{question_id}: {label} FIXED requires notes"))
        if has_hash_column:
            recorded_hash = csv_cell(row, "question_hash").casefold()
            if require_hashes and not recorded_hash:
                findings.append(Finding("ERROR", "missing-review-hash", f"{question_id}: {label} question_hash is empty"))
            elif recorded_hash and hashes.get(question_id) != recorded_hash:
                findings.append(Finding("ERROR", "review-hash-mismatch", f"{question_id}: {label} review hash does not match current question"))

    for question_id in sorted(question_ids - set(records)):
        findings.append(Finding("ERROR", "missing-review", f"{question_id}: no {label} review record"))
    for question_id in sorted(set(records) - question_ids):
        findings.append(Finding("ERROR", "stale-review", f"{question_id}: {label} review record has no question"))
    return reviewers


def validate_reviewer_independence(
    semantic_reviewers: dict[str, str], independent_reviewers: dict[str, str], findings: list[Finding]
) -> None:
    for question_id in sorted(set(semantic_reviewers) & set(independent_reviewers)):
        semantic = reviewer_identity(semantic_reviewers[question_id])
        independent = reviewer_identity(independent_reviewers[question_id])
        if semantic and semantic == independent:
            findings.append(Finding("ERROR", "non-independent-reviewer", f"{question_id}: semantic and independent reviewers are identical"))


def validate_answer_distribution(
    questions: Iterable[dict[str, Any]], args: argparse.Namespace, findings: list[Finding]
) -> None:
    cohorts: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for question in questions:
        if resolved_question_type(question) != "single_choice":
            continue
        options = question.get("options")
        correct = question.get("correct")
        if isinstance(options, dict) and isinstance(correct, str):
            cohort = tuple(sorted(str(key) for key in options))
            cohorts[cohort][correct] += 1
    for cohort, distribution in sorted(cohorts.items()):
        total = sum(distribution.values())
        if total < args.answer_position_min_cohort or len(cohort) <= 1:
            continue
        complete_distribution = {position: distribution.get(position, 0) for position in cohort}
        counts = list(complete_distribution.values())
        tolerance = max(1, math.ceil(total * 0.05))
        if max(counts) - min(counts) > tolerance:
            findings.append(Finding("WARNING", "answer-position-skew", f"single-choice cohort {cohort} is skewed: {complete_distribution}"))


def validate_answer_cues(questions: list[dict[str, Any]], args: argparse.Namespace, findings: list[Finding]) -> None:
    if not args.check_answer_cues:
        return
    eligible = 0
    correct_much_longer = 0
    correct_much_shorter = 0
    cue_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    cue_terms = tuple(dict.fromkeys(term.casefold() for term in (*DEFAULT_CUE_TERMS, *args.cue_term) if term))

    for question in questions:
        question_type = resolved_question_type(question)
        if question_type not in {"single_choice", "multiple_response", "true_false"}:
            continue
        options = question.get("options")
        correct = question.get("correct")
        if not isinstance(options, dict):
            continue
        if isinstance(correct, str):
            correct_keys = {correct}
        elif question_type == "multiple_response" and isinstance(correct, list):
            correct_keys = {str(key) for key in correct}
        else:
            continue
        option_keys = {str(key) for key in options}
        if not correct_keys or not correct_keys.issubset(option_keys) or correct_keys == option_keys:
            continue
        lengths = {str(key): visible_length(str(value)) for key, value in options.items()}
        wrong_lengths = [length for key, length in lengths.items() if key not in correct_keys and length > 0]
        if wrong_lengths:
            wrong_median = float(median(wrong_lengths))
            for correct_key in correct_keys:
                correct_length = lengths.get(correct_key, 0)
                if correct_length <= 0:
                    continue
                eligible += 1
                difference = abs(correct_length - wrong_median)
                if wrong_median > 0 and difference >= args.length_cue_min_difference and correct_length >= wrong_median * args.length_cue_ratio:
                    correct_much_longer += 1
                if difference >= args.length_cue_min_difference and wrong_median >= correct_length * args.length_cue_ratio:
                    correct_much_shorter += 1
        for key, value in options.items():
            option_text = unicodedata.normalize("NFKC", str(value)).casefold()
            for term in cue_terms:
                if term in option_text:
                    cue_counts[term][0] += 1
                    if str(key) in correct_keys:
                        cue_counts[term][1] += 1

    minimum_questions = max(10, args.cue_min_occurrences)
    if eligible >= minimum_questions:
        longer_share = correct_much_longer / eligible
        shorter_share = correct_much_shorter / eligible
        if longer_share > args.length_cue_share:
            findings.append(Finding("WARNING", "correct-option-length-cue", f"correct option is at least {args.length_cue_ratio:.2f}x longer in {correct_much_longer}/{eligible} eligible answer comparisons"))
        if shorter_share > args.length_cue_share:
            findings.append(Finding("WARNING", "correct-option-length-cue", f"correct option is at least {args.length_cue_ratio:.2f}x shorter in {correct_much_shorter}/{eligible} eligible answer comparisons"))
    for term, (total, correct_total) in sorted(cue_counts.items()):
        if total < args.cue_min_occurrences:
            continue
        correct_share = correct_total / total
        if correct_share >= args.cue_dominance or correct_share <= 1.0 - args.cue_dominance:
            findings.append(Finding("WARNING", "lexical-answer-cue", f"cue term {term!r} appears in correct options {correct_total}/{total} times"))


def validate_arguments(args: argparse.Namespace) -> None:
    for name, value in (("stem", args.stem_similarity), ("explanation", args.explanation_similarity)):
        if not 0.0 < value <= 1.0:
            raise SystemExit(f"--{name}-similarity must be in (0, 1]")
    if args.length_cue_ratio <= 1.0:
        raise SystemExit("--length-cue-ratio must be greater than 1")
    if args.length_cue_min_difference < 0:
        raise SystemExit("--length-cue-min-difference must be non-negative")
    if not 0.0 < args.length_cue_share <= 1.0:
        raise SystemExit("--length-cue-share must be in (0, 1]")
    if not 0.5 < args.cue_dominance <= 1.0:
        raise SystemExit("--cue-dominance must be in (0.5, 1]")
    if args.cue_min_occurrences < 1:
        raise SystemExit("--cue-min-occurrences must be positive")
    if args.answer_position_min_cohort < 2:
        raise SystemExit("--answer-position-min-cohort must be at least 2")
    if args.max_source_age_days is not None and args.max_source_age_days < 0:
        raise SystemExit("--max-source-age-days must be non-negative")
    compiled_patterns = [UNRESOLVED_PLACEHOLDER_PATTERN]
    for raw_pattern in args.placeholder_pattern:
        try:
            compiled_patterns.append(re.compile(raw_pattern, re.IGNORECASE))
        except re.error as error:
            raise SystemExit(f"invalid --placeholder-pattern {raw_pattern!r}: {error}") from error
    args.compiled_placeholder_patterns = tuple(compiled_patterns)
    args.normalized_forbidden_explanations = tuple(
        sorted(
            {normalize_exact_text(item) for item in (*DEFAULT_FORBIDDEN_EXPLANATIONS, *args.forbidden_explanation) if item.strip()},
            key=len,
            reverse=True,
        )
    )
    if args.require_independent_review and args.independent_review_ledger is None:
        return
    if args.review_ledger and args.independent_review_ledger:
        try:
            if args.review_ledger.resolve() == args.independent_review_ledger.resolve():
                raise SystemExit("semantic and independent review ledgers must be different files")
        except OSError:
            pass


def main() -> int:
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except (AttributeError, ValueError):
        pass
    args = parse_args()
    validate_arguments(args)
    findings: list[Finding] = []

    questions = load_jsonl(args.questions, findings)
    allowed = load_allowlist(args.allowlist, findings)
    valid, stems, explanations = validate_structure(questions, args, findings)
    find_similar_pairs(stems, "stem", args.stem_similarity, allowed, findings)
    find_similar_pairs(explanations, "explanation", args.explanation_similarity, allowed, findings)
    targets = validate_targets(
        args.targets,
        valid,
        args.require_metadata_targets,
        args.require_course_count_policy,
        args.official_source_host,
        findings,
    )
    validate_question_source_profile(
        targets,
        args.require_question_source_profile,
        findings,
    )
    validate_artifact_policy(
        targets,
        valid,
        args.require_artifact_policy,
        args.official_source_host,
        findings,
    )
    validate_sources(valid, args, findings)

    hashes = {str(question["id"]): question_hash(question) for question in valid}
    write_hash_report(args.hash_report, valid, hashes)
    baseline_total_value = targets.get("baseline_total") if targets is not None else None
    expected_baseline_total = baseline_total_value if _is_non_negative_int(baseline_total_value) else None
    baseline_required = args.require_baseline_protection or (
        args.require_course_count_policy
        and expected_baseline_total is not None
        and expected_baseline_total > 0
    )
    validate_baseline_protection(
        args.baseline_hash_report,
        args.baseline_change_log,
        hashes,
        expected_baseline_total,
        baseline_required,
        findings,
    )
    question_ids = set(hashes)
    semantic_reviewers = validate_review_ledger(
        args.review_ledger,
        "semantic",
        question_ids,
        hashes,
        args.require_review_hashes,
        args.require_review_hashes,
        findings,
    )
    independent_reviewers: dict[str, str] = {}
    if args.independent_review_ledger is not None or args.require_independent_review:
        independent_reviewers = validate_review_ledger(
            args.independent_review_ledger,
            "independent",
            question_ids,
            hashes,
            args.require_review_hashes,
            args.require_independent_review,
            findings,
        )
    validate_reviewer_independence(semantic_reviewers, independent_reviewers, findings)
    validate_answer_distribution(valid, args, findings)
    validate_answer_cues(valid, args, findings)

    error_count = sum(finding.severity == "ERROR" for finding in findings)
    warning_count = sum(finding.severity == "WARNING" for finding in findings)
    print(f"Questions: {len(valid)}")
    print(f"Errors: {error_count}")
    print(f"Warnings: {warning_count}")
    for finding in findings[: args.max_findings]:
        print(f"{finding.severity} [{finding.code}] {finding.message}")
    if len(findings) > args.max_findings:
        print(f"... {len(findings) - args.max_findings} additional findings omitted")

    failed = error_count > 0 or (args.fail_on_warnings and warning_count > 0)
    print("RESULT: FAIL" if failed else "RESULT: PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
