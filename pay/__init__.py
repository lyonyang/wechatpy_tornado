# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import inspect
import logging

import ssl
import xmltodict
from xml.parsers.expat import ExpatError
from optionaldict import optionaldict

from wechatpy_tornado.crypto import WeChatRefundCrypto
from wechatpy_tornado.utils import random_string
from wechatpy_tornado.exceptions import WeChatPayException, InvalidSignatureException, RequestException
from wechatpy_tornado.pay.utils import (
    calculate_signature, calculate_signature_hmac, _check_signature, dict_to_xml
)
from wechatpy_tornado.pay.base import BaseWeChatPayAPI
from wechatpy_tornado.pay import api
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from urllib.parse import urlencode
from wechatpy_tornado.utils import to_binary

logger = logging.getLogger(__name__)


def _is_api_endpoint(obj):
    return isinstance(obj, BaseWeChatPayAPI)


class WeChatPay(object):
    """
    微信支付接口

    :param appid: 微信公众号 appid
    :param sub_appid: 当前调起支付的小程序APPID
    :param api_key: 商户 key,不要在这里使用小程序的密钥
    :param mch_id: 商户号
    :param sub_mch_id: 可选，子商户号，受理模式下必填
    :param mch_cert: 必填，商户证书路径
    :param mch_key: 必填，商户证书私钥路径
    :param timeout: 可选，请求超时时间，单位秒，默认无超时设置
    :param sandbox: 可选，是否使用测试环境，默认为 False
    """

    redpack = api.WeChatRedpack()
    """红包接口"""
    transfer = api.WeChatTransfer()
    """企业付款接口"""
    coupon = api.WeChatCoupon()
    """代金券接口"""
    order = api.WeChatOrder()
    """订单接口"""
    refund = api.WeChatRefund()
    """退款接口"""
    micropay = api.WeChatMicroPay()
    """刷卡支付接口"""
    tools = api.WeChatTools()
    """工具类接口"""
    jsapi = api.WeChatJSAPI()
    """公众号网页 JS 支付接口"""
    withhold = api.WeChatWithhold()
    """代扣接口"""

    API_BASE_URL = 'https://api.mch.weixin.qq.com/'

    def __new__(cls, *args, **kwargs):
        self = super(WeChatPay, cls).__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, _api in api_endpoints:
            api_cls = type(_api)
            _api = api_cls(self)
            setattr(self, name, _api)
        return self

    def __init__(self, appid, api_key, mch_id, sub_mch_id=None,
                 mch_cert=None, mch_key=None, timeout=None, sandbox=False, sub_appid=None):
        self.appid = appid
        self.sub_appid = sub_appid
        self.api_key = api_key
        self.mch_id = mch_id
        self.sub_mch_id = sub_mch_id
        self.mch_cert = mch_cert
        self.mch_key = mch_key
        self.timeout = timeout
        self.sandbox = sandbox
        self._sandbox_api_key = None
        self._http = AsyncHTTPClient()

    async def _fetch_sandbox_api_key(self):
        nonce_str = random_string(32)
        sign = calculate_signature({'mch_id': self.mch_id, 'nonce_str': nonce_str}, self.api_key)
        payload = dict_to_xml({
            'mch_id': self.mch_id,
            'nonce_str': nonce_str,
        }, sign=sign)
        headers = {'Content-Type': 'text/xml'}
        api_url = '{base}sandboxnew/pay/getsignkey'.format(base=self.API_BASE_URL)
        request = HTTPRequest(api_url, method='POST', body=payload, headers=headers)
        response = await self._http.fetch(request)
        return xmltodict.parse(response.body.decode('utf-8'))['xml'].get('sandbox_signkey')

    async def _request(self, method, url_or_endpoint, **kwargs):
        if not url_or_endpoint.startswith(('http://', 'https://')):
            api_base_url = kwargs.pop('api_base_url', self.API_BASE_URL)
            if self.sandbox:
                api_base_url = '{url}sandboxnew/'.format(url=api_base_url)
            url = '{base}{endpoint}'.format(
                base=api_base_url,
                endpoint=url_or_endpoint
            )
        else:
            url = url_or_endpoint

        params = kwargs.pop('params', {})
        params = urlencode(dict((k, to_binary(v)) for k, v in params.items()))
        url = '{0}?{1}'.format(url, params)

        data = kwargs.pop('data', {})

        if isinstance(data, dict):
            if 'mchid' not in data:
                data.setdefault('mch_id', self.mch_id)
            data.setdefault('sub_mch_id', self.sub_mch_id)
            data.setdefault('nonce_str', random_string(32))
            data = optionaldict(data)

            if data.get('sign_type', 'MD5') == 'HMAC-SHA256':
                sign = calculate_signature_hmac(data, await self.sandbox_api_key() if self.sandbox else self.api_key)
            else:
                sign = calculate_signature(data, await self.sandbox_api_key() if self.sandbox else self.api_key)
            body = dict_to_xml(data, sign)
            body = body.encode('utf-8')
            kwargs['body'] = body

        # 商户证书
        if self.mch_cert and self.mch_key:
            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain(self.mch_cert, self.mch_key)
            kwargs['ssl_options'] = ssl_ctx

        kwargs['request_timeout'] = kwargs.pop('timeout') if 'timeout' in kwargs else self.timeout
        logger.debug('Request to WeChat API: %s %s\n%s', method, url, kwargs)

        req = HTTPRequest(
            url,
            method=method,
            **kwargs
        )

        res = await self._http.fetch(req)
        if res.error is not None:
            raise WeChatPayException(
                return_code=None,
                client=self,
                request=req,
                response=res
            )

        return self._handle_result(res)

    def _handle_result(self, res):
        xml = res.body.decode('utf-8')
        logger.debug('Response from WeChat API \n %s', xml)
        try:
            data = xmltodict.parse(xml)['xml']
        except (xmltodict.ParsingInterrupted, ExpatError):
            logger.debug('WeChat payment result xml parsing error', exc_info=True)
            return xml

        return_code = data['return_code']
        return_msg = data.get('return_msg')
        result_code = data.get('result_code')
        errcode = data.get('err_code')
        errmsg = data.get('err_code_des')
        if return_code != 'SUCCESS' or result_code != 'SUCCESS':
            # 返回状态码不为成功
            raise WeChatPayException(
                return_code,
                result_code,
                return_msg,
                errcode,
                errmsg,
                client=self,
                request=res.request,
                response=res
            )
        return data

    async def get(self, url, **kwargs):
        return await self._request(
            method='GET',
            url_or_endpoint=url,
            **kwargs
        )

    async def post(self, url, **kwargs):
        return await self._request(
            method='POST',
            url_or_endpoint=url,
            **kwargs
        )

    async def check_signature(self, params):
        return _check_signature(params, self.api_key if not self.sandbox else await self.sandbox_api_key())

    @classmethod
    def get_payment_data(cls, xml):
        """
        解析微信支付结果通知，获得appid, mch_id, out_trade_no, transaction_id
        如果你需要进一步判断，请先用appid, mch_id来生成WeChatPay,
        然后用`wechatpay.parse_payment_result(xml)`来校验支付结果

        使用示例::

            from wechatpy_tornado.pay import WeChatPay
            # 假设你已经获取了微信服务器推送的请求中的xml数据并存入xml变量
            data = WeChatPay.get_payment_appid(xml)
            {
                "appid": "公众号或者小程序的id",
                "mch_id": "商户id",
            }

        """
        try:
            data = xmltodict.parse(xml)
        except (xmltodict.ParsingInterrupted, ExpatError):
            raise ValueError("invalid xml")
        if not data or 'xml' not in data:
            raise ValueError("invalid xml")
        data = data["xml"]
        return {
            "appid": data["appid"],
            "mch_id": data["mch_id"],
            "out_trade_no": data["out_trade_no"],
            "transaction_id": data["transaction_id"],
        }

    async def parse_payment_result(self, xml):
        """解析微信支付结果通知"""
        try:
            data = xmltodict.parse(xml)
        except (xmltodict.ParsingInterrupted, ExpatError):
            raise InvalidSignatureException()

        if not data or 'xml' not in data:
            raise InvalidSignatureException()

        data = data['xml']
        sign = data.pop('sign', None)
        real_sign = calculate_signature(data, self.api_key if not self.sandbox else await self.sandbox_api_key())
        if sign != real_sign:
            raise InvalidSignatureException()

        for key in ('total_fee', 'settlement_total_fee', 'cash_fee', 'coupon_fee', 'coupon_count'):
            if key in data:
                data[key] = int(data[key])
        data['sign'] = sign
        return data

    async def parse_refund_notify_result(self, xml):
        """解析微信退款结果通知"""
        refund_crypto = WeChatRefundCrypto(self.api_key if not self.sandbox else await self.sandbox_api_key())
        data = refund_crypto.decrypt_message(xml, self.appid, self.mch_id)
        for key in ('total_fee', 'settlement_total_fee', 'refund_fee', 'settlement_refund_fee'):
            if key in data:
                data[key] = int(data[key])
        return data

    async def sandbox_api_key(self):

        if self.sandbox and self._sandbox_api_key is None:
            self._sandbox_api_key = await self._fetch_sandbox_api_key()

        return self._sandbox_api_key