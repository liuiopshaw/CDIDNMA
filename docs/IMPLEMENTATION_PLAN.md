# CDI 多 Agent 系统：实施与 Coding Agent 交接计划（v1.0）

> 日期：2026-10-13。
> 交付对象：接手本项目的 coding agent。
> 本文件是待执行的实施计划。代码示例用于约束接口和编码方式，不表示系统已经实现。
> 用户最新决定：暂缓深入讨论预测协议、架构细节和研究方法细节，采用可修改的工程默认值直接推进开发。
> 部署环境已确认：Windows + WSL2，RTX 5090 机器；首版同时使用远程 API 和本地模型。

## 1. 接手说明与工作范围

先阅读本文件，再阅读 [DESIGN_PLAN.md](DESIGN_PLAN.md) 和 [rubric.md](rubric.md)。讨论背景见 [discussion-summary.md](discussion-summary.md)。当前用户指示优先；本文中的首版默认值用于解决旧文档的待定事项，不需要逐项重新征求确认。

当前源码目录位于 `/Users/liuiop/cdi-agent`。这是当前文件所在机器的路径，不是部署机器的固定路径。部署到 WSL2 后建议放在 `~/cdi-agent`，所有运行路径均通过项目根目录或配置解析。

本次交接要求完成一个真实可运行的应用。不要只交空接口、静态页面或模拟报告。开发可以使用离线测试数据，但必须区分测试结果、真实模型调用和真实实验数据。

### 1.1 用户已经确定的要求

1. 系统自主完成材料预测、评估、性能预测和机理探究。
2. 文献提取、知识归纳、材料预测、评估筛选、性能预测、机理探究六类子 agent 均可独立调用。
3. 跨纳米颗粒、纳米团簇、单原子家族比较；先导材料固定作为现有实验案例。
4. 排名支持调整权重和过滤条件，保留调整前后的分数和版本。先导材料不必第一，也不要求换材料重新实验。
5. 真正灭活与出水细菌去除为优先目标，分别输出和评价。ROS 任务内部优先量化，再分析对灭活的贡献，最后比较候选间能力。
6. 尽可能提供合理数值范围；缺少依据时输出未知或条件化判断，任务可以带未知项结束。
7. 初版同时接入远程模型与 RTX 5090 上的本地模型。专用模型微调后置。
8. 不要求用户人工标注文献或补齐大量实验细节。
9. 不包含实验设计、合成操作指导、实验执行或论文自动撰写。
10. 材料判断由 LLM 完成；代码负责流程、数据检查、算术与文件处理。不增加统计机器学习性能回归。

### 1.2 后续实施必须交付

- Python 可安装项目、依赖锁定、环境检查和启动说明。
- SQLite 工作区、文献与证据存储、运行记录和结果导出。
- 远程与本地模型的统一调用层，以及实际连通性检查。
- 六类可独立调用的 agent，以及自动完成主流程的编排器。
- 文献元数据导入、本地全文导入、基本在线检索与可用全文获取。
- 评分、可调整榜单、性能区间、机理档案和有限的缺口补充。
- 五类 Streamlit 页面，能够操作真实服务。
- 实验记录导入与结果对比、基础单 agent 对照入口。
- 有针对性的自动化测试、离线演示、混合模型实测报告和交接说明。

### 1.3 明确后置

精细区间校准、复杂贡献归因、自动重写全部研究方案、复杂状态机、复杂统计检验、系统性模块移除对照、全面数据库接入、本地微调、DFT、分布式部署、多用户账户及云发布均后置。

保留简单接口供以后扩展，不先搭建这些功能。旧文档中“待专题讨论”的条目不作为开发阻塞点。开发中只在缺少凭证、缺少目标机器访问或存在真正相互矛盾的用户要求时提问。

## 2. 已有资源与案例信息

### 2.1 保留已有文件

| 文件或目录 | 用途 |
|---|---|
| `data/all_titles_dois.csv` | 1500 条文献元数据，字段为 layer、title、doi |
| `data/cdi_core/titles_dois.csv` | 262 条核心层记录 |
| `data/electrocatalysis_prior/titles_dois.csv` | 905 条电催化先验记录 |
| `data/photocatalysis_inspiration/titles_dois.csv` | 333 条光催化灵感记录 |
| `data/increment_v2_titles_dois.csv` | 扩展查询及来源记录 |
| `scripts/collect_literature.py` | 已有 OpenAlex 采集脚本，可复用其中查询与分层逻辑 |
| `config/models.yaml`、`config/rubric.yaml` | 现有模型配置草案、五维评分默认值 |

元数据不等于全文或定量证据。导入时先保留这些原文件，不覆盖重采集。对 DOI 规范化去重，保留全部查询来源。

### 2.2 建立默认场景和指定材料记录

