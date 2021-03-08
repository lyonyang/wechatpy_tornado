# wechatpy_tornado

异步wechatpy_tornado支持

wechatpy version: 1.8.14

# 如果同样对异步 wechatpy 有需求的, 可以添加我的QQ: 547903993, 一起交流

因为工作以及时间原因, 暂时还并没有进行试错, 快速的处理方案是直接在 `RequestHandler` 中定义 `executor` , 使用同步方式

通过 `concurrent` 提供线程池支持

如下: 

```python

import tornado.process
import concurrent.futures


class RequestHandler(tornado.web.RequestHandler):
    __doc__ = ""

    def __init__(self, application, request, **kwargs):
        super(RequestHandler, self).__init__(application, request, **kwargs)

        if not hasattr(self, "executor"):
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=(tornado.process.cpu_count() * 5)
            )  # type: concurrent.futures.Executor

```

使用方式: 

```python
from tornado.concurrent import run_on_executor

class Demo(RequestHandler):
    async def post(self):
        ioloop.add_callback(self.block_function)
        # return response

    @run_on_executor
    def block_function(self):
        pass
```

关于 add_callback, 或者是直接调用, 都无关紧要

**这里也可以考虑提升为类属性**
