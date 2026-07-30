"""
TaskClassifier — 功耗感知式任务分类
====================================

根据任务关键词将任务映射到五个难度层级之一。
默认返回 "medium"。
"""


class TaskClassifier:
    """功耗感知式任务分类"""

    TIERS = {
        "ultra_light": [
            "心跳回复",
            "状态检查",
            "数据汇总",
            "格式转换",
            "hello",
            "ping",
        ],
        "light": [
            "模板填充",
            "简单查询",
            "格式转换",
            "日报",
            "摘要",
        ],
        "medium": [
            "行业调研",
            "内容撰写",
            "分析摘要",
            "代码审查",
            "技术文档",
        ],
        "heavy": [
            "战略推理",
            "BP内容",
            "叙事架构",
            "资本分析",
            "估值建模",
        ],
        "reasoning": [
            "估值建模",
            "多步推理",
            "复杂数学",
            "财务模型",
        ],
    }

    def classify(self, task: str) -> str:
        """将任务文本分类到难度层级。

        Args:
            task: 任务描述文本。

        Returns:
            层级标识: "ultra_light" | "light" | "medium" | "heavy" | "reasoning"
        """
        task_lower = task.lower()
        for tier, keywords in self.TIERS.items():
            for kw in keywords:
                if kw in task_lower:
                    return tier
        return "medium"  # default
