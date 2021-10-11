# ghtorrent:从Github API镜像和索引数据  

一个库和脚本集合，用于从Github API检索数据，并提取SQL数据库中的元数据，以模块化和可伸缩的方式。 这些脚本作为Gem (ghtorrent)分发，但是也可以通过签出这个存储库来运行它们。  

GHTorrent可以用于多种目的，如:  

- 镜像Github API事件流，并跟随从事件到实际数据的链接，逐步构建一个Github索引  

- 为特定存储库创建可查询的元数据数据库  

- 为一个或多个存储库构建一个数据源，用于提取流程分析(参见示例)  

## 组件

APIClient:知道如何查询Github API(单个实体和页面)，并尊重API请求限制。可以配置为覆盖默认IP地址，在多主机的情况下。

检索器（Retriver）:知道如何按名称检索特定的Github实体(用户、存储库、监视者)。使用可选的持久化程序以避免检索未更改的数据。

Persister:一个键/值存储，可以由一个真正的键/值存储支持，存储Github JSON回复并在请求时查询它们。支持键/值存储必须支持对存储的JSON对象的任意查询。

GHTorrent:知道如何从检索器检索的数据中提取信息，以便使用元数据更新SQL数据库(见模式)。

## 组件配置

Persister和GHTorrent组件有可配置的后端:

Persister:使用MongoDB &gt;3.0 (mongo驱动)或no persister (noop驱动)

GHTorrent: GHTorrent测试主要使用MySQL和SQLite，但理论上可以使用任何SQL数据库与Sequel兼容。你的里程可能会有所不同。

对于分布式镜像，您还需要RabbitMQ &gt;= 3.3

## 用法

镜像事件流并捕获所有数据:

- 镜像事件.rb定期轮询Github的事件队列(https://api.github.com/events)，将所有新事件存储在配置的瘟疫中，并发布到RabbitMQ的Github交换。

- ght-data_retrieval.Rb创建队列，将发布的事件路由到处理器函数。这些函数使用适当的Github API调用来检索链接的内容，提取元数据(用于数据库存储)，并将检索到的数据存储在persister中的适当集合中，以避免重复的API调用。SQL数据库中的数据包含指向持久器中的“原始”数据的指针(ext_ref_id字段)。

  为存储库或用户检索数据:

  ight -retrieve-repo检索特定存储库的所有数据。

  ghbt -load将选择的事件从persister加载到队列中，以便

  ght-data-retrieval脚本重新处理它们。您可以在下载页面中找到项目中收集的所有数据。

  有两组数据:

  原始事件:Github的事件流。这些是镜像操作的根。ght数据检索爬虫从一个事件开始，并深入到兔子洞。

  SQL dump + Linked data:从SQL数据库和相应的MongoDB实体转储数据。