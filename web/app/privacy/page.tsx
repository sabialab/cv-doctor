import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-12 prose prose-neutral">
      <h1>隐私说明（P0）</h1>
      <ul>
        <li>上传的简历与岗位描述仅用于当次诊断。</li>
        <li>默认约 24 小时后自动删除；你可随时在结果页触发删除（API 已实现）。</li>
        <li>不用于训练通用模型；不向第三方出售数据。</li>
        <li>P0 使用内存/临时存储联调；生产环境使用 Cloudflare R2 + D1。</li>
      </ul>
      <Link href="/">返回首页</Link>
    </main>
  );
}
