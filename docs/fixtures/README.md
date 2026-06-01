# P0 测试夹具

- `sample-jd.txt`：粘贴 JD 示例（手工测试 / 单测引用）。
- `sample-resume.docx`：用 Word 或 `python-docx` 生成一份最小简历后放于此目录（勿提交含真实 PII 的文件）。

生成最小 docx：

```bash
cd server && uv run python -c "from docx import Document; Document().save('../docs/fixtures/sample-resume.docx')"
```
