---
name: ultimate-revelation
description: Use when long or multi-source material is repetitive, low-density, contradictory, or difficult to synthesize, and the user needs a few defensible insights rather than exhaustive notes, topic summaries, or a literal transcript.
---

# Ultimate Revelation

## Overview

把长材料压缩成少数会改变理解、判断或行动的认知，不做目录式缩写。

**核心原则：先建立证据链，再形成结论。** 每条认知必须能反向回到足以支持它的原始内容；时间戳、页码和段落号只负责定位。

默认使用用户的语言，优先交付结果，不展示冗长的内部工作过程。

## Result Contract

遵守用户指定的长度和格式。用户没有指定时，按下面顺序输出：

1. **一句话总判断**：仅当整份材料有单一主轴时输出。
2. **1–7 条关键认知**：默认争取 3–5 条；证据只支持 1 条时就只写 1 条。
3. **认知之间的关系**：仅当至少 3 条认知存在明显的因果、层级或张力时输出。

每条关键认知使用这个最小充分结构：

```markdown
### N. 可判断、可反驳的认知结论

- 原始内容：
  - F1「足以支持结论的原话、数字、事件或明确对比」（来源与定位）
  - F2「另一条独立或互补证据」（来源与定位）
- 推导链：F1 + F2 → 事实关系 → 稳定模式 → So What
- 边界：关键条件、反例、分歧或不可外推之处。
- 底层原则：仅当材料能直接支持生成机制时输出；否则省略或标为“候选原则（推断）”。
- 行动含义：仅当用户需要且材料支持时输出。
```

简洁任务可把推导链和边界各压缩为一句。审计任务保留 F 编号；普通任务可以不显示内部编号，但必须保留原始内容。

## Workflow

### 1. Cover the source

- 阅读完整相关材料后再下全局结论；无法完整处理时，先披露实际覆盖范围。
- 音视频先取得尽可能完整的转写；PDF、网页和报告保留标题、表格、数字、引文归属及上下文。
- 多份材料分别维护来源边界，不把 A 的事实写成 B 的主张。
- 只做最小限度的转写或 OCR 纠正，不把猜测词语当关键证据。

### 2. Build evidence before prose

按章节、话题或时间段记录原子事实，并标记为：观察事实、材料陈述、案例、反证/边界。先保存最小充分原文，再解释它意味着什么。

### 3. Cluster and rank globally

去重后按机制、约束、因果阶段、问题—反应—结果或变化前后分组。优先保留同时具备以下特征的事实簇：

- 证据具体且足量；
- 一条结论解释多条独立事实；
- 回答“为什么”或“所以什么”；
- 会改变判断或行动；
- 边界可以说清。

重复次数不是重要性。案例只能证明可能性，不能单独证明普遍规律。

### 4. Derive, then reverse-audit

沿这条链上升：

`原始内容 → 事实关系 → 稳定模式 → So What → 生成机制`

在失去向下解释力之前停止。再按相反方向检查：结论中的每个关键限定词是否都能回到已展示的原始内容。断链时缩小或删除结论，不用更多抽象语言掩盖缺证。

复杂、多源或审计型任务必须读取 [references/derivation-method.md](references/derivation-method.md)。

### 5. Deliver the capability, not the scaffolding

先给结论，再给最小充分证据和推导。不要把分块笔记、候选簇、评分表或完整事实账本倾倒给用户，除非用户明确要求审计过程。

## Hard Constraints

- 展示原始内容本身；定位信息不能单独充当证据。
- 明确观点归属；说话人或作者的判断不是自动成立的外部事实。
- 保留会改变结论的分歧、反例与样本边界。
- 不把同一主张的重复表达伪装成多份独立证据。
- 不强行凑认知数量，不强行输出第一性原理或行动建议。
- 外部知识与材料内证据分开；若用户要求事实核验，另行检索并标明来源。
- 结论的确定性不得高于证据。

遇到数字冲击、案例外推、观点冲突、OCR 不稳或输出过度展开时，读取 [references/gotchas.md](references/gotchas.md)。

## Resources

- [references/derivation-method.md](references/derivation-method.md)：长材料、多来源与审计任务的完整三遍法。
- [references/gotchas.md](references/gotchas.md)：从失败中沉淀的高风险模式与修正方式。
- [references/worked-example.md](references/worked-example.md)：需要校准默认输出形态时读取。
- [evals/cases.json](evals/cases.json)：维护路由正例、forbidden-load 反例与执行验收；正常任务不加载。
- `scripts/validate_output.py`：当默认结构被写入 Markdown 文件时运行，检查字段缺失和“只有定位、没有原文”的证据。

## Final Gate

提交前确认：

- 已读完相关材料，或明确披露覆盖范围；
- 每条认知都展示了最小充分原始内容；
- 推导能正向推出，也能反向回溯；
- 事实、材料主张、案例、推断和原则没有混写；
- 关键分歧与边界没有被压平；
- 输出明显短于原材料，并遵守用户指定的长度与形式。
