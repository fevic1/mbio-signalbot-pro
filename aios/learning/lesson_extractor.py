from datetime import datetime, timezone
import uuid


class LessonExtractor:


    def extract(
        self,
        execution_record,
    ):

        result = (
            execution_record
            .get("result", {})
        )

        lessons = []


        if result.get(
            "issues"
        ):

            lessons.append(
                {
                    "type": "failure",
                    "lesson":
                        "Review failed execution causes before repeating approach",
                    "issues":
                        result["issues"],
                }
            )


        if result.get(
            "confidence",
            0
        ) < 0.5:

            lessons.append(
                {
                    "type": "quality",
                    "lesson":
                        "Increase verification requirements for low confidence execution",
                }
            )


        if result.get(
            "status"
        ) == "completed":

            lessons.append(
                {
                    "type": "success",
                    "lesson":
                        "Execution pattern produced acceptable outcome",
                }
            )


        return {
            "id": str(uuid.uuid4()),
            "lessons": lessons,
            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        }
