from telegram import Update
from telegram.ext import CallbackContext

from notifier.handlers.start import message_text
from notifier.models import InviteCode
from notifier.utils import extract_user_data_from_update
from personal.models import Person


def proceed_code(user_id: str, code: str) -> str:
    """Returns reply text."""
    invite_code = InviteCode.objects.filter(code=code, requester__telegram_id=None).first()

    if not invite_code:
        return message_text.CODE_ALREADY_USED

    invite_code.requester.telegram_id = user_id
    invite_code.requester.save()

    return message_text.REGISTERED


def command_start(update: Update, context: CallbackContext) -> None:
    if Person.get_person(update):
        update.message.reply_text(message_text.ALREADY_REGISTERED)
        return

    if context.args and context.args[0].isnumeric():
        user_id = extract_user_data_from_update(update)['user_id']
        reply_text = proceed_code(user_id, context.args[0])
        update.message.reply_text(reply_text)
        return

    update.message.reply_text(message_text.NEW_USER)


def message_invite_code(update: Update, context: CallbackContext) -> None:
    if Person.get_person(update):
        update.message.reply_text(message_text.ALREADY_REGISTERED)
        return

    user_id = extract_user_data_from_update(update)['user_id']
    reply_text = proceed_code(user_id, update.message.text)
    update.message.reply_text(reply_text)
