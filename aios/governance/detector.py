from .issues import SystemIssue


class IssueDetector:


    def __init__(self):

        self.issues = []



    def detect(
        self,
        title,
        description,
        severity,
        source,
    ):

        issue = SystemIssue(
            title,
            description,
            severity,
            source,
        )

        self.issues.append(
            issue
        )

        return issue



    def history(self):

        return [
            issue.describe()
            for issue in self.issues
        ]
