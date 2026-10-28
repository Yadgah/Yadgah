# ⚠️ ورک‌فلوهای به‌روزشده — Updated GitHub Actions workflows

این فولدر نسخه‌ی به‌روزشده‌ی ورک‌فلوهای پروژه است (ایشوهای #202).
**این فایل‌ها اینجا اجرا نمی‌شوند!** گیت‌هاب فقط ورک‌فلوهای داخل
`.github/workflows/` را اجرا می‌کند.

## چه کاری باید انجام شود؟

هر سه فایل زیر را به فولدر `.github/workflows/` منتقل کنید (جایگزین فایل‌های
هم‌نام فعلی) و بعد این فولدر (`workflows-updated/`) را حذف کنید:

```bash
mv workflows-updated/*.yml .github/workflows/
rm -r workflows-updated
```

## تغییرات نسبت به نسخه‌ی فعلی

| فایل | تغییر |
|---|---|
| `pre-commit.yml` | ارتقاء `actions/checkout` از v3 به v7 و `actions/setup-python` از v4 به v7، فعال‌کردن کش pip، اضافه‌کردن `permissions: contents: read` |
| `security-check.yml` | همان ارتقاء اکشن‌ها + جایگزینی `safety check` (که دیگر بدون حساب/API Key کار نمی‌کند) با `pip-audit` + اجرای خودکار روی PRهایی که `requirements.txt` را تغییر می‌دهند |
| `release.yml` | ارتقاء اکشن‌ها + نسخه‌ی پایتون از 3.10 به 3.13 برای یکدستی با بقیه‌ی ورک‌فلوها |

بعد از انتقال، Dependabot (پیکربندی‌شده در
[`.github/dependabot.yml`](../.github/dependabot.yml)) به‌صورت خودکار و
هفتگی، هم وابستگی‌های پایتون (`requirements.txt`) و هم نسخه‌ی اکشن‌های
گیت‌هاب را به‌روز نگه می‌دارد و برای آسیب‌پذیری‌های امنیتی PR باز می‌کند.
