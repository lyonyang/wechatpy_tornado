# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from wechatpy_tornado.client.api.base import BaseWeChatAPI


class WeChatTag(BaseWeChatAPI):
    """
    标签管理

    https://work.weixin.qq.com/api/doc#90000/90135/90209
    """

    async def create(self, name):
        return await self._post(
            'tag/create',
            data={
                'tagname': name
            }
        )

    async def update(self, tag_id, name):
        return await self._post(
            'tag/update',
            data={
                'tagid': tag_id,
                'tagname': name
            }
        )

    async def delete(self, tag_id):
        return await self._get(
            'tag/delete',
            params={
                'tagid': tag_id
            }
        )

    async def get_users(self, tag_id):
        return await self._get(
            'tag/get',
            params={
                'tagid': tag_id
            }
        )

    async def add_users(self, tag_id, user_ids):
        return await self._post(
            'tag/addtagusers',
            data={
                'tagid': tag_id,
                'userlist': user_ids
            }
        )

    async def delete_users(self, tag_id, user_ids):
        return await self._post(
            'tag/deltagusers',
            data={
                'tagid': tag_id,
                'userlist': user_ids
            }
        )

    async def list(self):
        res = await self._get('tag/list')
        return res['taglist']
