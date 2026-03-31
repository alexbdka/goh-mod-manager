from typing import Callable, Dict, List


class EventType:
    CATALOGUE_CHANGED = "CATALOGUE_CHANGED"
    ACTIVE_MODS_CHANGED = "ACTIVE_MODS_CHANGED"
    PRESETS_CHANGED = "PRESETS_CHANGED"


class EventBus:
    """
    A simple pure-Python event bus.
    Allows the core logic to notify the UI (or any other subscriber)
    of state changes without depending on a specific framework like Qt.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass

    def emit(self, event_type: str, *args, **kwargs) -> None:
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(*args, **kwargs)
