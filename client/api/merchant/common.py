# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from wechatpy_tornado.client.api.base import BaseWeChatAPI


class MerchantCommon(BaseWeChatAPI):

    API_BASE_URL = 'https://api.weixin.qq.com/'

    async def upload_image(self, filename, image_data):
        res = await self._post(
            'merchant/common/upload_img',
            params={
                'filename': filename
            },
            data=image_data,
            result_processor=lambda x: x['image_url']
        )
        return res
