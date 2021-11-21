from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings

from notifier.models import InviteCode


@login_required
def settings_view(request):
    invite_code = request.user.person.invitecode_set.first()
    if not invite_code:
        invite_code = InviteCode(requester=request.user.person)
        invite_code.code = invite_code.generate_code()
        invite_code.save()

    context = dict(
        invite_link=f'https://t.me/{settings.TG_BOT_NAME}?start={invite_code.code}',
        code=invite_code.code,
    )

    return render(request, 'personal/settings.html', context=context)
