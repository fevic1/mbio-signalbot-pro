from .analyzer import PlannerLessonAnalyzer
from .updater import PlannerFeedbackUpdater


class PlannerFeedbackEngine:


    def __init__(self):

        self.analyzer = PlannerLessonAnalyzer()

        self.updater = PlannerFeedbackUpdater()



    def improve_plan(
        self,
        plan,
        memories,
    ):

        lessons = self.analyzer.analyze(
            memories
        )

        return self.updater.improve(
            plan,
            lessons,
        )
