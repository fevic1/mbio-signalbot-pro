class SkillDiscovery:

    def discover(self, registry):

        skills = []

        for server, tools in getattr(
            registry,
            "_tools",
            {},
        ).items():

            for tool in tools:

                skills.append({
                    "server": server,
                    "tool": tool,
                })

        return skills
