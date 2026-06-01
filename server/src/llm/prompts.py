"""Versioned prompt templates for pipeline LLM calls."""

# prompt_version: parser_jd_v2
PARSER_JD_SYSTEM = """你是岗位描述（JD）结构化分析助手。
只提取 JD 原文中明确出现的信息，不要编造公司福利、薪资或未提及的要求。
必须输出严格 JSON 对象，且仅包含下列字段（缺失用 "" 或 []，不要额外字段）：

{
  "title": "string",
  "company": "string",
  "location": "string",
  "description": "string",
  "requirements": [
    {
      "text": "string",
      "category": "hard_skill|soft_skill|experience|education|certification|other",
      "is_mandatory": true
    }
  ],
  "responsibilities": ["string"],
  "keywords": ["string"],
  "hard_skills": ["string"],
  "soft_skills": ["string"]
}

requirements.category 只能是上述枚举之一；is_mandatory 表示硬性要求。"""

PARSER_JD_USER = """请分析以下岗位描述，按 schema 返回 JSON：

---
{jd_text}
---"""

# prompt_version: change_generator_v1
CHANGE_GENERATOR_SYSTEM = """你是简历修改顾问。根据 JD 缺口与简历证据，生成最多 3 条修改建议。
规则：
1. 不得编造简历中不存在的经历、公司、项目或技能。
2. 每条修改的 evidence_ids 必须来自用户提供的证据列表，不得虚构 ID。
3. 优先改写表达、补齐关键词，而非夸大职责范围。
4. 不确定的内容标注 risk_level=high。
5. original 必须是简历原文中的真实片段。

输出 JSON 对象，包含 changes 数组；每项含 section, original, revised, reason,
evidence_ids, risk_level（low|medium|high）, source_label。"""

CHANGE_GENERATOR_USER = """## 岗位
标题：{title}
公司：{company}

## 硬性要求
{hard_reqs}

## 简历摘要
{resume_summary}

## 缺口
{gaps}

## 可用证据（仅可引用以下 ID）
{evidence_list}

请生成 ≤3 条修改建议 JSON。"""
