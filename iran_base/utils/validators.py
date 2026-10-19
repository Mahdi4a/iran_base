from __future__ import annotations

import re

from iran_base.utils.numbers import to_latin_digits

_LEGAL_ID_COEFFICIENTS = (29, 27, 23, 19, 17, 29, 27, 23, 19, 17)
_POSTAL_CODE = re.compile(r"^(?!(\d)\1{3})[13-9]{4}[1346-9][013-9]\d{4}$")


def _digits(value) -> str:
	return to_latin_digits(value).strip()


def is_valid_national_id(value) -> bool:
	"""کد ملی: 10 digits with the control digit of the Iranian national id."""
	code = _digits(value)
	if not re.fullmatch(r"\d{10}", code) or len(set(code)) == 1:
		return False
	total = sum(int(code[i]) * (10 - i) for i in range(9))
	remainder = total % 11
	control = int(code[9])
	return control == remainder if remainder < 2 else control == 11 - remainder


def is_valid_legal_id(value) -> bool:
	"""شناسه ملی: 11 digits for companies and organizations."""
	code = _digits(value)
	if not re.fullmatch(r"\d{11}", code) or len(set(code)) == 1:
		return False
	tens = int(code[9]) + 2
	total = sum((tens + int(code[i])) * _LEGAL_ID_COEFFICIENTS[i] for i in range(10))
	remainder = total % 11
	return int(code[10]) == (0 if remainder == 10 else remainder)


def is_valid_postal_code(value) -> bool:
	return bool(_POSTAL_CODE.match(_digits(value)))


def is_valid_economic_code(value) -> bool:
	"""کد اقتصادی: 12 digits (legal) or 14 digits (real person). Format only; no public checksum."""
	return bool(re.fullmatch(r"\d{12}|\d{14}", _digits(value)))


def is_valid_mobile(value) -> bool:
	from iran_base.utils.sms import try_normalize_mobile

	return try_normalize_mobile(value) is not None
