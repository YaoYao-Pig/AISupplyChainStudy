# Ecosystem Graphs: The Social Footprint of Foundation Models



## 主要发现

Ecosystem Graphs 是一个知识图谱，记录了 262 个资产和 356 个依赖关系，涵盖数据集、模型和应用，并附有元数据如许可证和训练排放。识别了 The Pile 数据集、PaLM 模型和 ChatGPT API 等“枢纽”，这些资产在生态系统中具有高影响力。

### 详细报告

论文强调基础模型对社会的广泛影响，指出其生态系统缺乏透明性。Ecosystem Graphs 被提出作为一种解决方案，通过记录资产及其依赖关系和元数据，提供一个集中化的文档框架，旨在增强对基础模型社会影响的理解。

作者通过手动整理资产和依赖关系，构建了 Ecosystem Graphs。截至 2023 年 3 月 16 日，包含 262 个资产（64 个数据集、128 个模型、70 个应用）和 356 个依赖关系，并附有 3,850 条元数据记录，托管在 https://crfm.stanford.edu/ecosystem-graphs

#### 主要发现

- **Ecosystem Graphs 框架**：该框架链接资产（数据集、模型、应用）通过依赖关系，反映技术（如 Bing 依赖 GPT-4）和社会（如 Microsoft 依赖 OpenAI）关系，并补充元数据如许可证和训练排放。

## 关键统计数据

| 方面           | 数字  |
| -------------- | ----- |
| 分析的资产总数 | 262   |
| 数据集数量     | 64    |
| 模型数量       | 128   |
| 应用数量       | 70    |
| 组织数量       | 63    |
| 依赖关系总数   | 356   |
| 元数据条目总数 | 3,850 |

#### 具体案例

论文提供了 Stable Diffusion 的案例研究，展示了从内容创建到应用部署的生态系统：

1. 人们创建内容并上传至网络；
2. LAION 整理 LAION-5B 数据集；
3. LMU Munich 等机构训练 Stable Diffusion；
4. Stability AI 构建 Stable Diffusion Reimagine，并部署在 Clipdrop 上，允许用户生成图像变体。
    其他例子包括 The Pile 数据集（用于训练多个模型）和 ChatGPT API（加速行业部署）。