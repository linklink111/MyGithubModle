# github数据库设计

## 整体组成部分分析

假设该网络爬虫爬取github.org数据，首先考虑有哪些数据可以爬取：

- 用户信息，虽然作为普通用户，我们不能爬取其他用户的信息，但是有时开发人员与研究人员需要用户信息作为数据；
- 仓库信息，仓库信息可以再用户主页获取，也可以在搜索页面获取，但是无论通过什么渠道获取，都是同样的schema
- 仓库文件版本迭代

## 细节考虑与分析

### 仓库设计分析

考虑一个仓库中包含的数据：

- 代码  Text
- 仓库所有者，可以以外键的形式
- 仓库贡献者，可以使用外键
- 语言  varchar
- 分支 int
- 标签  varchar

### 仓库文件版本迭代与分支管理的解决方案

这是一个困难的问题，我们在进行了一些思考后，为了防止我们自身的思考过于局限，我们在网上搜索了非常切合github本身实现办法的方法

#### 我们的想法

- 仓库的每一个版本都独立存储为一个实体
- 只存储仓库的第一个版本，随后每次有更新就只存储更新的内容

#### 在Quora中得到的优化解

> 原回答：https://www.quora.com/In-what-way-is-Githubs-database-structured-so-that-users-can-always-get-previous-versions-of-their-code-Whats-the-schema

对于该回答的总结：

- 每一个commit的版本有一个哈希值
- commit记录了这个版本中所有object，其中：
  - 如果这个版本中的object与之前的版本不同，则它具有一个新的object并且它是一个新的object
  - 另外一类object，它们没有被修改，那么它们的哈希值和实体都还是原来的
  - 每个commit有一个parent，用于找到那个没被修改的object，或者进行被修改object的恢复

### 用户设计分析



- 注意到用户是通过邮箱登录的，因此可以吧邮箱作为主键

遇到的问题：

- star有一个数量，同时有一个列表，following和follower也一样，可以只针对用户定义相应的变量，例如：只记录每一个用户收藏了那些仓库，在需要某一个仓库的收藏量的数据时，从所有的数据中搜索收藏了该仓库的用户。（此处本来认为需要用空间换取时间的，但是参考了下面好友列表的设计例子后，发现从好友关系表中查找（计算）出好友列表这样庞大的计算量都不需要以空间换取时间，所以此处具有更小的查找量也不需要用空间换取时间）
- 继续上面的问题：列表和数量，列表可以计算出数量，因此在有列表的情况下数量其实是冗余的
- 继续上面的问题：一个用户可以有多个列表，这样似乎会发生表的嵌套，不符合最基本的1NF，上网搜索到了类似情况的解决方案，类似于好友列表，

​    从爬虫的角度思考好友列表的问题，爬虫从github爬下来的一定是一个列表，但是github后台真正存储好友的可能是一个混杂的关系表，而且可能是分布式存储

## Schema 设计

schema 表（见 schema.pdf）

ER图

## 爬虫设计

py

## 前端设计

## 后端增强



在对github背后的数据库进行了逆向分析之后，我们在知乎和github上了解到了一些github使用的提高数据库效率的办法（是一些开源项目）：

- bcrypt-ruby：bcrypt- Ruby是OpenBSD bcrypt()密码散列算法的Ruby绑定，允许您轻松存储用户密码的安全散列。
- ZeroClipboard：ZeroClipboard库提供了一种使用不可见的Adobe Flash影片和JavaScript接口将文本复制到剪贴板的简单方法。
- Resque：企业所使用的!Resque是一个redisr支持的Ruby库，用于控制后台作业。



## 参考：

https://ghtorrent.org/relational.html(github schema)

https://www.quora.com/What-is-GitHubs-database-schema(github高效运转)

https://zhuanlan.zhihu.com/p/165940906（sql编写规范）