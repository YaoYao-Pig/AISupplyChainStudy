基于The ML Supply Chain in the Era of Software 2.0: Lessons Learned from Hugging Face论文提供的数据集
论文的数据集将该研究分析了 760,460 个模型和 175,000 个数据集，重点关注文档、供应链结构和许可实践。软件 2.0 指的是以 ML 模型为核心的软件开发范式

## 数据处理

我们基于上述数据集的基础上，编写了一套将上述数据导入Neo4j的代码

start：

```python
python -u "filename"
```

导入分为datasets和models两部分，都是多线程导入。值得注意的是，为了构建模型之间的依赖关系，模型相关的数据导入了两次。第一次数据导入，第二次导入关系

SQL文件夹下存储了一些sql查询语句，包括了一些基本的数据分析，之后会继续更新

## 文档挑战
只有 7,258 个模型卡片（0.95%）因 API 不可访问而需要网页抓取，通常受限于条款和条件。
只有 37.8% 的模型（287,143 个）和 27.6% 的数据集（48,356 个）声明了机器可读的许可。
一个例子是 OpenAI 的 clip-vit-large-patch14-336 模型，下载量达 5,827,027 次，但其模型卡片不完整。
这些问题可能导致合规性和安全性的挑战，尤其是在自动化分析和 ML/AIBOM（机器学习/人工智能物料清单）生成时。

## 供应链结构
供应链结构的分析揭示了其复杂性：

构建了 53,151 个血统链，平均长度为 6.2 个模型，最长链为 40 个模型。
只有 15.4% 的模型（117,245 个）声明了至少一个基础模型，其中 111,568 个声明了一个基础模型。
9.9% 的模型（75,516 个）声明了至少一个数据集，其中 64,343 个声明了一个数据集。
这种低透明度可能影响模型可追溯性和可信度。
## 许可景观
许可问题尤为突出：

62.2% 的模型和 72.4% 的数据集缺乏机器可读的许可。
模型中最常见的许可是 Apache-2.0（41.6%，119,449 个）、MIT（17.8%，51,184 个）和 OpenRAIL（10.5%，30,095 个）。
存在 66,460 个（24%）父子模型许可差异，其中 54.8% 无重叠（例如 cc-by-nc-4.0 到 Apache-2.0 的 11,001 个案例）。
这些差异可能导致法律和合规性风险。

## 统计数据表
以下是关键统计数据总结：

| 方面             | 详情                                                         | 数字                                        |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------- |
| 分析的模型总数   | 总计                                                         | 760,460                                     |
| 分析的数据集总数 | 总计                                                         | 175,000                                     |
| 文档访问问题     | 因 API 问题需网页抓取的模型卡片                              | 7,258（0.95%）                              |
| 许可声明         | 具有机器可读许可的模型                                       | 37.8%（287,143）                            |
| 许可声明         | 具有机器可读许可的数据集                                     | 27.6%（48,356）                             |
| 基础模型声明     | 声明至少一个基础模型的模型                                   | 15.4%（117,245）                            |
| 数据集声明       | 声明至少一个数据集的模型                                     | 9.9%（75,516）                              |
| 血统链总数       | 分析的总链数                                                 | 53,151                                      |
| 平均链长         | 6.2 个模型                                                   |                                             |
| 最长链           | 从 cohereforai/c4ai-command-r-v01 到 Citaman/command-r-1-layer | 40 个模型                                   |
| 父子许可差异     | 总实例，無重疊示例                                           | 66,460，cc-by-nc-4.0 → Apache-2.0（11,001） |









