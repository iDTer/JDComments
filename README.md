# JDComments
### 环境配置

Python 3.6

PyCharm

### 主要思想

爬取京东商城商品的评论，这里我采用了两种方法去爬取：1、通过JSON，这个方法是首先想到的，但是实施起来却让我琢磨了很久，因为直接调用产品评论的JSON数据时是没有返回的，经好朋友提醒，在使用Burpsuit调试后发现，需要加上response表项才会有回显，应该是京东的反爬取措施，总之，使用response后就work了。2、使用selenium包，模拟自动爬取，使用webdriver里的PhantomJS来模拟点击换页，通过XPath或者CSS_SELECTOR来定位评论元素。

### 方法一

主要就是请求JSON数据时要加response表项



### 方法二

这里需要注意几个地方：

1. 京东会有侧栏的悬浮框，经过测试默认是展开的，所以有时候模拟点击时会无法选中下一页
2. 如果CSS_SELECTOR无法获取元素，就试试XPath，都是傻瓜式的，很方便

ps: 源码在JDProductsComments文件夹下



### 截图

存入MongoDB数据库：
![png](http://cdn.peckerwood.top/2019-08-15_091732.png)

存入CSV：

![png](http://cdn.peckerwood.top/2019-08-15_091751.png)