| 项目 | 已知值 |
|---|---|
| 材料 | 原始 ZIF-67 包裹铜纳米团簇 |
| 配体 | 4-巯基苯甲醛；用户简称 MBA，不能据缩写替换为其他化合物 |
| 导电载体 | 炭黑 |
| 阳极、阴极 | 目标复合材料为阳极，活性炭为阴极 |
| 水体系 | 含菌纯水相 |
| 外加电压 | 1.2 V；定义和参比未明确，保存原始表述 |
| 流动 | 单次流过，1 mL/min |
| 时间 | 装置运行 0–60 min，每隔 5 min 取出水样 |
| 目标菌 | 大肠杆菌，初始浓度 10⁶ CFU/mL |
| 外部条件 | 无光照、无曝气、无外加氧化剂 |
| 已有观测 | 出水菌数；H₂O₂、·OH 有标定的浓度、生成量、清除剂实验及对照；材料表征 |
| 未知 | pH、电导率、溶解氧、停留时间等未提供参数 |

已知数值用于 `config/scenarios/default.yaml`。未知值使用 `null`。实验具体数值尚未导入，不创建虚构的先导材料 ROS 或杀菌结果。

出水计数保存为出水 CFU 或 log 去除；运行时间与接触时间分开。现有计数不自动标记为整个体系的真实灭活。配体、ZIF-67 框架和炭黑载体分字段保存。

## 3. 首版技术方案

以下为可直接采用的工程默认值，不需要先做额外选型研究。

| 层 | 首版选择 |
|---|---|
| 语言与依赖 | Python 3.12、uv、`pyproject.toml`、`uv.lock` |
| 数据结构与配置 | Pydantic v2、PyYAML，敏感值来自环境变量 |
| 持久化 | 标准库 sqlite3，加本地 JSON/JSONL 文件 |
| 模型调用 | LiteLLM SDK 的统一网关，支持异步调用 |
| 本地推理 | WSL2 中独立环境运行 vLLM，提供兼容接口 |
| 在线工具 | httpx；OpenAlex 为首个检索适配器，Crossref 核验 DOI，Unpaywall 或已提供链接获取全文 |
| PDF 与表格 | pypdf 先处理有文本层的 PDF；pandas、openpyxl 导入 CSV/XLSX |
| 检索 | 首版用 SQLite 全文检索与元数据过滤；向量检索保留接口 |
| CLI 与 UI | Typer、Streamlit，共用业务服务 |
| 检查与测试 | Ruff、mypy、pytest；网络和真实模型测试单独标记 |

不引入多 agent 框架、消息队列或独立后端服务作为前提。编排先使用 Python 顺序流程，局部 API 调用可受限并发。

