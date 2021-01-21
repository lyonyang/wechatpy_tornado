# -*- coding: utf-8 -*-
"""
    wechatpy_tornado._compat
    ~~~~~~~~~~~~~~~~~

    This module makes it easy for wechatpy_tornado to run on both Python 2 and 3.

    :copyright: (c) 2014 by messense.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import absolute_import, unicode_literals
import sys  # NOQA
import six  # NOQA
import warnings

warnings.warn("Module `wechatpy_tornado._compat` is deprecated, will be removed in 2.0"
              "use `wechatpy_tornado.utils` instead",
              DeprecationWarning, stacklevel=2)

from wechatpy_tornado.utils import get_querystring  # NOQA
from wechatpy_tornado.utils import json  # NOQA
