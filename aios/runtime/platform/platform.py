import platform
import sys


class RuntimePlatform:

    def __init__(self):
        self.python = sys.version.split()[0]
        self.implementation = platform.python_implementation()
        self.system = platform.system()
        self.release = platform.release()
        self.machine = platform.machine()
        self.processor = platform.processor()

    def export(self):
        return {
            "python": self.python,
            "implementation": self.implementation,
            "system": self.system,
            "release": self.release,
            "machine": self.machine,
            "processor": self.processor,
        }
