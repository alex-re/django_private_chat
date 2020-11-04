# TODO: Make this file markdown and better explain. 😁

3 ways for async consumers: 

1.
set this environment variable `export DJANGO_ALLOW_ASYNC_UNSAFE=True`.

2.
from asgiref.sync import sync_to_async
users = sync_to_async(User.objects.all)()
a=await users
a.first()

3.
from asgiref.sync import sync_to_async
@sync_to_async
def get_all_users():
    return User.objects.all()
async def connect():
        a=await get_all_users()
        return a
a=await connect()
a.first()

# =======================

from asgiref.sync import sync_to_async
users = sync_to_async(User.objects.all)()
a=await users
a.first()
# 
@sync_to_async
def get_all_users():
        return User.objects.all()
a=await get_all_users()
a.first()
# 
@sync_to_async
    def get_all_users():
        return User.objects.all()
async def conn():
        a=await get_all_users()
        return a
a=await conn()
a.first()