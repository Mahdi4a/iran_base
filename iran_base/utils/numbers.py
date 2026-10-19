from __future__ import annotations

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_TO_LATIN = str.maketrans(PERSIAN_DIGITS + ARABIC_DIGITS, "0123456789" * 2)
_TO_PERSIAN = str.maketrans("0123456789", PERSIAN_DIGITS)

# 1 Toman = 10 Rial
RIAL_PER_TOMAN = 10


def to_latin_digits(value) -> str:
	"""Persian and Arabic-Indic digits to 0-9, so user input can be compared and stored."""
	return str(value if value is not None else "").translate(_TO_LATIN)


def to_persian_digits(value) -> str:
	return str(value if value is not None else "").translate(_TO_PERSIAN)


def group_digits(amount, separator: str = ",") -> str:
	"""1234567 -> 1,234,567. Amounts in Toman/Rial have no decimals."""
	return f"{int(round(float(amount))):,}".replace(",", separator)


def format_toman(amount, persian: bool = False) -> str:
	text = f"{group_digits(amount)} تومان"
	return to_persian_digits(text) if persian else text


def format_rial(amount, persian: bool = False) -> str:
	text = f"{group_digits(amount)} ریال"
	return to_persian_digits(text) if persian else text


def toman_to_rial(amount):
	return amount * RIAL_PER_TOMAN


def rial_to_toman(amount):
	return amount / RIAL_PER_TOMAN
