import datetime
import unittest

from iran_base.utils import jalali, numbers, sms, validators


class TestJalali(unittest.TestCase):
	def test_known_dates(self):
		self.assertEqual(jalali.gregorian_to_jalali(2024, 3, 20), (1403, 1, 1))
		self.assertEqual(jalali.gregorian_to_jalali(2000, 1, 1), (1378, 10, 11))
		self.assertEqual(jalali.jalali_to_gregorian(1403, 1, 1), (2024, 3, 20))

	def test_round_trip_over_many_years(self):
		day = datetime.date(1990, 1, 1)
		while day < datetime.date(2060, 1, 1):
			self.assertEqual(jalali.jalali_to_gregorian(*jalali.to_jalali(day)), (day.year, day.month, day.day))
			day += datetime.timedelta(days=7)

	def test_parse_and_format(self):
		self.assertEqual(jalali.parse_jalali("۱۴۰۳/۰۱/۰۱"), datetime.date(2024, 3, 20))
		self.assertEqual(jalali.format_jalali(datetime.date(2024, 3, 20)), "1403-01-01")
		self.assertEqual(jalali.format_jalali("2024-03-20", with_month_name=True), "1 فروردین 1403")

	def test_invalid_dates_are_refused(self):
		for text in ("1403/13/01", "1403/07/31", "1404/12/30", "abc"):
			with self.assertRaises(ValueError):
				jalali.parse_jalali(text)
		self.assertTrue(jalali.is_jalali_leap(1403))
		self.assertEqual(jalali.parse_jalali("1403/12/30"), datetime.date(2025, 3, 20))


class TestNumbers(unittest.TestCase):
	def test_digits(self):
		self.assertEqual(numbers.to_latin_digits("۰۹۱۲٣"), "09123")
		self.assertEqual(numbers.to_persian_digits("1405"), "۱۴۰۵")

	def test_money(self):
		self.assertEqual(numbers.format_toman(1234567), "1,234,567 تومان")
		self.assertEqual(numbers.format_toman(1500, persian=True), "۱,۵۰۰ تومان")
		self.assertEqual(numbers.toman_to_rial(5), 50)


class TestValidators(unittest.TestCase):
	def test_national_id(self):
		self.assertTrue(validators.is_valid_national_id("0499370899"))
		self.assertTrue(validators.is_valid_national_id("۰۴۹۹۳۷۰۸۹۹"))
		self.assertFalse(validators.is_valid_national_id("0499370898"))
		self.assertFalse(validators.is_valid_national_id("1111111111"))
		self.assertFalse(validators.is_valid_national_id("123"))

	def test_legal_id(self):
		self.assertTrue(validators.is_valid_legal_id("10380284790"))
		self.assertFalse(validators.is_valid_legal_id("10380284791"))

	def test_postal_code(self):
		self.assertTrue(validators.is_valid_postal_code("1593613311"))
		self.assertFalse(validators.is_valid_postal_code("0593613311"))
		self.assertFalse(validators.is_valid_postal_code("159361331"))

	def test_economic_code(self):
		self.assertTrue(validators.is_valid_economic_code("411234567890"))
		self.assertFalse(validators.is_valid_economic_code("4112345"))

	def test_mobile(self):
		for value in ("09123456789", "+989123456789", "00989123456789", "9123456789", "۰۹۱۲۳۴۵۶۷۸۹"):
			self.assertEqual(sms.try_normalize_mobile(value), "09123456789")
		self.assertFalse(validators.is_valid_mobile("02112345678"))
		with self.assertRaises(sms.SMSError):
			sms.normalize_mobile("123")
