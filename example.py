import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession('http://httpbin.org') as session:  # base url

        params = {'key': 'value', 'key1': 'value1'}  # передать параметры в URL адресе
        async with session.get('/get', params=params) as resp:  # base url + /get
            expect = 'http://httpbin.org/get?key=value&key1=value1'  # output base url + /get
            print(resp.real_url)
            print(resp.text(encoding='utf-8'))

        # async with session.post('/post', json={'test': 'object'}):
        #     pass
        #
        # async with session.put('/put', data=b'data'):
        #     pass

asyncio.run(main())
