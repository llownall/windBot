if __name__ == '__main__':
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "windBot.settings")
    django.setup()

    from notifier.service import TelegramBot

    bot = TelegramBot()
    bot.start_polling()
