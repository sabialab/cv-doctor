export const FREE_CHANGE_LIMIT = 3;

export const PROCESSING_STEPS = [
  { id: "parsing_resume", label: "解析简历" },
  { id: "analyzing_jd", label: "分析岗位描述" },
  { id: "matching", label: "匹配与缺口" },
  { id: "generating_changes", label: "生成修改建议" },
] as const;

export type ProcessingStepId = (typeof PROCESSING_STEPS)[number]["id"];
