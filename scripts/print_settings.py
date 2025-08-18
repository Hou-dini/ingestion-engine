from config.settings import load_settings


def redact(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "REDACTED"
    return value[:4] + "..." + value[-4:]


if __name__ == "__main__":
    settings = load_settings()

    print("--- Application Settings (redacted) ---")
    print(f"REDDIT_CLIENT_ID={redact(settings.REDDIT_CLIENT_ID)}")
    print(f"REDDIT_CLIENT_SECRET={redact(settings.REDDIT_CLIENT_SECRET)}")
    print(f"REDDIT_USER_AGENT={settings.REDDIT_USER_AGENT}")
    print(f"GCS_BUCKET_NAME={settings.GCS_BUCKET_NAME}")
    print(f"GCS_CREDENTIALS_JSON={redact(settings.GCS_CREDENTIALS_JSON)}")
    print(f"ENV={settings.sources}")
