pager
=====

pager for flask

### 使用方法

将 pager.py 放到相应目录

```
from .pager import Pager

pager = Pager(count)


```

详细看 示例代码

* 查看是否有上一页  pager.has_prev
* 查看上一页        pager.prev_page
* 查看是否有下一页  pager.next_prev
* 查看下一页        pager.next_page
* 查看当前页码      pager.current_page
* 查看总页数        pager.pages
