# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from wechatpy_tornado.client.api.base import BaseWeChatAPI


class MerchantShelf(BaseWeChatAPI):

    API_BASE_URL = 'https://api.weixin.qq.com/'

    async def add(self, name, banner, shelf_data):
        return await self._post(
            'merchant/shelf/add',
            data={
                'shelf_name': name,
                'shelf_banner': banner,
                'shelf_data': shelf_data
            }
        )

    async def delete(self, shelf_id):
        return await self._post(
            'merchant/shelf/del',
            data={
                'shelf_id': shelf_id
            }
        )

    async def update(self, shelf_id, name, banner, shelf_data):
        return await self._post(
            'merchant/shelf/add',
            data={
                'shelf_id': shelf_id,
                'shelf_name': name,
                'shelf_banner': banner,
                'shelf_data': shelf_data
            }
        )

    async def get_all(self):
        res = await self._get(
            'merchant/shelf/getall',
            result_processor=lambda x: x['shelves']
        )
        return res

    async def get(self, shelf_id):
        return await self._post(
            'merchant/shelf/getbyid',
            data={
                'shelf_id': shelf_id
            }
        )
