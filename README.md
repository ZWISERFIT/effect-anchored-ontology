# Lineage-Anchored Ontology (LAO)

> **AI认知层基础设施。从LLM的概率推理到LAO的确定性校验。每一个Agent的错误都自动变成代码，永远不再犯。**

> `pip install lineage-anchored-ontology`

---

## 什么是LAO？

LAO是位于任何LLM和其输出之间的**确定性校验层**。六个开源Python库。三行代码接入。

LLM让AI知道世界。**LAO让AI知道你。**

聪明是通用的。懂你是专用的。

---

## 五层架构

```
L1 路由决策层      → 31模型自主选择·功耗感知·任务难度→模型分层
L2 六函数引擎      → H幻觉门·M记忆锚·C上下文·A自适应·E效果·S自审计
L3 经验复利闭环    → 错误→自动筛选→调取→保存→生成约束代码
L4 交互确认层      → 认知冲突自动处理/推送用户确认
L5 三层认知架构    → 懂你→懂业务→懂经营
```

---

## 快速开始

```bash
pip install lineage-anchored-ontology
```

```python
from effect_anchored import HallucinationGate, MemoryAnchor, ModelRouter

# 1. 路由: 自主选择31个模型中最合适的
from effect_anchored.routing import ModelRouter
router = ModelRouter()
route = router.route("这个任务该用哪个模型？资本分析·估值建模")
print(f"选择: {route.model}")

# 2. 校验: 模型产出的东西对不对
gate = HallucinationGate()
result = gate.check("门店在深圳", context={"anchors": ["founder_first_store_location"]})
print(f"幻觉拦截: {not result.passed}")  # True — 地理事实错误被拦截

# 3. 记忆: 确定性查找，不猜
anchor = MemoryAnchor()
anchor.put("founder_first_store_location", "东莞市万江街道")
print(anchor.get("founder_first_store_location"))  # "东莞市万江街道"
```

---

## 六函数一览

| 函数 | 职能 | 一句话 |
|:--|:--|:--|
| **H** HallucinationGate | 幻觉拦截 | "你说门店在深圳？拦截。" |
| **M** MemoryAnchor | 确定性记忆 | 不猜，直接查。 |
| **C** ContextRebuilder | 上下文重建 | 还原Agent当时看到了什么。 |
| **A** AdaptiveConstraint | 自适应约束 | 每犯一次错，生成一条Python规则。 |
| **E** EffectAnchoring | 效果锚定 | Agent说的效果 vs 实际验证。 |
| **S** SelfAudit | 自审计 | 系统审计自己的规则。 |

---

## 经验复利闭环（核心壁垒）

```
Agent犯错误 → H函数拦截
                ↓
    经验萃取器识别错误模式
                ↓
    约束生成器生成Python代码
                ↓
    规则注册器写入永久约束
                ↓
    下次同样错误 → 自动拦截 · 不再犯
```

**用了3个月的Agent vs 刚装的Agent → 质的差距。迁移成本 = 失去所有自动积累的约束谱系。**

---

## 与其他方案对比

| | NVIDIA Guardrails | LangChain Memory | LAO |
|:--|:--|:--|:--|
| 规则来源 | 人类预设 | 人类预设 | **Agent自身错误自动生成** |
| 幻觉处理 | 内容过滤 | 无 | **确定性外部校验** |
| 记忆 | 无 | 语义搜索(概率) | **确定性key-value(非概率)** |
| 自进化 | 无 | 无 | **错误→自动生成Python约束代码** |
| 经验复利 | 无 | 无 | **每犯一次错，系统更强** |

---

## 三步走路线图

```
Step 1: 开发者工具（现在）
├── pip install lineage-anchored-ontology
├── 解决两个具体痛点：幻觉+记忆
├── 开源·Apache 2.0
└── 开发者用了觉得好用 → 推荐给另一个

Step 2: 经验复利引擎（用了就离不开）
├── Agent的错误自动变成约束代码
├── 用了3个月 vs 刚装 → 质的差距
└── "换框架？我的Agent又要重新犯120天的错。"

Step 3: 认知层基础设施（市场定义我们）
├── 不是我们宣称自己是基础设施
├── 是开发者用了回不去
└── 就像pip——它就是。
```

---

## 测试

```bash
git clone https://github.com/ZWISERFIT/lineage-anchored-ontology
cd lineage-anchored-ontology
pip install -e ".[dev]"
pytest tests/ -v
```

**59 tests · 全部通过 · 0 failed**

---

## 开源协议

Apache 2.0

---

## 由ZWISERFIT 9-Agent Collective构建

LAO是 **ZWISERFIT** 的第一个对外开源产品——面向线下实体门店的全栈AI自治平台。ZWISERFIT是9套垂直Agent微型OS构成的AI操作系统级公司。

- **创始人：** 莫淑瑜 · 保险内行×健身布道者×产品架构师×AI系统创建者
- **AI军团：** 9-Agent 24×7自主运行
- **门店：** 东莞万江 · 7年深耕

**LLM让AI知道世界。LAO让AI知道你。**

https://github.com/ZWISERFIT
