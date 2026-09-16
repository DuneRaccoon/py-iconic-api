# -*- coding: utf-8 -*-
"""Base class for the generated response models.

The generated models describe what The Iconic's OpenAPI document *says* a response
looks like. Live responses differ from it in two ways that used to be fatal, and both
are handled here rather than field by field:

1. **Nulls where the document promises a value.** ``Order.targetToShip`` is declared
   ``required: true, nullable: true`` in the spec; the generator honoured ``required``
   and ignored ``nullable``, so the field came out as a plain ``str``. Every live order
   returns ``null`` for it, so *listing orders failed completely*. Thirty-seven fields
   across fifteen models had the same defect. The generated models are therefore
   rewritten so no field is required: a response model's job is to report what arrived,
   and one unexpected null must never cost the caller the whole page.

2. **Zero-date sentinels.** The platform is PHP/MySQL underneath and returns
   ``0000-00-00 00:00:00`` for "never", which reaches us shifted through a timezone as
   ``-0001-11-30T00:00:00.000000+10:04``. No date parser accepts a year of -1, and
   pydantic is right to refuse it. It means "no date", so it is read as ``None``.

Containers keep the guarantee they had before this change: a list or dict field that
used to be required can still never be ``None``, it just becomes empty instead. Only
scalar and object fields gained ``None`` as a possible value.
"""
from __future__ import annotations

import re
import typing
from datetime import date, datetime
from typing import Any, Dict, Set, Tuple

from pydantic import BaseModel, model_validator

# A year of 0000 or a negative year: MySQL's zero date, with or without a timezone
# shift applied. Nothing else legitimately starts this way.
ZERO_DATE_RE = re.compile(r"^\s*(?:-\d{1,6}|0000)-")


def _mentions(annotation: Any, types: Tuple[type, ...]) -> bool:
    """True if ``annotation`` is, or contains, one of ``types``.

    Walks Optional/Union/List/Dict parameters, so ``Optional[List[datetime]]`` counts.
    """
    if annotation in types:
        return True
    origin = typing.get_origin(annotation)
    if origin is not None and origin in types:
        return True
    return any(_mentions(arg, types) for arg in typing.get_args(annotation))


# Per-class keyset caches. Module-level on purpose: an annotated class attribute on a
# pydantic model is interpreted as a field (or a private attribute when underscored).
_TEMPORAL_KEYS: Dict[str, Set[str]] = {}
_LIST_KEYS: Dict[str, Set[str]] = {}
_DICT_KEYS: Dict[str, Set[str]] = {}

# Distinguishes "no replacement" from a replacement of None.
_UNSET = object()


class IconicResponseModel(BaseModel):
    """Tolerant base for every generated response model."""

    @classmethod
    def _iconic_keysets(cls) -> Tuple[Set[str], Set[str], Set[str]]:
        """(temporal, list, dict) field keys, by field name *and* alias."""
        cache_key = f"{cls.__module__}.{cls.__qualname__}"
        if cache_key not in _TEMPORAL_KEYS:
            temporal, lists, dicts = set(), set(), set()
            for name, field in cls.model_fields.items():
                keys = {name}
                if field.alias:
                    keys.add(field.alias)
                annotation = field.annotation
                if _mentions(annotation, (datetime, date)):
                    temporal |= keys
                # Only containers that CANNOT be None are normalised. A field already
                # declared Optional[List[...]] could always be None, and callers may
                # test for exactly that - turning it into [] would be a regression.
                if type(None) in typing.get_args(annotation):
                    continue
                if _mentions(annotation, (list, set, tuple, frozenset)):
                    lists |= keys
                elif _mentions(annotation, (dict,)):
                    dicts |= keys
            _TEMPORAL_KEYS[cache_key] = temporal
            _LIST_KEYS[cache_key] = lists
            _DICT_KEYS[cache_key] = dicts
        return _TEMPORAL_KEYS[cache_key], _LIST_KEYS[cache_key], _DICT_KEYS[cache_key]

    @model_validator(mode="before")
    @classmethod
    def _iconic_tolerate_api_quirks(cls, data: Any) -> Any:
        """Normalise the payload before pydantic validates it.

        Copies lazily: an untouched payload is passed through as-is, so the common
        case costs one dict scan and no allocation.
        """
        if not isinstance(data, dict):
            return data

        temporal, lists, dicts = cls._iconic_keysets()
        cleaned = None

        for key, value in data.items():
            replacement = _UNSET

            if key in temporal and isinstance(value, str):
                # "" and the zero-date sentinel both mean "no date".
                if not value.strip() or ZERO_DATE_RE.match(value):
                    replacement = None
            elif value is None:
                # Containers stay containers: they were never None before the models
                # were loosened, and callers loop over them without checking.
                if key in lists:
                    replacement = []
                elif key in dicts:
                    replacement = {}

            if replacement is not _UNSET:
                if cleaned is None:
                    cleaned = dict(data)
                cleaned[key] = replacement

        return cleaned if cleaned is not None else data
