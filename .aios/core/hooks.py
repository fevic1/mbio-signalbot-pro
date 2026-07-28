#!/usr/bin/env python3

from collections import defaultdict


class HookManager:

    def __init__(self):
        self._hooks = defaultdict(list)

    def register(self, hook, func):
        self._hooks[hook].append(func)

    def unregister(self, hook, func):
        if func in self._hooks[hook]:
            self._hooks[hook].remove(func)

    def run(self, hook, *args, **kwargs):
        results = []

        for func in self._hooks.get(hook, []):
            results.append(func(*args, **kwargs))

        return results

    def list(self):
        return {
            hook: len(funcs)
            for hook, funcs in self._hooks.items()
        }


hooks = HookManager()


if __name__ == "__main__":

    def before():
        print("before")

    def after():
        print("after")

    hooks.register("startup", before)
    hooks.register("shutdown", after)

    hooks.run("startup")
    hooks.run("shutdown")

    print(hooks.list())
