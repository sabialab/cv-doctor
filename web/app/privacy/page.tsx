import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-semibold">隐私说明（P0）</h1>
      <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-neutral-700">
        <li>上传的简历与岗位描述仅用于当次诊断。</li>
        <li>
          计划在后续版本配置自动删除（TTL）；当前可在结果页点击「删除本会话」立即清除数据。
        </li>
        <li>不用于训练通用模型；不向第三方出售数据。</li>
        <li>P0 使用内存/临时存储联调；生产环境使用 Cloudflare R2 + D1。</li>
      </ul>
      <Link href="/" className="mt-8 inline-block text-sm text-neutral-600 underline">
        返回首页
      </Link>
    </main>
  );
}
