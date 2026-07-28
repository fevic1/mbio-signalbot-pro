class Disposable:

    def close(self):
        pass

    def dispose(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.dispose()
        return False
