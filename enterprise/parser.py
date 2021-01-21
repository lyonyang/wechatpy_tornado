# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import xmltodict

from wechatpy_tornado.enterprise.events import EVENT_TYPES
from wechatpy_tornado.enterprise.messages import MESSAGE_TYPES
from wechatpy_tornado.messages import UnknownMessage
from wechatpy_tornado.utils import to_text


def parse_message(xml):
    if not xml:
        return
    message = xmltodict.parse(to_text(xml))['xml']
    message_type = message['MsgType'].lower()
    if message_type == 'event':
        event_type = message['Event'].lower()
        message_class = EVENT_TYPES.get(event_type, UnknownMessage)
    else:
        message_class = MESSAGE_TYPES.get(message_type, UnknownMessage)
    return message_class(message)
