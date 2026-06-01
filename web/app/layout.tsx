import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CV Doctor",
  description: "简历与岗位匹配诊断（P0 MVP）",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
