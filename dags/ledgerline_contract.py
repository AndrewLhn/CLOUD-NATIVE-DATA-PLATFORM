import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


class ContractValidationError(ValueError):
    """Raised when an event does not conform to the supported Ledgerline contract."""


CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contracts" / "kafka_event.schema.json"


def _build_validator() -> Draft202012Validator:
    schema = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=FormatChecker())


EVENT_VALIDATOR = _build_validator()


def validate_event(payload: Any) -> dict[str, Any]:
    """Validate and return one version-1 Ledgerline event."""

    errors = sorted(EVENT_VALIDATOR.iter_errors(payload), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        field = ".".join(str(part) for part in error.path) or "event"
        raise ContractValidationError(f"{field}: {error.message}")

    return payload
