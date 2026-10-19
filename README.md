# iran_base

Shared Iran localization for Frappe apps (Press, CRM, Helpdesk, ERPNext, HRMS). The product apps
(`crm_iran`, `erpnext_iran`, ...) depend on this one, so none of them forks Frappe core.

- `iran_base.utils.jalali` Gregorian <-> Jalali conversion and formatting (`public/js/jalali.js` mirrors it)
- `iran_base.utils.validators` national id, legal id, mobile, postal code, economic code
- `iran_base.utils.numbers` Persian/Arabic digits and Toman/Rial formatting
- `iran_base.utils.sms` mobile normalization and SMS through SignalAds or Kavenegar

Dates stay Gregorian in the database. Only display and input are Jalali.

## Site config

```json
{
  "iran_sms_provider": "signalads",
  "signalads_token": "...",
  "signalads_sender": "...",
  "kavenegar_api_key": "...",
  "kavenegar_sender": "..."
}
```

## Tests

The pure-Python helpers need no bench: `python -m unittest discover -s iran_base/tests`
