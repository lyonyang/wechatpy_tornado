from __future__ import absolute_import, unicode_literals

import logging

from wechatpy_tornado.client import WeChatClient  # NOQA
from wechatpy_tornado.component import ComponentOAuth, WeChatComponent  # NOQA
from wechatpy_tornado.exceptions import WeChatClientException, WeChatException, WeChatOAuthException, WeChatPayException  # NOQA
from wechatpy_tornado.oauth import WeChatOAuth  # NOQA
from wechatpy_tornado.parser import parse_message  # NOQA
from wechatpy_tornado.pay import WeChatPay  # NOQA
from wechatpy_tornado.replies import create_reply  # NOQA

__version__ = '1.8.14'
__author__ = 'messense'

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
