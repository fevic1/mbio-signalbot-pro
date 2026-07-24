from dataclasses import dataclass, field


@dataclass
class PermissionSet:

    analyze: bool = True

    plan: bool = True

    execute_workflows: bool = True

    modify_systems: bool = False

    deploy_changes: bool = False

    spend_resources: bool = False

    access_restricted_actions: bool = False


    def can(
        self,
        action: str,
    ) -> bool:

        return getattr(
            self,
            action,
            False,
        )
