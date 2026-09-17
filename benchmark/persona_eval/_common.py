"""Shared strict-value helpers for the persona evaluation harness."""
from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from collections.abc import Sequence
from typing import Any, NoReturn


_CANONICAL_SHA256 = re.compile(r"sha256:[0-9a-f]{64}\Z")


class PersonaEvalError(ValueError):
    """A named, fail-closed harness refusal."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def refuse(code: str, message: str) -> NoReturn:
    raise PersonaEvalError(code, message)


def exact_mapping(
    value: Any, field: str, keys: frozenset[str], code: str
) -> dict[str, Any]:
    if not isinstance(value, dict):
        refuse(code, f"{field} must be an object")
    if any(not isinstance(key, str) for key in value):
        refuse(code, f"{field} keys must be strings")
    actual = frozenset(value)
    if actual != keys:
        refuse(
            code,
            f"{field} keys differ (missing={sorted(keys - actual)}, "
            f"unknown={sorted(actual - keys)})",
        )
    return value


def nonblank(value: Any, field: str, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        refuse(code, f"{field} must be a nonblank string")
    if any(unicodedata.category(character).startswith("C") for character in value):
        refuse(code, f"{field} must contain machine-readable UTF-8 text")
    try:
        value.encode("utf-8")
    except UnicodeError:
        refuse(code, f"{field} must contain machine-readable UTF-8 text")
    return value


def canonical_sha256(value: Any, field: str, code: str) -> str:
    """Require the one canonical textual representation of a SHA-256 digest."""

    digest = nonblank(value, field, code)
    if _CANONICAL_SHA256.fullmatch(digest) is None:
        refuse(code, f"{field} must be canonical sha256:<64 lowercase hex>")
    return digest


def integer(
    value: Any, field: str, code: str, *, minimum: int | None = None
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        refuse(code, f"{field} must be an integer")
    if minimum is not None and value < minimum:
        refuse(code, f"{field} must be at least {minimum}")
    return value


def finite_number(
    value: Any,
    field: str,
    code: str,
    *,
    minimum: float | None = None,
    strictly_positive: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        refuse(code, f"{field} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        refuse(code, f"{field} must be a finite number")
    if strictly_positive and number <= 0:
        refuse(code, f"{field} must be positive")
    if minimum is not None and number < minimum:
        refuse(code, f"{field} must be at least {minimum}")
    return number


def string_list(
    value: Any,
    field: str,
    code: str,
    *,
    nonempty: bool = False,
) -> tuple[str, ...]:
    if (
        isinstance(value, (str, bytes, bytearray))
        or not isinstance(value, Sequence)
    ):
        refuse(code, f"{field} must be a list")
    result = tuple(
        nonblank(item, f"{field}[{index}]", code)
        for index, item in enumerate(value)
    )
    if nonempty and not result:
        refuse(code, f"{field} must not be empty")
    if len(set(result)) != len(result):
        refuse(code, f"{field} must not contain duplicates")
    return result


def canonical_json(value: Any, code: str) -> str:
    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError, OverflowError, UnicodeError) as exc:
        refuse(code, f"value is not strict JSON: {exc}")


def detached(value: Any, code: str) -> Any:
    return json.loads(canonical_json(value, code))


def sha256_json(value: Any, code: str = "INVALID_PROTOCOL") -> str:
    encoded = canonical_json(value, code).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def sha256_text(*parts: str) -> str:
    digest = hashlib.sha256()
    for part in parts:
        encoded = part.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return "sha256:" + digest.hexdigest()
