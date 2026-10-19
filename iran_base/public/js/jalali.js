// Mirror of iran_base/utils/jalali.py. Dates are stored Gregorian; these only convert for display and input.
(function () {
	const G_DAYS = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
	const MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'];
	const PERSIAN = '۰۱۲۳۴۵۶۷۸۹';

	function gregorianToJalali(gy, gm, gd) {
		let jy;
		if (gy > 1600) {
			jy = 979;
			gy -= 1600;
		} else {
			jy = 0;
			gy -= 621;
		}
		const gy2 = gm > 2 ? gy + 1 : gy;
		let days =
			365 * gy + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100) + Math.floor((gy2 + 399) / 400) - 80 + gd + G_DAYS[gm - 1];
		jy += 33 * Math.floor(days / 12053);
		days %= 12053;
		jy += 4 * Math.floor(days / 1461);
		days %= 1461;
		if (days > 365) {
			jy += Math.floor((days - 1) / 365);
			days = (days - 1) % 365;
		}
		if (days < 186) return [jy, 1 + Math.floor(days / 31), 1 + (days % 31)];
		return [jy, 7 + Math.floor((days - 186) / 30), 1 + ((days - 186) % 30)];
	}

	function jalaliToGregorian(jy, jm, jd) {
		jy += 1595;
		let days = -355668 + 365 * jy + Math.floor(jy / 33) * 8 + Math.floor(((jy % 33) + 3) / 4) + jd;
		days += jm < 7 ? (jm - 1) * 31 : (jm - 7) * 30 + 186;
		let gy = 400 * Math.floor(days / 146097);
		days %= 146097;
		if (days > 36524) {
			days -= 1;
			gy += 100 * Math.floor(days / 36524);
			days %= 36524;
			if (days >= 365) days += 1;
		}
		gy += 4 * Math.floor(days / 1461);
		days %= 1461;
		if (days > 365) {
			gy += Math.floor((days - 1) / 365);
			days = (days - 1) % 365;
		}
		let gd = days + 1;
		const leap = (gy % 4 === 0 && gy % 100 !== 0) || gy % 400 === 0;
		const md = [0, 31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
		let gm = 1;
		while (gm < 13 && gd > md[gm]) {
			gd -= md[gm];
			gm++;
		}
		return [gy, gm, gd];
	}

	function toPersianDigits(value) {
		return String(value).replace(/\d/g, (d) => PERSIAN[d]);
	}

	// '2024-03-20' -> '1403-01-01' (or '۱۴۰۳-۰۱-۰۱')
	function formatJalali(isoDate, persian = false) {
		const [y, m, d] = isoDate.slice(0, 10).split('-').map(Number);
		const [jy, jm, jd] = gregorianToJalali(y, m, d);
		const text = `${String(jy).padStart(4, '0')}-${String(jm).padStart(2, '0')}-${String(jd).padStart(2, '0')}`;
		return persian ? toPersianDigits(text) : text;
	}

	window.iran_base = Object.assign(window.iran_base || {}, {
		MONTHS,
		gregorianToJalali,
		jalaliToGregorian,
		formatJalali,
		toPersianDigits,
	});
})();
