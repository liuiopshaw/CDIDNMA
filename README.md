# CDIDNMA

面向 CDI 抗菌电极研究的多 Agent 系统项目。目标是自主完成跨材料家族的候选生成、评估排序、性能预测与机理探究，同时支持单独调用六类子 Agent。

## 当前状态

项目已完成初步设计与开发交接计划，包含 1500 条文献元数据、文献采集脚本及模型和评分配置草案。多 Agent 应用尚未实现，GPU 部署与真实模型运行尚未验证。

首版目标环境为 **Windows + WSL2、RTX 5090**，同时使用远程 API 和本地模型。配置中的模型角色将在开发阶段按实施计划迁移。

## 开发入口

接手开发时按以下顺序阅读：

1. [实施与 Coding Agent 交接计划](docs/IMPLEMENTATION_PLAN.md)：技术默认值、目录结构、接口和代码示例、M0–M6 开发步骤、验收标准及可复制的任务提示。
2. [设计方案](docs/DESIGN_PLAN.md)：研究目标、六类 Agent、材料场景与系统边界。
3. [评分标准](docs/rubric.md)：五维评分、证据要求及可调整排名。
4. [讨论纪要](docs/discussion-summary.md)：已确认的用户需求与暂缓事项。

首版的技术选型、模型映射和评分聚合以实施计划为准。暂缓的深入讨论不作为开发前置条件。真实运行、模拟测试与科学结果验证分别记录。

## 仓库内容

```text
config/                     模型与评分配置草案
data/
  all_titles_dois.csv        1500 条文献元数据
  cdi_core/                 CDI 核心层：262 条
  electrocatalysis_prior/    电催化先验层：905 条
  photocatalysis_inspiration/ 光催化灵感层：333 条
  increment_v2_titles_dois.csv 扩展查询溯源
docs/                       设计、实施计划、评分规则与讨论记录
scripts/collect_literature.py 已有 OpenAlex 文献采集脚本
```

文献清单是标题和 DOI 等元数据，不代表已取得全文或完成定量证据提取。用户的真实实验数据尚未导入。

## 在目标机器接手

在 WSL2 终端克隆仓库：

```bash
git clone https://github.com/liuiopshaw/CDIDNMA.git
cd CDIDNMA
```

将 `docs/IMPLEMENTATION_PLAN.md` 交给 coding agent，从 M0 按顺序执行。业务依赖文件和启动命令属于待实现内容，目前没有可直接启动的完整应用。

API 密钥在目标机器通过环境变量或不入库的 `.env` 配置。全文、原始实验数据、模型权重及运行输出默认不纳入 Git；跨机器使用时单独提供相应文件。

已有采集脚本会改写文献 CSV。接手开发时先导入现有清单，不需要通过重跑脚本准备项目。
