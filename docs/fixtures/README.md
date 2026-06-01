# P0 测试夹具

- `sample-jd.txt`：粘贴 JD 示例（手工测试 / 单测引用）。
- `sample-resume.docx`：虚构简历（张明 / 后端工程师），供单测与 `curl` 验收；勿替换为含真实 PII 的文件。

手工验收（需配置 `DEEPSEEK_API_KEY` 且 `USE_REAL_PIPELINE=1`）：

```bash
cd server
export USE_REAL_PIPELINE=1
export DEEPSEEK_API_KEY=sk-...
uv run uvicorn src.main:app --host 127.0.0.1 --port 8787

# jd_text 必须是表单字符串，不能作为文件字段上传
curl -F resume=@../docs/fixtures/sample-resume.docx \
  --form-string "jd_text=$(cat ../docs/fixtures/sample-jd.txt)" \
  http://127.0.0.1:8787/sessions
```
