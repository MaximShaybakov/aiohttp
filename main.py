import datetime
import json
from sqlalchemy.future import select
from aiohttp import web
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import PG_DSN, TOKEN_TTL
from typing import Callable, Awaitable
from models import Base, User, Token, Ads
from auth import hash_password, check_password

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


async def check_auth(request: web.Request):
    token_id = request.headers.get('token')
    if not token_id:
        raise_error(web.HTTPForbidden, message='incorrect token')
    try:
        token = await get_orm_item(Token, token_id, request['session'])
    except web.HTTPNotFound:
        raise_error(web.HTTPForbidden, message='incorrect token')
    if token.created + datetime.timedelta(seconds=TOKEN_TTL) < datetime.datetime.utcnow():
        raise_error(web.HTTPForbidden, message='incorrect token')
    request['token'] = token


async def check_owner(request: web.Request, owner_id: int):
    if request['token'].user.id != owner_id:
        raise_error(web.HTTPForbidden, message='token incorrect')


async def get_orm_item(orm_class, object_id, sessions):
    item = await sessions.get(orm_class, object_id)
    if item is None:
        raise raise_error(web.HTTPNotFound, f'{orm_class.__name__} not found')
    return item


async def login(request: web.Request):
    user_data = await request.json()
    query = select(User).where(User.name == user_data['name'])
    result = await request['session'].execute(query)
    user = result.scalar()
    if not user or not check_password(user_data['password'], user.password):
        raise raise_error(web.HTTPUnauthorized, message='user or password is incorrect')
    token = Token(user=user)
    request['session'].add(token)
    await request['session'].commit()
    return web.json_response({'status': 'success', 'token': token.id})


class UsersView(web.View):
    """ GET, CREATE, PATCH, DELETE users """

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
        return web.json_response({'status': 'success'})

    async def delete(self):
        # await check_auth(self.request)
        user_id = int(self.request.match_info['user_id'])
        # await check_owner(self.request, user_id)
        user = await get_orm_item(User, user_id, self.request['session'])
        await self.request['session'].delete(user)
        await self.request['session'].commit()
        return web.json_response({'status': 'delete'})


class AdsView(web.View):
    """ GET, CREATE, PATCH, DELETE advertisements """

    async def get(self):
        ads_id = int(self.request.match_info['id'])
        ads = await get_orm_item(Ads, ads_id, self.request['session'])
        return web.json_response({'id': ads.id, 'title': ads.title})

    async def post(self):
        ads_data = await self.request.json()
        new_ads = Ads(**ads_data)
        self.request['session'].add(new_ads)
        await self.request['session'].commit()
        return web.json_response({
            'status': 'OK',
            'ads_id': new_ads.id
        })

    async def patch(self):
        ads_id = int(self.request.match_info['id'])
        ads = await get_orm_item(Ads, ads_id, self.request['session'])
        ads_data = await self.request.json()
        for field, value in ads_data.items():
            setattr(ads, field, value)
        self.request['session'].add(ads)
        await self.request['session'].commit()
        return web.json_response({'status': 'success'})


my_app = web.Application(middlewares=[session_middleware])
my_app.cleanup_ctx.append(app_context)

my_app.add_routes(
    [
        web.post('/login', login),
        web.post('/users/', UsersView),
        web.get('/users/{user_id:\d+}', UsersView),
        web.patch('/users/{user_id:\d+}', UsersView),
        web.delete('/users/{user_id:\d+}', UsersView),
        web.get('/ads/{id:\d+}', AdsView),
        web.post('/ads/', AdsView),
    ]
)

if __name__ == '__main__':
    web.run_app(my_app, host='127.0.0.1', port=8080)
