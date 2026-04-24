from collections.abc import Callable


class EventType:
    """Names for coarse-grained application events emitted by the facade."""

    CATALOGUE_CHANGED = "CATALOGUE_CHANGED"
    ACTIVE_MODS_CHANGED = "ACTIVE_MODS_CHANGED"
    PRESETS_CHANGED = "PRESETS_CHANGED"


class EventBus:
    """Minimal in-process event bus used to decouple state changes from Qt."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Register a callback for a named event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Remove a callback if it was previously registered."""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass

    def emit(self, event_type: str, *args, **kwargs) -> None:
        """Invoke every callback registered for a named event type."""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(*args, **kwargs)