`pyproject.toml` 使用 `src` 包布局，并在 `[project.scripts]` 注册 `cdi = "cdi_agent.cli:app"` 命令入口。测试和检查依赖放入 `[dependency-groups]` 的 `dev` 项，与本文 `uv sync --group dev` 保持一致；提示词作为包资源安装，不能依赖当前工作目录读取。依赖分组参见 [uv 官方文档](https://docs.astral.sh/uv/concepts/projects/dependencies/)。

### 3.1 Windows + WSL2 部署

使用 WSL2 内的 Linux 运行应用和 vLLM，Windows 浏览器访问本地 Streamlit。先检查现有环境，不重复安装或重置已经可用的 WSL。

PowerShell 环境检查示例：

```powershell
wsl --status
wsl --list --verbose
```

仅在缺少环境时按 [Microsoft WSL 安装说明](https://learn.microsoft.com/en-us/windows/wsl/install) 安装 WSL2 和 Ubuntu。GPU 使用 Windows 侧 NVIDIA 驱动，WSL 内不要另装 Linux 显示驱动。参见 [NVIDIA WSL 指南](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)。

应用与推理服务分开虚拟环境，防止 GPU 依赖影响普通业务依赖。检查实际 GPU 型号、可用显存、驱动、PyTorch 和 CUDA 兼容性后锁定可工作的版本。原记录曾提及 24 GB 显存，以目标机 `nvidia-smi` 输出为准。安装依据 [vLLM GPU 文档](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/)。

本地首次接通默认采用未微调的 `Qwen/Qwen3-8B`，多个本地角色共用一个服务。这是降低首轮部署负担的工程默认值。原方案的量化 Qwen3-30B-A3B 保留为可替换配置，已有可用服务时直接复用，不要求降级。两者都不需要先做 LoRA。Qwen3 的部署方式和思考模式参见 [官方模型说明](https://huggingface.co/Qwen/Qwen3-8B)。

本地启动参数示例，须在目标机验证后写入启动脚本：

```bash
uv venv .venv-vllm --python 3.12
uv pip install --python .venv-vllm/bin/python vllm --torch-backend=auto

# 从环境或不入库的本地配置提供 LOCAL_LLM_API_KEY。
: "${LOCAL_LLM_API_KEY:?Set LOCAL_LLM_API_KEY before starting vLLM}"
.venv-vllm/bin/vllm serve Qwen/Qwen3-8B \
  --served-model-name cdi-local \
  --host 127.0.0.1 \
  --port 8000 \
  --api-key "$LOCAL_LLM_API_KEY" \
  --max-model-len 8192 \
  --max-num-seqs 1 \
  --gpu-memory-utilization 0.80
```

这些参数是启动起点，不是显存适配保证。模型名称、路径、上下文长度、显存占用比例均可配置。记录最终可用组合，导出推理环境的依赖清单。本地文本提取任务在适配器中关闭不需要的思考模式；参数按已安装版本检查。

vLLM 提供兼容的在线服务，业务侧只连接其端点，不在业务进程中加载权重。参见 [vLLM 服务文档](https://docs.vllm.ai/en/latest/serving/online_serving/)。

### 3.2 模型角色映射

| 角色名 | 初版路由 |
|---|---|
| `extractor` | 远程 DeepSeek Chat，主提取 |
| `local_extractor` | 本地 Qwen3，独立交叉提取；初版不是 LoRA 模型 |
| `extractor_third` | 远程 DeepSeek Chat，字段冲突复核 |
| `synthesizer`、`local_worker` | 本地 Qwen3，知识归纳及整理 |
| `designer`、`screener` | 远程 DeepSeek Chat，候选生成与评分 |
| `predictor`、`reasoner` | 远程 DeepSeek Reasoner，性能与机理；不支持的参数由网关处理 |

配置支持按角色替换模型。不能让“用户独立调用的 agent 名称”与“底层模型端点”耦合。

项目配置示例，属于本项目自行解析的格式，不是直接交给 LiteLLM 的代理配置：

```yaml
version: "0.2"
endpoints:
  remote_chat:
    model: deepseek/deepseek-chat
    api_key_env: DEEPSEEK_API_KEY
    location: remote
  remote_reasoner:
    model: deepseek/deepseek-reasoner
    api_key_env: DEEPSEEK_API_KEY
    location: remote
  local:
    model: openai/cdi-local
    api_base: http://127.0.0.1:8000/v1
    api_key_env: LOCAL_LLM_API_KEY
    location: local
roles:
  extractor: remote_chat
  local_extractor: local
  extractor_third: remote_chat
  synthesizer: local
  local_worker: local
  designer: remote_chat
  screener: remote_chat
  predictor: remote_reasoner
  reasoner: remote_reasoner
```

实现时备份和迁移已有 `models.yaml`，清楚说明差异。真实模型或角色不可用时返回明确错误，不能自动切换为假数据。有限降级必须留日志，正式混合模型验收要求本地和远程都真实参与。

### 3.3 简单运行默认值

```yaml
profile: live
pipeline:
  candidate_count: 15
  family_target_counts: {nanoparticle: 5, nanocluster: 5, single_atom: 5}
  deep_analysis_top_k: 5
  include_designated_candidate: true
  max_total_llm_calls: 400
  max_output_tokens: 2048
  role_max_output_tokens: {predictor: 8192, reasoner: 8192}
  max_chunk_tokens: 2500
  remote_concurrency: 3
  local_concurrency: 1
  remote_timeout_seconds: 90
  local_timeout_seconds: 180
  retries: 2
  json_repair_attempts: 1
knowledge_gap:
  max_rounds_per_candidate: 2
  max_queries_per_round: 3
  max_new_papers_per_run: 10
  recursive_expansion: false
observation:
  wait: false
```

这些数值是初版工程默认值，全部放配置，不代表已经校准。默认目标为新生成 15 个候选，再加入指定先导材料并按材料身份去重，因此总数最多为 16。候选数不足就报告实际数量，不复制变体凑数。完整导入 1500 条元数据不意味着一次处理全部全文。

每次发出请求前扣减全局调用预算，重试和格式修复也计入。成本记录来自响应 usage；美元估计只有在价格可确认时填写，否则保留未知。首版不依赖复杂费用预测。

输出上限按角色覆盖，并适配实际模型；reasoning tokens 是否计入由端点规则决定。构造请求时预留输出空间，不向本地 8192 上下文服务一次塞入全部证据。超出时先按任务相关性选择原文块，保留引用位置；截断输出作为解析失败处理。

## 4. 目标目录结构

```text
cdi-agent/
├── pyproject.toml
├── uv.lock
├── README.md
├── .env.example
├── .gitignore
├── config/
│   ├── models.yaml
│   ├── rubric.yaml
│   ├── runtime.yaml
│   └── scenarios/default.yaml
├── data/                         # 保留已有文献清单
│   ├── documents/                # 本地全文，默认不入库
│   └── experimental/             # 真实实验导入目录，默认不入库
├── src/cdi_agent/
│   ├── __init__.py
│   ├── cli.py
│   ├── settings.py
│   ├── schemas.py
│   ├── services.py
│   ├── workspace.py
│   ├── llm.py
│   ├── pipeline.py
│   ├── scoring.py
│   ├── reporting.py
│   ├── evaluation.py
│   ├── ui.py
│   ├── agents/
│   │   ├── base.py
│   │   ├── extractor.py
│   │   ├── synthesizer.py
│   │   ├── designer.py
│   │   ├── screener.py
│   │   ├── predictor.py
│   │   └── reasoner.py
│   ├── tools/
│   │   ├── literature.py
│   │   └── documents.py
│   └── prompts/                 # 六类角色与仲裁提示词，作为包资源分发
├── scripts/                     # 保留原采集脚本，新增必要启动脚本
├── deploy/                      # WSL2、vLLM 启动和已验证依赖组合
├── examples/                    # 六类输入模板，引用由初始化生成的记录
├── tests/
│   ├── fixtures/               # 明确标记为合成测试数据
│   ├── unit/
│   └── integration/
├── workspace/                   # 运行时 DB、缓存，不入库
├── runs/                        # 每次运行的报告与快照，不入库
└── docs/
    ├── DESIGN_PLAN.md
    ├── rubric.md
    ├── discussion-summary.md
    ├── IMPLEMENTATION_PLAN.md
    ├── DEPLOYMENT.md
    └── IMPLEMENTATION_STATUS.md
```

可按代码增长拆分文件，不预先创建大量空包。所有目录创建与初始化通过应用入口完成，读取配置时不隐式修改源数据。

## 5. 数据、接口与代码示例

### 5.1 首版只建立必要记录

| 记录 | 至少包含 |
|---|---|
| `Source` | id、doi、title、layer、document_path、content_hash、processing_scope |
| `Evidence` | id、source_id、sample_id、field、value、unit、conditions、locator、原文片段、quality_flags |
| `Candidate` | id、name、family、active_unit、ligand、framework、support、origin、evidence_ids |
| `Assessment` | candidate_id、每次分数、聚合分数、总分、verdict、rubric_version、evidence_ids |
| `Prediction` | candidate_id、metric、unit、区间或未知、时间含义、evidence_ids、assumptions |
| `Mechanism` | candidate_id、主要路径、反应位置、ROS、贡献描述、替代解释、evidence_ids |
| `KnowledgeGap` | id、candidate_id、问题、受影响阶段、检索次数、status |
| `Run` | id、mode、profile、配置快照、输入引用、阶段状态、开始结束时间、usage |
| `Validation` | run_id、预测版本、实验记录、对比结果、无法比较项 |

记录归属、run_id、profile、创建时间由业务服务写入，不接受 LLM 自行声明。来源与证据引用写入时检查。第一版可用 SQLite 普通列加 JSON 内容，后续再细化表结构。

### 5.2 接口示例：统一输入输出

以下代码演示接口，不是完整应用。角色专用输入仍需独立的 Pydantic 模型。

```python
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

AgentName = Literal[
    "extractor", "synthesizer", "designer",
    "screener", "predictor", "reasoner",
]


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    agent: AgentName
    objective: str = Field(min_length=1)
    input_ids: list[str] = Field(default_factory=list)
    scenario_id: str


class AgentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["completed", "partial", "failed"]
    record_ids: list[str] = Field(default_factory=list)
    gap_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error_code: str | None = None


class Agent(Protocol):
    async def run(self, request: AgentRequest) -> AgentResult:
        ...
```

`Agent` 是接口定义，允许省略实现；最终具体 agent 不得保留 `pass`、`NotImplementedError` 或固定字符串结果。通过构造函数注入 LLM 网关、工作区和工具服务，不在 agent 内创建全局客户端。

### 5.3 示例：预测区间的基本检查

```python
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PredictionInterval(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    metric: str
    status: Literal["estimated", "unknown"]
    unit: str | None = None
    lower: float | None = None
    upper: float | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def check_interval(self) -> Self:
        if self.status == "unknown":
            if self.lower is not None or self.upper is not None:
                raise ValueError("Unknown predictions must not have bounds")
            return self

        if self.lower is None or self.upper is None:
            raise ValueError("Estimated predictions need both bounds")
        if self.lower > self.upper:
            raise ValueError("Interval bounds are reversed")
        if not self.unit or not self.evidence_ids:
            raise ValueError("Estimated predictions need units and evidence")
        return self
```

这个检查只保证格式约束；证据 ID 是否存在、是否属于允许使用的输入范围、能否支持该项推断，仍由服务层检查。类比材料的证据可以使用，但必须标明外推关系，不能伪装成本候选的实测值。不同指标的值域放在指标定义中，不在通用类里假设所有指标非负。字段定义与模型解析参见 [Pydantic 模型文档](https://pydantic.dev/docs/validation/latest/concepts/models/)。

### 5.4 示例：加权总分由代码计算

```python
from collections.abc import Mapping
from math import isclose, isfinite


def weighted_total(
    scores: Mapping[str, float],
    weights: Mapping[str, float],
) -> float:
    if set(scores) != set(weights):
        raise ValueError("Score dimensions must match weight dimensions")
    if not weights or any(not isfinite(w) or w < 0 for w in weights.values()):
        raise ValueError("Weights must be finite and non-negative")
    if not isclose(sum(weights.values()), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("Weights must sum to one")
    if any(not isfinite(s) or not 0 <= s <= 10 for s in scores.values()):
        raise ValueError("Scores must be finite and within [0, 10]")
    return sum(scores[name] * weight for name, weight in weights.items())
```

比较阈值时使用未四舍五入的结果，展示时才格式化。缺失维度先返回 partial/hold，不作为零分传给函数。单纯修改权重不调用 LLM。

首版评分采用简单明确的执行约定：新颖性、机理可行性、合成可行性三类前置判断各一次，综合评分默认五次；逐维度取中位数再计算总分；标准差按各次总分的总体标准差计算。有限重试后有效评分次数不足配置要求（默认五次）时保留已有结果并 hold，不据少量调用直接判 pass。保留模型自报裁决用于审计，最终裁决由证据完整性、波动阈值及现有数值门槛统一生成。关键分数缺失或波动超限先 hold，然后判断 reject、pass、其余 hold。这个约定替代旧文档尚未定稿的多数裁决细节，不再作为讨论前置条件。

### 5.5 LLM 网关规则

所有调用经过一个 `LLMGateway`。接口接收角色、消息、期望输出类型和数据处理范围，返回已验证对象及调用元数据。

网关承担模型映射、凭证、超时、调用预算、重试、usage 和 JSON 校验。优先使用模型实际支持的结构化输出；否则使用 JSON 输出指令加 Pydantic 校验，最多修复一次。禁止用 `eval()` 解析输出，不用大量正则猜测缺失字段。LiteLLM 的能力检查与结构化输出接口见 [官方说明](https://docs.litellm.ai/docs/completion/json_mode)。

网络或服务限流采用有限重试；认证失败立即报配置错误；解析失败与科学证据不足分开记录。`.env`、API key 和鉴权请求头不进入日志。仅允许本地处理的资料由服务层限制路由，不能通过 agent 传参绕过。

来源处理范围随提取、归纳和后续推断继承。包含 `local_only` 来源的派生内容也只走本地端点；该调用的角色映射可由网关改为本地并记录原因。公共文献和明确允许远程处理的资料才进入远程请求。完整运行只检查实际需要的端点，独立本地任务不因无关远程角色缺少凭证而失败。

### 5.6 工作区与日志

首版使用 SQLite 的 `sources`、`records`、`runs`、`events`、`llm_calls` 表即可。启用外键，写入使用事务；记录更新保存新版本。CLI 与 UI 只通过工作区服务访问数据，不散落 SQL。

运行输出采用以下结构：

```text
runs/<run_id>/
├── manifest.json            # 配置、模型、提示词哈希、输入与 profile
├── candidates.jsonl
├── rankings.csv
├── predictions.jsonl
├── mechanisms.jsonl
├── gaps.jsonl
├── report.md
└── events.jsonl
```

模拟 profile 使用独立工作区或命名空间，报告显著标为 synthetic。真实预测与原始观测分类型保存，预测结果不进入原始证据查询。

运行模式默认为 `prediction`：创建 run 时冻结可用输入，并在工作区查询入口排除该案例留出的 ROS 与抗菌观测及其派生记录。`explanation` 模式允许读取明确选定的观测，报告标记为解释分析。这个最小区分只防止误把已知结果当作预测命中，不展开复杂评估协议。

## 6. 各 Agent 的最小实现要求

| Agent | 读取 | 必须输出 | 初版行为 |
|---|---|---|---|
| extractor | PDF 文本块、source、原文位置 | Evidence 与缺失字段 | 远程和本地分别提取，比较字段；允许远程的冲突做一次仲裁 |
| synthesizer | 已入库且可使用的 Evidence | 基元、材料卡、关联证据 | 按家族和材料整理，不覆盖原始提取 |
| designer | 目标场景、基元卡、候选数量 | 跨家族 Candidate | 首版由 LLM 提案，代码校验类别、字段和重复；精细枚举后置 |
| screener | Candidate、检索证据、rubric | Assessment | 按五维分数评估，代码聚合与排序 |
| predictor | Candidate、场景、可比证据 | Prediction | 给区间、依据、假设或未知项，不将主观评分换算成实测数值 |
| reasoner | Candidate、证据及允许使用的预测或观测 | Mechanism | ROS 路径、位置、贡献判断、替代解释和证伪条件 |

预测默认覆盖 H₂O₂、·OH 的浓度/生成量，以及出水 CFU/log 去除；速率仅在时间定义足以支持时计算。真实灭活单列一个目标，缺少可分辨证据时返回未知。没有校准的粗略范围标为估计范围，不能命名为统计置信区间。机理中的 ROS 贡献默认给带依据的定性判断，有支持时才补数值。

提示词放独立文件，公共规则复用。公共规则至少包括：仅引用提供或检索得到的真实证据、保留未知项、遵守输出结构、引用原文位置、不提供实验操作步骤。

独立任务缺少资料时，从工作区查询并做有限补检索。比如直接运行 `reasoner` 不要求材料先达到 pass；直接运行 `screener` 也不要求由 designer 创建材料。

对仅允许本地处理的全文，不做远程提取或远程仲裁，保留质量限制。在线来源无法取得全文时保留元数据，不能用标题或摘要编造全文数值。扫描 PDF 暂标为需要 OCR，继续其他任务。

## 7. 完整流程的首版执行方式

1. 加载配置，创建 run，记录 live/mock、任务目标、场景和输入快照。
2. 检查本次任务将使用的本地与远程端点状态。
3. 导入或复用元数据，选择当前批次的可用全文，提取并归纳。
4. 生成跨家族候选，加入指定先导材料并去重。
5. 逐个评估并形成榜单。证据不足时最多执行两轮缺口补充。
6. 对排名靠前且适合继续的候选，以及指定先导材料，做性能预测与机理探究。原有 hold/reject 标记保留。
7. 保存候选档案、榜单、未知项、调用统计与可阅读报告。

首版主流程顺序执行，不增加复杂回溯图。失败的单个候选不终止其他候选；全局模型不可用或配置无效时明确停止。运行在阶段边界记录进度，恢复时复用已成功阶段；已变化的配置启动新 run，不静默混用旧结果。

缺口只处理实际缺失证据，不因为一个完整评分低于通过线就无限检索。新增证据后最多重跑受影响阶段，预算耗尽输出 partial。复杂的后期机理纠正流程暂缓。

## 8. CLI、UI 与用户可执行示例

所有命令均是接手 agent 需要实现的目标接口，当前还不存在。参数含义写入 `--help`。命令返回结构化错误，CLI 不吞掉异常。

```bash
# 安装业务依赖与开发工具；vLLM 使用独立环境。
uv sync --group dev

# 检查配置、文件路径、GPU 信息、本地端点和远程端点。
uv run cdi doctor --profile live

# 导入已有清单和本地全文。
uv run cdi ingest metadata data/all_titles_dois.csv
uv run cdi ingest documents data/documents --limit 8 --scope local_only

# scope 在确认处理范围后可为 remote_allowed；默认 local_only。
# 本地与远程共同提取的实测须选允许远程处理的全文。

# 完整运行。默认 profile 为 live。
uv run cdi run --scenario config/scenarios/default.yaml --candidates 15 --mode prediction

# 查询结果。实际 run ID 由上述命令输出，用户自行替换。
uv run cdi runs list
uv run cdi report --run RUN_ID

# 独立调用每个 agent；input 文件通过对应角色的 Pydantic 模型验证。
uv run cdi agent extractor --input examples/extractor.json
uv run cdi agent synthesizer --input examples/synthesizer.json
uv run cdi agent designer --input examples/designer.json
uv run cdi agent screener --input examples/screener.json
uv run cdi agent predictor --input examples/predictor.json
uv run cdi agent reasoner --input examples/reasoner.json

# 重排只读取已有有效分数，不产生模型调用。
uv run cdi rank --run RUN_ID --rubric config/rubric.yaml

# 导入真实实验记录并比较；数值缺失时只导入结构，不伪造数据。
uv run cdi validate --run RUN_ID --observations data/experimental/results.csv

# 读取已选定的观测做解释分析；OBSERVATION_ID 由导入命令返回。
uv run cdi run --mode explanation --observation-id OBSERVATION_ID

# 基础单 agent 对照入口。
uv run cdi evaluate --baseline single-agent --scenario config/scenarios/default.yaml

# 离线测试示例走相同业务代码，但明确使用 mock profile。
uv run cdi run --profile mock --scenario config/scenarios/default.yaml

# 浏览器界面。
uv run streamlit run src/cdi_agent/ui.py --server.address 127.0.0.1
```

示例输入由初始化或 fixtures 生成，不能引用不存在的真实论文。需要记录引用的示例，先创建测试记录再填其 ID。仓库携带示例时显著标为测试数据。

UI 必须实现运行总览、候选浏览器、工作区浏览器、配置、缺口与验证五类页面。完整运行和独立调用共用同一服务入口。长任务在独立工作进程运行，UI 读取持久化进度，刷新页面不重新启动任务。首版同一工作区只允许一个写入任务运行。

配置页显示修改前后差异并保存新版本。候选页可以固定展示先导材料，但不修改其排序位置或得分。显示区分预测值、实测值、未知项和 synthetic 数据。

## 9. 分阶段完成计划

每完成一个阶段，更新 `docs/IMPLEMENTATION_STATUS.md`，记录完成内容、实际命令、检查结果和剩余依赖。完成前置阶段后直接进入下一阶段，不为已确定的要求反复等待确认。

### M0：环境、项目骨架与双端连通

**工作**：检查已有文件；建立 Python 包、CLI、依赖锁定、`.env.example`、忽略规则；在 WSL2 启动本地模型；接入远程模型；实现 doctor。

**产物**：`pyproject.toml`、`uv.lock`、`deploy/` 启动文件、初版 README 和部署记录。

**完成条件**：在目标机至少各完成一次本地与远程真实响应，记录模型和环境。没有目标机或凭证时可以继续写与验证离线代码，但 M0 的真实连通项保持未完成。

### M1：工作区、配置与基础结构

**工作**：实现基本 Pydantic 记录、SQLite 服务、run 与事件记录、配置检查、指定材料及默认场景初始化。

**产物**：可重复初始化的工作区、1500 条元数据导入、材料与场景记录。

**完成条件**：重复导入不制造重复 DOI；未知值保持未知；写入失败回滚；任何结果可关联到 run、来源和配置。

### M2：文献获取、双模型提取与归纳

**工作**：接入首个检索 API；导入本地 PDF；保存来源和页码；分块提取；远程与本地字段比对；对允许远程处理的冲突做一次复核；生成材料与基元卡。

**产物**：可独立使用的 extractor、synthesizer，文献与证据浏览数据。

**完成条件**：对一小批可用真实全文跑通；数值与来源可定位；模型实际身份可查；无法读取的文献明确标记，不伪造字段。无需先处理完整文献库。

### M3：候选生成、筛选与重排

**工作**：实现 designer、screener；生成不同家族候选；加入先导材料；五维评分、重复聚合、排序；重排版本保存。

**产物**：候选档案、真实评分调用、CSV 榜单、可复算的分数。

**完成条件**：身份去重有效；生成不足报告实际数量；评分有证据或缺失标记；修改权重后排名可重算且零 LLM 调用。

### M4：性能预测、机理与完整编排

**工作**：实现 predictor、reasoner；补充区间检查与证据引用；串联全流程；实现简单缺口重试、部分完成、阶段恢复与报告导出。

**产物**：完整 run、候选分数、ROS 与出水去除预测、机理档案、未知项和调用统计。

**完成条件**：完整流程可自主结束；指定材料可独立预测和分析；不强制每个字段有数值；预算与重试有效；不是六个返回固定文本的空壳。

### M5：五类界面与实验记录

**工作**：实现五类 Streamlit 页面；完整与独立任务入口；真实结果浏览；配置修改；CSV/XLSX 实验导入；简单预测与观测对比。

**产物**：可操作的本地应用，数值与证据的导出入口。

**完成条件**：页面读取真实工作区；长任务不因刷新重复启动；预测与观测按材料、指标、单位和时间含义匹配；无真实实验文件时保留导入待办。

### M6：基础方法对照、实测与最终交接

**工作**：增加单 agent 基线；同样输入、可用证据和总调用上限下运行；输出简单比较报告；完成离线测试和目标机小批真实混合运行；完善文档。

**产物**：对照命令、测试结果、混合运行报告、安装和恢复指南、已知限制。

首版基线采用一个连续上下文的通用 agent，默认使用 `reasoner` 角色的模型，复用相同检索工具、输入快照和输出结构，不使用六角色分工。报告调用次数、token、耗时、引用可定位率、格式通过率、有效定量输出比例；有可比实测时再报告数值误差、区间覆盖与宽度。无观测的指标记为不可计算。记录两组实际模型配置，模型差异也可能影响结果，不将比较直接解释为纯粹的架构因果效应。

**完成条件**：本地与远程调用均可核验；有真实证据驱动的完整案例输出；六类独立入口均可用；报告实际表现，不以多 agent 必须获胜作为软件验收条件。

当前硬件、凭证或实验数据无法取得时，将对应实测单独标为阻塞，并说明已完成的软件范围。不能用 mock 结果代替真实验收。

## 10. 编码规范

1. **依赖方向**：CLI/UI → 业务服务与编排 → agent/工具 → LLM 网关与工作区。UI 不直接写 SQL 或拼模型请求。
2. **类型**：公开函数写类型注解；跨模块数据用 Pydantic 或 dataclass；禁止用无限扩张的 `dict[str, Any]` 传遍全项目。
3. **职责**：模型名、URL、提示词、权重和预算放配置或资源文件；业务代码不散落这些常量。
4. **错误**：区分配置错误、服务不可用、输出校验失败和证据不足。禁止 `except Exception: return {}`。仅在顶层记录未处理异常并标记 run 失败。
5. **真实与模拟**：只有显式 mock profile 或测试依赖注入才能返回固定数据；没有 API key 时 live 必须报错。
6. **数学**：总分、标准差、log 换算与区间检查用代码；未知与零严格分开；阈值比较前不四舍五入。
7. **数据**：使用 `pathlib.Path` 和 UTF-8；时间存 UTC，界面按配置显示；保存原始单位和换算结果；不覆盖原始文献及实验文件。
8. **日志**：至少包含 run_id、stage、candidate_id（适用时）、模型、耗时和错误类型；不打印密钥、鉴权头或不必要的完整全文。
9. **凭证**：只提供变量名与空值的 `.env.example`，真实 `.env` 忽略；来源处理范围由网关和工作区服务执行。
10. **模型输出**：外部文献视为资料，不执行其中的指令；agent 输出必须校验；不通过执行模型生成的 Python 或 SQL 完成业务。
11. **工程规模**：先完成一条真实纵向流程，再扩大批量；不先建设插件平台、分布式基础设施或复杂代理框架。
12. **依赖锁定**：业务依赖锁进 uv.lock；GPU 推理环境单独留档。第三方 API 差异封装在适配器中。
13. **代码检查**：使用 Ruff 格式化和 lint；mypy 检查自有模块。必要的第三方类型豁免局部设置，不全局关闭类型检查。
14. **测试范围**：测试真实边界、失败情况和核心业务，不追求无意义的覆盖率数字，不测试第三方库自身行为。
15. **工作交接**：每阶段更新状态文档。记录已实现、已测试、外部阻塞和后置事项，不把接口定义算作功能完成。

## 11. 测试与验收清单

### 11.1 必要自动化测试

- DOI 大小写与 URL 前缀规范化，重复导入不新增同一来源。
- 候选身份包含配体、框架与载体，名称相似不随意合并。
- 无效权重、缺失维度、NaN、反向区间与不存在证据 ID 被识别。
- 仅调整权重时不发出模型请求，并保留新榜单版本。
- 仅本地处理的内容不能进入远程请求；mock 记录不能混入 live 报告。
- API 认证错误不无限重试；格式修复和预算上限生效。
- 指定材料不需要先通过筛选即可独立运行 predictor/reasoner。
- 一个候选失败时其他候选继续，恢复时不重复写成功阶段。
- 出水去除与灭活、运行时间与接触时间不混用。
- 留出实验值在预测请求中不可见；实验解释任务显式允许读取。

### 11.2 运行命令

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src/cdi_agent
uv run pytest -m "not live"
uv run cdi doctor --profile live
uv run pytest -m live
```

真实测试只在明确配置环境后运行，默认测试不调用收费 API。live 测试使用小批数据和有限预算；无服务时跳过并明确报告，不能当作通过。

### 11.3 最终完成检查

- [ ] 全新 WSL2 环境可按文档安装，或已有环境可按检查步骤复现。
- [ ] 远程与本地模型均真实参与一次完整运行。
- [ ] 六个独立 agent 命令可使用同一套工作区记录运行。
- [ ] 现有元数据导入完成，全文不可用状态可见。
- [ ] 有完整候选报告、榜单、预测、机理、缺口和调用记录。
- [ ] 至少有一项基于真实证据的定量预测；若全部未知，单列科学目标未达成。
- [ ] 排名可调整，先导材料可固定展示，历史结果可追溯。
- [ ] 五类页面均连接真实功能。
- [ ] 实验导入和对比功能可用；真实案例数据是否导入单独列明。
- [ ] 单 agent 对照可运行，结果按实际情况报告。
- [ ] 离线测试、真实实测和未完成项在状态文档中分开。
- [ ] README、部署说明、配置示例和最终交接记录齐全。

## 12. 可直接交给 Coding Agent 的任务提示

> 请根据 `docs/IMPLEMENTATION_PLAN.md` 实现 CDI 多 agent 系统，从 M0 开始按顺序完成 M6。阅读现有设计、评分规则、配置和数据，保留已有文件。用户已确认第一版在 Windows + WSL2 的 RTX 5090 机器上同时使用远程 API 和本地模型；系统要自主运行完整流程，也能独立调用六类子 agent。
>
> 使用本文给出的工程默认值，不因此前暂缓的科学或架构细节重新进入长期方案讨论。实现真实模型调用、证据存储、可调排名、ROS 与出水去除预测、机理分析、五类界面和基础方法对照。先完成一条真实流程，再扩展规模。mock 只用于测试，不能代替真实验收。
>
> 每阶段完成后更新 `docs/IMPLEMENTATION_STATUS.md` 并继续。不要重新询问已确定的材料和实验条件。遇到缺少凭证、目标机访问或真实数据时，准确记录受阻项，继续不依赖它的工作；需要用户提供信息时只问必要问题。最终报告列出运行命令、实际验证结果和剩余外部依赖。
