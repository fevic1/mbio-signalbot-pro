class Observable:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)
        return observer

    def unsubscribe(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event):
        for observer in tuple(self._observers):
            observer(event)
