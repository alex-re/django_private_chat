from django.shortcuts import render
from .models import Dialog
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q


def index(request):
    return render(request, 'chat/index.html', {})


@login_required
def room(request, room_name):
    if room_name == request.user.username:
        return HttpResponse('Dont Chat With Your self!')
    opponent_user = User.objects.get(username=room_name)
    if Dialog.objects.filter(Q(owner=request.user, opponent=opponent_user) | Q(opponent=request.user, owner=opponent_user)).exists():
        dialog = Dialog.objects.filter(Q(owner=request.user, opponent=opponent_user) | Q(opponent=request.user, owner=opponent_user)).first()
    else:
        dialog = Dialog.objects.create(owner=request.user, opponent=opponent_user)
    return render(request, 'chat/room.html', {
        # 'room_name_json': mark_safe(json.dumps(opponent_user.username)),
        'room_name_json': opponent_user.username,
        'username': request.user.username
    })
