# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from optionaldict import optionaldict
from wechatpy_tornado.client.api.base import BaseWeChatAPI


class MerchantOrder(BaseWeChatAPI):

    API_BASE_URL = 'https://api.weixin.qq.com/'

    async def get(self, order_id):
        res = await self._post(
            'merchant/order/getbyid',
            data={
                'order_id': order_id
            },
            result_processor=lambda x: x['order']
        )
        return res

    async def get_by_filter(self, status=None, begin_time=None, end_time=None):
        filter_dict = optionaldict(
            status=status,
            begintime=begin_time,
            endtime=end_time
        )

        res = await self._post(
            'merchant/order/getbyfilter',
            data=dict(filter_dict),
            result_processor=lambda x: x['order_list']
        )
        return res

    async def set_delivery(self, order_id, company, track_no,
                     need_delivery=1, is_others=0):
        return await self._post(
            'merchant/order/setdelivery',
            data={
                'order_id': order_id,
                'delivery_company': company,
                'delivery_track_no': track_no,
                'need_delivery': need_delivery,
                'is_others': is_others
            }
        )

    async def close(self, order_id):
        return await self._post(
            'merchant/order/close',
            data={
                'order_id': order_id
            }
        )
