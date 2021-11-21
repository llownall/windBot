from telegram import Bot
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, Filters

from django.conf import settings

from notifier.handlers.start import handlers as start_handlers


class TelegramBot:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TelegramBot, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        self._updater = Updater(settings.TG_TOKEN)
        self._dispatcher = self._updater.dispatcher  # type: Dispatcher
        self._bot = self._updater.bot  # type: Bot

    def _setup_dispatcher(self):
        handlers = [
            CommandHandler('start', start_handlers.command_start),
            MessageHandler(Filters.regex(r'^\d{6}$'), start_handlers.message_invite_code),
        ]

        for handler in handlers:
            self._dispatcher.add_handler(handler)

    def start_polling(self):
        self._setup_dispatcher()

        self._bot.send_message(settings.TG_ADMIN_CHAT_ID, '👋')

        self._updater.start_polling()
        self._updater.idle()

    def send_message(self, *args, **kwargs):
        return self._bot.send_message(*args, **kwargs)
