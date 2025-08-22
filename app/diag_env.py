from app.config import settings
print("len(token) =", len(settings.bot_token))
print("prefix =", settings.bot_token[:12])
print("admin_id =", settings.admin_id)