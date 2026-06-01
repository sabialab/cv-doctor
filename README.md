# 🩺 CV-Doctor 简历对症下药

<p align="center">
  <strong>LLM 驱动的简历深度优化工具 — 针对具体公司+岗位精准优化</strong>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> •
  <a href="#功能特性">功能特性</a> •
  <a href="#安装">安装</a> •
  <a href="#使用方法">使用方法</a> •
  <a href="#架构">架构</a> •
  <a href="#贡献">贡献</a>
</p>

---

## 为什么需要 CV-Doctor？

市面上的简历工具大多是**简历生成器**——从零开始帮你建简历。

CV-Doctor 不同：它是**简历优化器**——你已有简历，我们帮你针对目标公司和岗位"对症下药"。

### 🎯 对症下药模式（核心卖点）

> "我想去字节跳动做后端开发，怎么改简历？"

CV-Doctor 会自动：
1. 采集字节跳动的公司画像（文化、技术栈、规模）
2. 采集目标岗位 JD（支持 BOSS直聘自动采集）
3. 交叉分析同公司多条 JD，提取隐性要求
4. 逐条对比你的简历 vs 岗位要求
5. 生成针对性优化建议 + 优化后简历

**没有其他开源项目做到这一层。**

---

## 功能特性

- 🔍 **简历解析** — 支持 PDF / DOCX / Markdown，ML 级解析精度
- 📊 **ATS 评分** — TF-IDF 关键词匹配 + LLM 语义分析双引擎
- 🏢 **公司画像** — 天眼查 + 官网 + 技术博客多源采集
- 🎯 **对症下药** — 针对具体公司+岗位深度优化（独家功能）
- 🤖 **LLM 驱动** — 支持 OpenAI / Claude / Gemini / Ollama 等 30+ 提供商
- 🔒 **隐私优先** — 支持 Ollama 本地模型，简历数据不出本机
- 📝 **多格式输出** — PDF / DOCX / Markdown，带匹配度报告
- 🇨🇳 **中文优先** — 国内招聘平台深度集成

---

## 安装

```bash
# pip 安装（推荐）
pip install cv-doctor

# 或从源码安装
git clone https://github.com/your-username/cv-doctor.git
cd cv-doctor
pip install -e .
```

### 配置 LLM

```bash
# 使用 OpenAI（默认）
cv-doctor config set llm.provider openai
cv-doctor config set llm.model gpt-4o
export OPENAI_API_KEY="sk-..."

# 使用本地 Ollama（隐私优先）
cv-doctor config set llm.provider ollama
cv-doctor config set llm.model llama3.1

# 使用 Claude
cv-doctor config set llm.provider anthropic
cv-doctor config set llm.model claude-sonnet-4-20250514
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## 使用方法

### 通用优化模式

```bash
# 从 JD 文本优化
cv-doctor optimize resume.pdf --jd "岗位要求：熟悉 Go 语言，有微服务架构经验..."

# 从 JD 文件优化
cv-doctor optimize resume.pdf --jd-file jd.txt

# 从 JD 链接优化
cv-doctor optimize resume.pdf --jd-url "https://www.zhipin.com/job_detail/..."
```

### 对症下药模式 ⭐

```bash
# 针对具体公司+岗位优化
cv-doctor target resume.pdf --company "字节跳动" --position "后端开发工程师"

# 指定城市
cv-doctor target resume.pdf --company "腾讯" --position "产品经理" --city "深圳"
```

### ATS 评分

```bash
cv-doctor score resume.pdf --jd "岗位描述..."
```

### 公司画像

```bash
cv-doctor company "字节跳动"
cv-doctor company "阿里巴巴" --position "前端开发"
```

---

## 输出示例

```
$ cv-doctor target resume.pdf --company "字节跳动" --position "后端开发"

━━━ CV-Doctor 简历对症下药 ━━━

📋 简历解析完成
   姓名: 张三 | 工作经验: 5年 | 技能: 12项

🏢 公司画像: 字节跳动
   行业: 互联网/信息技术 | 规模: 100000+人 | 阶段: 已上市
   文化关键词: 追求极致、开放谦逊、坦诚清晰、始终创业
   技术栈: Go, Rust, K8s, Microservice, Distributed System

📊 JD 分析 (基于 3 条同岗位 JD 交叉分析)
   硬技能: Go(必须), K8s(必须), 分布式系统(必须), MySQL(加分)
   软技能: 沟通能力, 自驱力, 技术热情

🔍 差距分析
   ✅ 完全匹配 (5/8): Go, MySQL, 微服务架构, RESTful API, Git
   ⚠️ 部分匹配 (2/8): K8s(有Docker经验但未提及K8s), 分布式(有概念但缺实践)
   ❌ 缺失 (1/8): Rust

📝 优化建议
   1. 将 Docker 经历扩展为「容器化 + K8s 编排」
   2. 在项目描述中增加分布式相关关键词
   3. 将「追求极致」的文化关键词自然融入自我评价
   4. 技能排序调整: Go → K8s → MySQL → Redis → ...

📈 评分对比
   优化前: 62/100 (关键词覆盖: 58%)
   优化后: 87/100 (关键词覆盖: 91%)
   提升: +25 分

✅ 优化后简历已生成: output/张三_字节跳动_后端开发_optimized.pdf
📊 完整报告已生成: output/张三_字节跳动_后端开发_report.md
```

---

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户输入层                          │
│  简历(PDF/DOCX/MD) + JD文本 / 目标公司+岗位              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      数据采集层                          │
│  简历解析(marker-pdf) | JD采集(Playwright) | 公司画像    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      分析引擎层                          │
│  JD解析 | 公司画像分析 | 差距分析 | ATS评分              │
│           LiteLLM（统一接口，30+提供商）                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      优化输出层                          │
│  简历重写(LLM) | 评分报告 | 多格式输出(PDF/DOCX/MD)      │
└─────────────────────────────────────────────────────────┘
```

---

## 技术栈

| 模块 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| CLI | Typer |
| PDF 解析 | marker-pdf |
| DOCX 解析 | python-docx |
| LLM | LiteLLM (OpenAI/Ollama/Gemini/Claude) |
| 数据模型 | Pydantic v2 |
| PDF 生成 | WeasyPrint |
| 网页采集 | Playwright |
| 企业信息 | 天眼查 API |
| 本地 LLM | Ollama |

---

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](docs/contributing.md)。

```bash
# 开发环境
git clone https://github.com/your-username/cv-doctor.git
cd cv-doctor
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check .
```

---

## 许可证

[MIT License](LICENSE)

---

## 致谢

- [boss-agent-cli](https://github.com/can4hou6joeng4/boss-agent-cli) — BOSS直聘数据采集参考
- [JadeAI](https://github.com/LingyiChen-AI/JadeAI) — 简历模板设计参考
- [marker-pdf](https://github.com/VikParuchuri/marker) — PDF 解析引擎
- [LiteLLM](https://github.com/BerriAI/litellm) — LLM 统一接口
