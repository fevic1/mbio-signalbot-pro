from dataclasses import dataclass


@dataclass
class PermissionSet:

    can_search: bool = True

    can_code: bool = True

    can_review_code: bool = True

    can_reason: bool = True

    can_plan: bool = True

    can_execute_shell: bool = False

    can_write_files: bool = False

    can_verify: bool = True


    def can(
        self,
        capability: str,
    ) -> bool:

        return getattr(
            self,
            capability,
            False,
        )


    def allowed_actions(self):

        return {
            key: value
            for key, value in self.__dict__.items()
        }
