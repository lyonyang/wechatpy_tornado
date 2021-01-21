# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from wechatpy_tornado.client.api.base import BaseWeChatAPI


class MerchantExpress(BaseWeChatAPI):

    API_BASE_URL = 'https://api.weixin.qq.com/'

    async def add(self, delivery_template):
        return await self._post(
            'merchant/express/add',
            data={
                'delivery_template': delivery_template
            }
        )

    async def delete(self, template_id):
        return await self._post(
            'merchant/express/del',
            data={
                'template_id': template_id
            }
        )

    async def update(self, template_id, delivery_template):
        return await self._post(
            'merchant/express/update',
            data={
                'template_id': template_id,
                'delivery_template': delivery_template
            }
        )

    async def get(self, template_id):
        res = await self._post(
            'merchant/express/getbyid',
            data={
                'template_id': template_id
            },
            result_processor=lambda x: x['template_info']
        )
        return res

    async def get_all(self):
        res = await self._get(
            'merchant/express/getall',
            result_processor=lambda x: x['template_info']
        )
        return res
