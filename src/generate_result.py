from dataclasses import dataclass


@dataclass
class GenerateResult:
    binary_data: bytes
    plain_text: str
    texty_json: dict
