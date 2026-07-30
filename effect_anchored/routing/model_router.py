"""
ModelRouter — 模型路由与降级链路
================================

根据任务分类结果选择最优模型，并构建降级链路。
"""

from dataclasses import dataclass


@dataclass
class RouteSelection:
    """单次路由决策结果"""

    task: str
    model: str
    tier: str
    cost: str  # "$/M tokens"
    fallback_chain: list


class ModelRouter:
    """根据任务难度层级路由到最合适的模型。

    每个层级定义了优先级降序的候选模型池，
    主模型为 pool[0]，其余为降级链路。
    """

    MODEL_POOL = {
        "ultra_light": [
            {"model": "deepseek-flash", "cost": "$0.14/$0.28"},
        ],
        "light": [
            {"model": "qwen-plus", "cost": "$0.40/$1.20"},
            {"model": "deepseek-flash", "cost": "$0.14/$0.28"},
        ],
        "medium": [
            {"model": "deepseek-v4", "cost": "$1.10/$4.40"},
            {"model": "qwen-plus", "cost": "$0.40/$1.20"},
        ],
        "heavy": [
            {"model": "deepseek-v4-pro", "cost": "$2.20/$8.80"},
            {"model": "deepseek-v4", "cost": "$1.10/$4.40"},
        ],
        "reasoning": [
            {"model": "deepseek-reasoner", "cost": "$0.55/$2.19"},
            {"model": "deepseek-v4-pro", "cost": "$2.20/$8.80"},
        ],
    }

    def __init__(self, task_classifier=None):
        """初始化路由器。

        Args:
            task_classifier: 可选的自定义分类器实例。
                             默认使用 TaskClassifier。
        """
        from effect_anchored.routing.task_classifier import TaskClassifier

        self.classifier = task_classifier or TaskClassifier()

    def route(
        self,
        task: str,
        budget: float | None = None,
        latency_preference: str | None = None,
    ) -> RouteSelection:
        """根据任务文本路由到最优模型。

        Args:
            task: 任务描述文本。
            budget: 可选预算上限 ($USD)。
            latency_preference: 可选延迟偏好 ("low" | "balanced" | "quality")。

        Returns:
            RouteSelection 包含所选模型、层级、成本和降级链路。
        """
        tier = self.classifier.classify(task)
        pool = self.MODEL_POOL.get(tier, self.MODEL_POOL["medium"])
        primary = pool[0]
        fallback_chain = [m["model"] for m in pool[1:]]

        return RouteSelection(
            task=task,
            model=primary["model"],
            tier=tier,
            cost=primary["cost"],
            fallback_chain=fallback_chain,
        )
