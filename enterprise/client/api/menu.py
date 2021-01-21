# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from wechatpy_tornado.client.api.base import BaseWeChatAPI


class WeChatMenu(BaseWeChatAPI):
    """
    自定义菜单

    https://work.weixin.qq.com/api/doc#90000/90135/90230
    """

    async def create(self, agent_id, menu_data):
        """
        创建菜单

        https://work.weixin.qq.com/api/doc#90000/90135/90231

        :param agent_id: 应用id
        """
        return await self._post(
            'menu/create',
            params={
                'agentid': agent_id
            },
            data=menu_data
        )

    async def get(self, agent_id):
        """
        获取菜单

        https://work.weixin.qq.com/api/doc#90000/90135/90232

        :param agent_id: 应用id
        """
        return await self._get(
            'menu/get',
            params={
                'agentid': agent_id
            }
        )

    async def delete(self, agent_id):
        """
        删除菜单

        https://work.weixin.qq.com/api/doc#90000/90135/90233

        :param agent_id: 应用id
        """
        return await self._get(
            'menu/delete',
            params={
                'agentid': agent_id
            }
        )

    async def update(self, agent_id, menu_data):
        await self.delete(agent_id)
        return await self.create(agent_id, menu_data)
