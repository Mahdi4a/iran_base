from __future__ import annotations

import datetime

from iran_base.utils.numbers import to_latin_digits, to_persian_digits

MONTHS = (
	"فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
	"مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
)  # fmt: skip
_G_DAYS_BEFORE_MONTH = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
	if gy > 1600:
		jy, gy = 979, gy - 1600
	else:
		jy, gy = 0, gy - 621
	gy2 = gy + 1 if gm > 2 else gy
	days = (
		365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 - 80
		+ gd + _G_DAYS_BEFORE_MONTH[gm - 1]
	)  # fmt: skip
	jy += 33 * (days // 12053)
	days %= 12053
	jy += 4 * (days // 1461)
	days %= 1461
	if days > 365:
		jy += (days - 1) // 365
		days = (days - 1) % 365
	if days < 186:
		return jy, 1 + days // 31, 1 + days % 31
	return jy, 7 + (days - 186) // 30, 1 + (days - 186) % 30


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> tuple[int, int, int]:
	jy += 1595
	days = -355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33) + 3) // 4 + jd
	days += (jm - 1) * 31 if jm < 7 else (jm - 7) * 30 + 186
	gy = 400 * (days // 146097)
	days %= 146097
	if days > 36524:
		days -= 1
		gy += 100 * (days // 36524)
		days %= 36524
		if days >= 365:
			days += 1
	gy += 4 * (days // 1461)
	days %= 1461
	if days > 365:
		gy += (days - 1) // 365
		days = (days - 1) % 365
	gd = days + 1
	leap = (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0
	month_days = (0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
	gm = 1
	while gm < 13 and gd > month_days[gm]:
		gd -= month_days[gm]
		gm += 1
	return gy, gm, gd


def is_jalali_leap(jy: int) -> bool:
	return jalali_to_gregorian(jy + 1, 1, 1) == _add_days(jalali_to_gregorian(jy, 1, 1), 366)


def _add_days(date: tuple[int, int, int], days: int) -> tuple[int, int, int]:
	d = datetime.date(*date) + datetime.timedelta(days=days)
	return d.year, d.month, d.day


def to_jalali(date: datetime.date | datetime.datetime | str) -> tuple[int, int, int]:
	if isinstance(date, str):
		date = datetime.date.fromisoformat(to_latin_digits(date)[:10])
	return gregorian_to_jalali(date.year, date.month, date.day)


def format_jalali(date, persian_digits: bool = False, with_month_name: bool = False) -> str:
	jy, jm, jd = to_jalali(date)
	text = f"{jd} {MONTHS[jm - 1]} {jy}" if with_month_name else f"{jy:04d}-{jm:02d}-{jd:02d}"
	return to_persian_digits(text) if persian_digits else text


def parse_jalali(text: str) -> datetime.date:
	"""'1403/01/01' or '۱۴۰۳-۰۱-۰۱' to the Gregorian date stored in the database."""
	parts = to_latin_digits(text).replace("/", "-").split("-")
	if len(parts) != 3:
		raise ValueError(f"Not a Jalali date: {text!r}")
	jy, jm, jd = (int(p) for p in parts)
	if not (1 <= jm <= 12 and 1 <= jd <= 31) or (jm > 6 and jd > 30):
		raise ValueError(f"Not a Jalali date: {text!r}")
	if jm == 12 and jd == 30 and not is_jalali_leap(jy):
		raise ValueError(f"Not a Jalali date: {text!r}")
	return datetime.date(*jalali_to_gregorian(jy, jm, jd))
