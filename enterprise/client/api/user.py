# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from optionaldict import optionaldict

from wechatpy_tornado.client.api.base import BaseWeChatAPI


class WeChatUser(BaseWeChatAPI):
    """
    成员管理

    https://work.weixin.qq.com/api/doc#90000/90135/90194

    邀请成员接口位于 `WeChatBatch.invite`
    """

    async def create(self, user_id, name, department=None, position=None,
               mobile=None, gender=0, tel=None, email=None,
               weixin_id=None, extattr=None, **kwargs):
        """
        创建成员

        https://work.weixin.qq.com/api/doc#90000/90135/90195
        """
        user_data = optionaldict()
        user_data['userid'] = user_id
        user_data['name'] = name
        user_data['gender'] = gender
        user_data['department'] = department
        user_data['position'] = position
        user_data['mobile'] = mobile
        user_data['tel'] = tel
        user_data['email'] = email
        user_data['weixinid'] = weixin_id
        user_data['extattr'] = extattr
        user_data.update(kwargs)

        return await self._post(
            'user/create',
            data=user_data
        )

    async def get(self, user_id):
        """
        读取成员

        https://work.weixin.qq.com/api/doc#90000/90135/90196
        """
        return await self._get(
            'user/get',
            params={
                'userid': user_id
            }
        )

    async def update(self, user_id, name=None, department=None, position=None,
               mobile=None, gender=None, tel=None, email=None,
               weixin_id=None, enable=None, extattr=None, **kwargs):
        """
        更新成员

        https://work.weixin.qq.com/api/doc#90000/90135/90197
        """
        user_data = optionaldict()
        user_data['userid'] = user_id
        user_data['name'] = name
        user_data['gender'] = gender
        user_data['department'] = department
        user_data['position'] = position
        user_data['mobile'] = mobile
        user_data['tel'] = tel
        user_data['email'] = email
        user_data['weixinid'] = weixin_id
        user_data['extattr'] = extattr
        user_data['enable'] = enable
        user_data.update(kwargs)

        return await self._post(
            'user/update',
            data=user_data
        )

    async def delete(self, user_id):
        """
        删除成员

        https://work.weixin.qq.com/api/doc#90000/90135/90198
        """
        return await self._get(
            'user/delete',
            params={
                'userid': user_id
            }
        )

    async def batch_delete(self, user_ids):
        """
        批量删除成员

        https://work.weixin.qq.com/api/doc#90000/90135/90199
        """
        return await self._post(
            'user/batchdelete',
            data={
                'useridlist': user_ids
            }
        )

    async def list(self, department_id, fetch_child=False, status=0, simple=False):
        """
        批量获取部门成员 / 批量获取部门成员详情

        https://work.weixin.qq.com/api/doc#90000/90135/90200
        https://work.weixin.qq.com/api/doc#90000/90135/90201

        此接口和 `WeChatDepartment.get_users` 是同一个接口，区别为 simple 的默认值不同。
        """
        url = 'user/simplelist' if simple else 'user/list'
        res = await self._get(
            url,
            params={
                'department_id': department_id,
                'fetch_child': 1 if fetch_child else 0,
                'status': status
            }
        )
        return res['userlist']

    async def convert_to_openid(self, user_id, agent_id=None):
        """
        user_id 转成 openid

        https://work.weixin.qq.com/api/doc#90000/90135/90202

        :param user_id: 企业微信内的成员 ID
        :param agent_id: 可选，需要发送红包的应用ID，若只是使用微信支付和企业转账，则无需该参数
        :return: 返回的 JSON 数据包
        """
        data = optionaldict(
            userid=user_id,
            agentid=agent_id
        )
        return await self._post('user/convert_to_openid', data=data)

    async def convert_to_user_id(self, openid):
        """
        openid 转成 user_id

        https://work.weixin.qq.com/api/doc#90000/90135/90202

        :param openid: 在使用微信支付、微信红包和企业转账之后，返回结果的openid
        :return: 该 openid 在企业微信中对应的成员 user_id
        """
        res = await self._post('user/convert_to_userid', data={'openid': openid})
        return res['userid']

    async def verify(self, user_id):
        """
        二次验证

        https://work.weixin.qq.com/api/doc#90000/90135/90203

        :param user_id: 成员UserID。对应管理端的帐号
        """
        return await self._get(
            'user/authsucc',
            params={
                'userid': user_id
            }
        )

    async def get_info(self, agent_id, code):
        return await self._get(
            'user/getuserinfo',
            params={
                'agentid': agent_id,
                'code': code
            }
        )
