import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-semibold">隐私说明（P0）</h1>
      <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-neutral-700">
        <li>上传的简历与岗位描述仅用于当次诊断。</li>
        <li>
          数据保留：本地联调（内存存储）在进程重启前保留，或你可在结果页点击「删除本会话」立即清除；
          生产环境（Cloudflare R2 + D1）默认在 24 小时内自动删除（由 <code>AUTO_DELETE_HOURS</code>{" "}
          配置，见 docs/p0-cloudflare-stack.md），亦可随时手动删除。
        </li>
        <li>
          诊断会调用第三方云模型（DeepSeek）处理文本；不向第三方出售数据，不用于训练通用模型。
        </li>
        <li>P0 本地默认内存联调；上线后文件与会话元数据存于 Cloudflare R2 / D1。</li>
      </ul>
      <Link href="/" className="mt-8 inline-block text-sm text-neutral-600 underline">
        返回首页
      </Link>
    </main>
  );
}
