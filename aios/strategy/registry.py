from .versioning import StrategyVersionRegistry


class StrategyRegistry:

    def __init__(self):

        self.registry = StrategyVersionRegistry()
        self.metrics = {}


    def register_strategy(
        self,
        name,
        version,
        metadata=None,
    ):

        return self.registry.register(
            name,
            version,
            metadata,
        )


    def attach_metrics(
        self,
        name,
        version,
        metrics,
    ):

        key = f"{name}:{version}"

        self.metrics[key] = metrics


    def performance(
        self,
        name,
        version,
    ):

        return self.metrics.get(
            f"{name}:{version}",
            {},
        )


    def compare(
        self,
        name,
    ):

        results = {}

        for item in self.registry.list_versions(name):

            key = (
                f"{item['name']}:"
                f"{item['version']}"
            )

            results[key] = self.metrics.get(
                key,
                {},
            )

        return results
