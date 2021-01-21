# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from wechatpy_tornado.client.api.base import BaseWeChatAPI


class WeChatPoi(BaseWeChatAPI):

    async def add(self, poi_data):
        """
        创建门店

        详情请参考
        http://mp.weixin.qq.com/wiki/16/8f182af4d8dcea02c56506306bdb2f4c.html

        :param poi_data: 门店信息字典
        :return: 返回的 JSON 数据包
        """
        return await self._post('poi/addpoi', data=poi_data)

    async def get(self, poi_id):
        """
        查询门店信息

        详情请参考
        http://mp.weixin.qq.com/wiki/16/8f182af4d8dcea02c56506306bdb2f4c.html

        :param poi_id: 门店 ID
        :return: 返回的 JSON 数据包
        """
        return await self._post('poi/getpoi', data={'poi_id': poi_id})

    async def list(self, begin=0, limit=20):
        """
        查询门店列表

        详情请参考
        http://mp.weixin.qq.com/wiki/16/8f182af4d8dcea02c56506306bdb2f4c.html

        :param begin: 开始位置，0 即为从第一条开始查询
        :param limit: 返回数据条数，最大允许50，默认为20
        :return: 返回的 JSON 数据包
        """
        return await self._post(
            'poi/getpoilist',
            data={
                'begin': begin,
                'limit': limit,
            }
        )

    async def update(self, poi_data):
        """
        修改门店

        详情请参考
        http://mp.weixin.qq.com/wiki/16/8f182af4d8dcea02c56506306bdb2f4c.html

        :param poi_data: 门店信息字典
        :return: 返回的 JSON 数据包
        """
        return await self._post('poi/updatepoi', data=poi_data)

    async def delete(self, poi_id):
        """
        删除门店

        详情请参考
        http://mp.weixin.qq.com/wiki/16/8f182af4d8dcea02c56506306bdb2f4c.html

        :param poi_id: 门店 ID
        :return: 返回的 JSON 数据包
        """
        return await self._post('poi/delpoi', data={'poi_id': poi_id})

    async def get_categories(self):
        """
        获取微信门店类目表

        详情请参考
        http://mp.weixin.qq.com/wiki/16/8f182af4d8dcea02c56506306bdb2f4c.html

        :return: 门店类目表
        """
        res = await self._get(
            'api_getwxcategory',
            result_processor=lambda x: x['category_list']
        )
        return res
