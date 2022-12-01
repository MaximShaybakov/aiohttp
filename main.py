import json

from aiohttp import web
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import PG_DSN
from typing import Callable, Awaitable
from models import Base, User  # Token, Ads
from auth import hash_password  # check_password

engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@web.middleware
async def session_middleware(request: web.Request, handler: Callable[[web.Request], Awaitable[web.Response]]):
    async with Session() as session:
        request['session'] = session
        return await handler(request)


async def app_context(app: web.Application):
    async with engine.begin() as conn:
        async with Session() as session:
            await session.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            await session.commit()
        await conn.run_sync(Base.metadata.create_all)
    print('START')
    yield
    print('FINISH')
    await engine.dispose()


def raise_error(exception_class, message):
    raise exception_class(
        text=json.dumps({'status': 'error', 'message': message}),
        content_type='application/json'
    )


async def get_orm_item(orm_class, object_id, sessions):
    item = await sessions.get(orm_class, object_id)
    if item is None:
        raise raise_error(web.HTTPNotFound, f'{orm_class.__name__} not found')
    return item


async def login(request: web.Request):
    return web.json_response({})


class UsersView(web.View):
    ''' GET, CREATE, PATCH, DELETE users '''

    async def get(self):
        user_id = int(self.request.match_info['user_id'])
        user = await get_orm_item(User, user_id, self.request['session'])
        return web.json_response({'id': user.id, 'name': user.name})

    async def post(self):
        user_data = await self.request.json()
        user_data['password'] = hash_password(user_data['password'])
        new_user = User(**user_data)
        self.request['session'].add(new_user)
        await self.request['session'].commit()
        return web.json_response({
            'status': 'OK',
            'id': new_user.id
        })

    async def patch(self):
        user_id = int(self.request.match_info['user_id'])
        user = await get_orm_item(User, user_id, self.request['session'])
        user_data = await self.request.json()
        if 'password' in user_data:
            user_data['password'] = hash_password(user_data['password'])
        for field, value in user_data.items():
            setattr(user, field, value)
        self.request['session'].add(user)
        await self.request['session'].commit()
        return web.json_response({})

    async def delete(self, user_id: int):
        return web.json_response({})


my_app = web.Application(middlewares=[session_middleware])
my_app.cleanup_ctx.append(app_context)

my_app.add_routes(
    [
        web.post('/users/', UsersView),
        web.get('/users/{user_id:\d+}', UsersView),
        web.patch('/users/{user_id:\d+}', UsersView),
    ]
)

if __name__ == '__main__':
    web.run_app(my_app, host='127.0.0.1', port=8080)
