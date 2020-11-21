###### TODO: Write better documents in this file.
# Three ways for async chat consumers:
1. set **DJANGO_ALLOW_ASYNC_UNSAFE** environment variable **True**.
 mac & linux 😎 `export DJANGO_ALLOW_ASYNC_UNSAFE=True`.
###### (Just this item work for async channels)
___
2. 
```py
from asgiref.sync import sync_to_async

users = sync_to_async(User.objects.all)()
all_users = await users
all_users.first()
```
___
3. 
```py 
from asgiref.sync import sync_to_async

@sync_to_async
def get_all_users():
    return User.objects.all()

async def connect():
    users = await get_all_users()
    return users

all_users = await connect()
a.first()
```