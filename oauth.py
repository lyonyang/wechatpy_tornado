# -*- coding: utf-8 -*-
"""
    wechatpy_tornado.oauth
    ~~~~~~~~~~~~~~~

    This module provides OAuth2 library for WeChat

    :copyright: (c) 2014 by messense.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import absolute_import, unicode_literals

from urllib.parse import quote

from wechatpy_tornado.exceptions import WeChatOAuthException
from wechatpy_tornado.utils import json
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from urllib.parse import urlencode
from wechatpy_tornado.utils import to_binary


class WeChatOAuth(object):
    """ 微信公众平台 OAuth 网页授权

    详情请参考
    https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1419316505
    """

    API_BASE_URL = 'https://api.weixin.qq.com/'
    OAUTH_BASE_URL = 'https://open.weixin.qq.com/connect/'

    def __init__(self, app_id, secret, redirect_uri, scope='snsapi_base', state=''):
        """

        :param app_id: 微信公众号 app_id
        :param secret: 微信公众号 secret
        :param redirect_uri: OAuth2 redirect URI
        :param scope: 可选，微信公众号 OAuth2 scope，默认为 ``snsapi_base``
        :param state: 可选，微信公众号 OAuth2 state
        """
        self.app_id = app_id
        self.secret = secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.state = state
        self._http = AsyncHTTPClient()

    async def _request(self, method, url_or_endpoint, **kwargs):
        if not url_or_endpoint.startswith(('http://', 'https://')):
            url = '{base}{endpoint}'.format(
                base=self.API_BASE_URL,
                endpoint=url_or_endpoint
            )
        else:
            url = url_or_endpoint

        params = kwargs.pop('params', {})
        params = urlencode(dict((k, to_binary(v)) for k, v in params.items()))
        url = '{0}?{1}'.format(url, params)

        data = kwargs.pop('data', {})
        if isinstance(data, dict):
            body = json.dumps(data, ensure_ascii=False)
            body = body.encode('utf-8')
            kwargs['body'] = body

        req = HTTPRequest(url, method=method, **kwargs)
        res = await self._http.fetch(req)
        if res.error is not None:
            raise WeChatOAuthException(
                errcode=None,
                errmsg=None,
                client=self,
                request=req,
                response=res
            )
        result = json.loads(res.body.decode('utf-8', 'ignore'), strict=False)

        if 'errcode' in result and result['errcode'] != 0:
            errcode = result['errcode']
            errmsg = result['errmsg']
            raise WeChatOAuthException(
                errcode,
                errmsg,
                client=self,
                request=res.request,
                response=res
            )

        return result

    async def _get(self, url, **kwargs):
        return await self._request(
            method='GET',
            url_or_endpoint=url,
            **kwargs
        )

    @property
    def authorize_url(self):
        """获取授权跳转地址

        :return: URL 地址
        """
        redirect_uri = quote(self.redirect_uri, safe=b'')
        url_list = [
            self.OAUTH_BASE_URL,
            'oauth2/authorize?appid=',
            self.app_id,
            '&redirect_uri=',
            redirect_uri,
            '&response_type=code&scope=',
            self.scope
        ]
        if self.state:
            url_list.extend(['&state=', self.state])
        url_list.append('#wechat_redirect')
        return ''.join(url_list)

    @property
    def qrconnect_url(self):
        """生成扫码登录地址

        :return: URL 地址
        """
        redirect_uri = quote(self.redirect_uri, safe=b'')
        url_list = [
            self.OAUTH_BASE_URL,
            'qrconnect?appid=',
            self.app_id,
            '&redirect_uri=',
            redirect_uri,
            '&response_type=code&scope=',
            'snsapi_login'  # scope
        ]
        if self.state:
            url_list.extend(['&state=', self.state])
        url_list.append('#wechat_redirect')
        return ''.join(url_list)

    async def fetch_access_token(self, code):
        """获取 access_token

        :param code: 授权完成跳转回来后 URL 中的 code 参数
        :return: JSON 数据包
        """
        res = await self._get(
            'sns/oauth2/access_token',
            params={
                'appid': self.app_id,
                'secret': self.secret,
                'code': code,
                'grant_type': 'authorization_code'
            }
        )
        self.access_token = res['access_token']
        self.open_id = res['openid']
        self.refresh_token = res['refresh_token']
        self.expires_in = res['expires_in']
        return res

    async def refresh_access_token(self, refresh_token):
        """刷新 access token

        :param refresh_token: OAuth2 refresh token
        :return: JSON 数据包
        """
        res = await self._get(
            'sns/oauth2/refresh_token',
            params={
                'appid': self.app_id,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        )
        self.access_token = res['access_token']
        self.open_id = res['openid']
        self.refresh_token = res['refresh_token']
        self.expires_in = res['expires_in']
        return res

    async def get_user_info(self, openid=None, access_token=None, lang='zh_CN'):
        """获取用户信息

        :param openid: 可选，微信 openid，默认获取当前授权用户信息
        :param access_token: 可选，access_token，默认使用当前授权用户的 access_token
        :param lang: 可选，语言偏好, 默认为 ``zh_CN``
        :return: JSON 数据包
        """
        openid = openid or self.open_id
        access_token = access_token or await self.access_token()
        return await self._get(
            'sns/userinfo',
            params={
                'access_token': access_token,
                'openid': openid,
                'lang': lang
            }
        )

    async def check_access_token(self, openid=None, access_token=None):
        """检查 access_token 有效性

        :param openid: 可选，微信 openid，默认获取当前授权用户信息
        :param access_token: 可选，access_token，默认使用当前授权用户的 access_token
        :return: 有效返回 True，否则 False
        """
        openid = openid or self.open_id
        access_token = access_token or await self.access_token()
        res = await self._get(
            'sns/auth',
            params={
                'access_token': access_token,
                'openid': openid
            }
        )
        if res['errcode'] == 0:
            return True
        return False
