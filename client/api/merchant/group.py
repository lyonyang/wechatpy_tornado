# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from wechatpy_tornado.client.api.base import BaseWeChatAPI


class MerchantGroup(BaseWeChatAPI):

    API_BASE_URL = 'https://api.weixin.qq.com/'

    async def add(self, name, product_list):
        return await self._post(
            'merchant/group/add',
            data={
                'group_detail': {
                    'group_name': name,
                    'product_list': product_list
                }
            }
        )

    async def delete(self, group_id):
        return await self._post(
            'merchant/group/del',
            data={
                'group_id': group_id
            }
        )

    async def update(self, group_id, name):
        return await self._post(
            'merchant/group/propertymod',
            data={
                'group_id': group_id,
                'group_name': name
            }
        )

    async def update_product(self, group_id, product):
        return await self._post(
            'merchant/group/productmod',
            data={
                'group_id': group_id,
                'product': product
            }
        )

    async def get_all(self):
        res = await self._get(
            'merchant/group/getall',
            result_processor=lambda x: x['groups_detail']
        )
        return res

    async def get(self, group_id):
        res = await self._post(
            'merchant/group/getbyid',
            data={
                'group_id': group_id
            },
            result_processor=lambda x: x['group_detail']
        )
        return res
