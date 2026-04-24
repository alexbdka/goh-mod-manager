from PySide6.QtCore import QEvent


class LanguageChangeMixin:
    """
    Reapplies translated text when Qt emits LanguageChange.
    """

    def changeEvent(self, event: QEvent) -> None:
        super_change_event = getattr(super(), "changeEvent", None)
        if callable(super_change_event):
            super_change_event(event)
        if event.type() == QEvent.Type.LanguageChange:
            retranslate = getattr(self, "retranslate_ui", None)
            if callable(retranslate):
                retranslate()
