// Jalali dates on the desk. The database and the API keep Gregorian 'YYYY-MM-DD'; only what a person
// reads or types is Jalali. Switched by "Use Jalali Dates" in Iran Settings (frappe.boot.iran_base).
(function () {
	const base = () => window.iran_base;
	const WEEKDAYS = ['ی', 'د', 'س', 'چ', 'پ', 'ج', 'ش']; // Sunday first, like Date#getDay()
	const pad = (n, len = 2) => String(n).padStart(len, '0');

	// Persian (۰-۹) and Arabic-Indic (٠-٩) digits -> 0-9
	function toLatin(text) {
		return String(text).replace(/[۰-۹٠-٩]/g, (c) => {
			const code = c.charCodeAt(0);
			return code >= 0x06f0 ? code - 0x06f0 : code - 0x0660;
		});
	}

	function userFormat() {
		return (frappe.datetime.get_user_date_fmt() || 'yyyy-mm-dd').toLowerCase();
	}

	// Position of year, month and day in the user's date format, e.g. 'dd-mm-yyyy' -> ['d', 'm', 'y']
	function formatOrder() {
		return (userFormat().match(/yyyy|mm|dd/g) || ['yyyy', 'mm', 'dd']).map((token) => token[0]);
	}

	function formatJalaliParts(jy, jm, jd) {
		return userFormat().replace('yyyy', pad(jy, 4)).replace('mm', pad(jm)).replace('dd', pad(jd));
	}

	function daysInJalaliMonth(jy, jm) {
		if (jm <= 6) return 31;
		if (jm <= 11) return 30;
		// Esfand has 30 days in a leap year: day 30 survives a round trip through Gregorian
		const back = base().gregorianToJalali(...base().jalaliToGregorian(jy, 12, 30));
		return back[0] === jy && back[1] === 12 && back[2] === 30 ? 30 : 29;
	}

	// A moment (already in the zone the person sees) -> '1404-01-01' in the user's format
	function jalaliFromMoment(m) {
		const [jy, jm, jd] = base().gregorianToJalali(m.year(), m.month() + 1, m.date());
		return formatJalaliParts(jy, jm, jd);
	}

	// Text typed or pasted by a person -> 'YYYY-MM-DD' (Gregorian) or null.
	// A year of 1700 or more is read as Gregorian, so a pasted '2025-03-21' still works.
	function parseUserDate(text) {
		const numbers = toLatin(text).match(/\d+/g);
		if (!numbers || numbers.length < 3) return null;
		const order = formatOrder();
		const parts = {};
		order.forEach((key, i) => (parts[key] = parseInt(numbers[i], 10)));
		let { y, m, d } = parts;
		if (numbers[order.indexOf('y')].length <= 2) y += 1400;
		if (!(m >= 1 && m <= 12 && d >= 1)) return null;
		let gy, gm, gd;
		if (y >= 1700) {
			[gy, gm, gd] = [y, m, d];
			const check = moment([gy, gm - 1, gd]);
			if (!check.isValid() || check.date() !== gd) return null;
		} else {
			if (d > daysInJalaliMonth(y, m)) return null;
			[gy, gm, gd] = base().jalaliToGregorian(y, m, d);
		}
		return `${pad(gy, 4)}-${pad(gm)}-${pad(gd)}`;
	}

	function patchDatetime() {
		const dt = frappe.datetime;
		const original = {
			str_to_user: dt.str_to_user,
			user_to_str: dt.user_to_str,
		};

		dt.str_to_user = function (val, only_time = false, only_date = false) {
			if (!val || only_time) return original.str_to_user.apply(this, arguments);
			if (only_date || (typeof val === 'string' && val.indexOf(' ') === -1)) {
				const date = moment(val, frappe.defaultDateFormat);
				return date.isValid() ? jalaliFromMoment(date) : original.str_to_user.apply(this, arguments);
			}
			const system = moment.tz(val, frappe.defaultDatetimeFormat, frappe.boot.time_zone.system);
			if (!system.isValid()) return original.str_to_user.apply(this, arguments);
			const user = system.clone().tz(frappe.boot.time_zone.user);
			return jalaliFromMoment(user) + ' ' + user.format(dt.get_user_time_fmt());
		};

		dt.user_to_str = function (val, only_time = false) {
			if (only_time || !val) return original.user_to_str.apply(this, arguments);
			const text = String(val).trim();
			const space = text.indexOf(' ');
			const date = parseUserDate(space === -1 ? text : text.slice(0, space));
			if (!date) return 'Invalid date';
			if (space === -1) return date;
			const time = moment(toLatin(text.slice(space + 1)), dt.get_user_time_fmt());
			return time.isValid() ? `${date} ${time.locale('en').format('HH:mm:ss')}` : 'Invalid date';
		};

		dt.obj_to_user = function (d) {
			return jalaliFromMoment(moment(d));
		};
	}

	// A calendar that replaces the popup of the stock date picker. The stock picker object stays in place
	// (hidden) because the form code reads its selected date and time; this only chooses the day.
	class JalaliPicker {
		constructor(control) {
			this.control = control;
			this.$input = control.$input;
			this.withTime = control.df.fieldtype === 'Datetime';
			this.range = control.df.fieldtype === 'DateRange';
			this.ns = '.jalali' + Math.random().toString(36).slice(2);
			this.$el = $('<div class="iran-jalali-picker" dir="rtl" style="display:none"></div>').appendTo('body');
			this.$input.on('focus' + this.ns + ' click' + this.ns, () => this.open());
			this.$input.on('keydown' + this.ns, (e) => {
				if (e.key === 'Escape' || e.key === 'Tab') this.close();
			});
			$(document).on('mousedown' + this.ns, (e) => {
				if (!this.visible) return;
				if (this.$el.is(e.target) || this.$el.has(e.target).length || this.$input.is(e.target)) return;
				this.close();
			});
			// Keep focus where it is while clicking inside the calendar, except in the time field
			this.$el.on('mousedown', (e) => {
				if (!$(e.target).is('input')) e.preventDefault();
			});
			// The control's wrapper goes away with its form or dialog; clean up with it
			this.$input.on('remove' + this.ns, () => this.destroy());
		}

		// A range field holds '01-01-1404 to 25-01-1404': the two ISO dates, or an empty range
		currentRange() {
			const separator = __('{0} to {1}').replace('{0}', '').replace('{1}', '');
			const parts = String(this.$input.val() || '').split(separator);
			const [start, end] = parts.length === 2 ? parts.map(parseUserDate) : [null, null];
			return start && end ? { start, end } : { start: null, end: null };
		}

		current() {
			if (this.range) {
				const { start } = this.currentRange();
				return start ? moment(start, 'YYYY-MM-DD') : null;
			}
			// What the person sees in the input, as Gregorian wall-clock time
			const system = this.$input.val() ? frappe.datetime.user_to_str(this.$input.val()) : '';
			const m = system && system !== 'Invalid date' ? moment(system, 'YYYY-MM-DD HH:mm:ss') : null;
			return m && m.isValid() ? m : null;
		}

		nowInUserZone() {
			const tz = frappe.boot.time_zone && frappe.boot.time_zone.user;
			return tz ? moment.tz(tz) : moment();
		}

		open() {
			if (this.visible || this.control.df.read_only) return;
			const selected = this.current();
			const shown = selected || this.nowInUserZone();
			const [jy, jm] = base().gregorianToJalali(shown.year(), shown.month() + 1, shown.date());
			this.view = { jy, jm };
			this.selected = selected;
			this.pending = null;
			this.rangeValue = this.range ? this.currentRange() : null;
			this.time = (selected || this.nowInUserZone()).format('HH:mm:ss');
			this.visible = true;
			this.render();
			this.$el.show();
			this.position();
		}

		close() {
			this.visible = false;
			this.$el.hide();
		}

		destroy() {
			this.$input.off(this.ns);
			$(document).off(this.ns);
			this.$el.remove();
		}

		position() {
			const rect = this.$input[0].getBoundingClientRect();
			const height = this.$el.outerHeight();
			const width = this.$el.outerWidth();
			const below = window.innerHeight - rect.bottom;
			const top = below < height + 8 && rect.top > height + 8 ? rect.top - height - 4 : rect.bottom + 4;
			const left = Math.max(8, Math.min(rect.left, window.innerWidth - width - 8));
			this.$el.css({ top, left });
		}

		bounds() {
			const toIso = (v) => (v ? moment(v).format('YYYY-MM-DD') : null);
			return { min: toIso(this.control.df.min_date), max: toIso(this.control.df.max_date) };
		}

		render() {
			const { jy, jm } = this.view;
			const digits = (v) => base().toPersianDigits(v);
			const first = frappe.datetime.get_first_day_of_the_week_index();
			const [fy, fm, fd] = base().jalaliToGregorian(jy, jm, 1);
			const offset = (new Date(fy, fm - 1, fd).getDay() - first + 7) % 7;
			const total = daysInJalaliMonth(jy, jm);
			const todayIso = this.nowInUserZone().format('YYYY-MM-DD');
			const selectedIso = this.selected ? this.selected.format('YYYY-MM-DD') : null;
			const { min, max } = this.bounds();
			const disabled = this.control.df.disabled_dates || [];

			let cells = '';
			for (let i = 0; i < offset; i++) cells += '<span class="jp-cell jp-empty"></span>';
			for (let day = 1; day <= total; day++) {
				const [gy, gm, gd] = base().jalaliToGregorian(jy, jm, day);
				const iso = `${pad(gy, 4)}-${pad(gm)}-${pad(gd)}`;
				const off = (min && iso < min) || (max && iso > max) || disabled.includes(iso);
				const classes = ['jp-cell', 'jp-day'];
				if (iso === todayIso) classes.push('jp-today');
				if (this.range) {
					const { start, end } = this.rangeValue;
					if (iso === start || iso === end) classes.push('jp-selected');
					else if (start && end && iso > start && iso < end) classes.push('jp-inrange');
				} else if (iso === selectedIso) classes.push('jp-selected');
				if (off) classes.push('jp-disabled');
				cells += `<button type="button" class="${classes.join(' ')}" data-iso="${iso}" ${off ? 'disabled' : ''}>${digits(day)}</button>`;
			}

			const names = [];
			for (let i = 0; i < 7; i++) names.push(`<span class="jp-cell jp-weekday">${WEEKDAYS[(first + i) % 7]}</span>`);

			const time = this.withTime
				? `<div class="jp-time"><input type="text" class="jp-time-input" value="${this.time}" maxlength="8" dir="ltr"></div>`
				: '';

			this.$el.html(`
				<div class="jp-head">
					<button type="button" class="jp-nav" data-step="-12" title="${__('Previous year')}">»</button>
					<button type="button" class="jp-nav" data-step="-1" title="${__('Previous month')}">›</button>
					<span class="jp-title">${base().MONTHS[jm - 1]} ${digits(jy)}</span>
					<button type="button" class="jp-nav" data-step="1" title="${__('Next month')}">‹</button>
					<button type="button" class="jp-nav" data-step="12" title="${__('Next year')}">«</button>
				</div>
				<div class="jp-grid">${names.join('')}${cells}</div>
				${time}
				<div class="jp-foot"><button type="button" class="jp-today-btn">${this.withTime ? __('Now') : __('Today')}</button></div>
			`);

			this.$el.find('.jp-nav').on('click', (e) => {
				const step = parseInt($(e.currentTarget).data('step'), 10);
				const index = this.view.jy * 12 + (this.view.jm - 1) + step;
				this.view = { jy: Math.floor(index / 12), jm: (index % 12) + 1 };
				this.render();
			});
			this.$el.find('.jp-day').on('click', (e) => this.choose($(e.currentTarget).data('iso')));
			this.$el.find('.jp-today-btn').on('click', () => {
				const now = this.nowInUserZone();
				if (this.withTime) this.time = now.format('HH:mm:ss');
				this.choose(now.format('YYYY-MM-DD'));
			});
			this.$el.find('.jp-time-input').on('input', (e) => {
				this.time = toLatin(e.target.value);
				if (this.selected) this.apply(this.selected.format('YYYY-MM-DD'), false, false);
			});
		}

		jalaliText(iso) {
			const [y, m, d] = iso.split('-').map(Number);
			return formatJalaliParts(...base().gregorianToJalali(y, m, d));
		}

		// First click picks the start, second the end (the earlier day is always the start)
		chooseRange(iso) {
			if (!this.pending) {
				this.pending = iso;
				this.rangeValue = { start: iso, end: null };
				this.render();
				return;
			}
			const [start, end] = [this.pending, iso].sort();
			this.pending = null;
			this.rangeValue = { start, end };
			this.$input.val(__('{0} to {1}', [this.jalaliText(start), this.jalaliText(end)])).trigger('change');
			this.close();
		}

		choose(iso) {
			if (this.range) return this.chooseRange(iso);
			this.selected = moment(iso, 'YYYY-MM-DD');
			this.apply(iso, !this.withTime, true);
		}

		// Writes the chosen day (and time) to the input as Jalali text and lets the form take it from there
		apply(iso, closeAfter, rerender) {
			const [y, m, d] = iso.split('-').map(Number);
			const [jy, jm, jd] = base().gregorianToJalali(y, m, d);
			let text = formatJalaliParts(jy, jm, jd);
			let date = new Date(y, m - 1, d);
			if (this.withTime) {
				const time = moment(this.time, 'HH:mm:ss');
				if (!time.isValid()) return;
				text += ' ' + time.format(frappe.datetime.get_user_time_fmt());
				date = new Date(y, m - 1, d, time.hours(), time.minutes(), time.seconds());
			}
			this.$input.val(text);
			// The stock onSelect triggers the change event the form listens to
			this.control.datepicker.selectDate(date);
			if (closeAfter) this.close();
			else if (rerender) this.render();
		}
	}

	function patchControls() {
		const proto = frappe.ui.form.ControlDate.prototype;
		if (proto._jalali) return;
		proto._jalali = true;

		const setDateOptions = proto.set_date_options;
		proto.set_date_options = function () {
			setDateOptions.apply(this, arguments);
			// No stock popup: the Jalali calendar opens instead
			this.datepicker_options.showEvent = 'jalali-none';
		};

		const setDatepicker = proto.set_datepicker;
		proto.set_datepicker = function () {
			setDatepicker.apply(this, arguments);
			// A Time field has no calendar and keeps its stock picker
			if (this.timepicker_only) return;
			// The stock picker would write its Gregorian text into the input after every selection
			this.datepicker._setInputValue = function () {};
			this.jalali_picker = new JalaliPicker(this);
		};
	}

	// The date range of list filters and reports: same calendar, two clicks
	function patchRangeControl() {
		const proto = frappe.ui.form.ControlDateRange.prototype;
		if (proto._jalali) return;
		proto._jalali = true;

		const setDateOptions = proto.set_date_options;
		proto.set_date_options = function () {
			setDateOptions.apply(this, arguments);
			this.datepicker_options.showEvent = 'jalali-none';
		};

		const setDatepicker = proto.set_datepicker;
		proto.set_datepicker = function () {
			setDatepicker.apply(this, arguments);
			this.datepicker._setInputValue = function () {};
			this.jalali_picker = new JalaliPicker(this);
		};
	}

	function start() {
		if (!(frappe.boot.iran_base && frappe.boot.iran_base.jalali_dates)) return;
		patchDatetime();
		patchControls();
		patchRangeControl();
	}

	$(document).on('startup', start);
})();
