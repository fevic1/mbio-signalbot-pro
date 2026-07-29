from .execution_memory import ExecutionMemory
from .feedback import FeedbackAnalyzer
from .coordinator import LearningCoordinator
from .event_handler import LearningEventHandler
from .provider_feedback import ProviderFeedbackHandler

from .lesson_extractor import LessonExtractor
from .knowledge_patterns import KnowledgePatternStore
from .planner_feedback import PlannerFeedbackEngine


__all__ = [
    "ExecutionMemory",
    "FeedbackAnalyzer",
    "LearningCoordinator",
    "LearningEventHandler",
    "ProviderFeedbackHandler",
    "LessonExtractor",
    "KnowledgePatternStore",
    "PlannerFeedbackEngine",
    "ExecutionEvaluator",
    "PlannerOptimizer",
]


def __getattr__(name):

    if name == "ExecutionEvaluator":
        from .evaluator import ExecutionEvaluator
        return ExecutionEvaluator

    if name == "PlannerOptimizer":
        from .optimizer import PlannerOptimizer
        return PlannerOptimizer

    raise AttributeError(
        f"module 'aios.learning' has no attribute '{name}'"
    )
