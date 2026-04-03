from unittest.mock import MagicMock

from src.ui.workers.mod_import_worker import ModImportWorker


class TestModImportWorker:
    def test_run_calls_manager_without_reload_and_emits_success(self):
        manager = MagicMock()
        manager.import_mod.return_value = True
        worker = ModImportWorker(manager, "archive.zip")
        success_calls = []

        worker.signals.success.connect(lambda: success_calls.append(True))

        worker.run()

        manager.import_mod.assert_called_once()
        args, kwargs = manager.import_mod.call_args
        assert args == ("archive.zip",)
        assert callable(kwargs["progress_callback"])
        assert callable(kwargs["conflict_callback"])
        assert kwargs["reload_on_success"] is False
        assert success_calls == [True]

    def test_run_emits_error_when_manager_returns_false(self):
        manager = MagicMock()
        manager.import_mod.return_value = False
        worker = ModImportWorker(manager, "archive.zip")
        errors = []

        worker.signals.error.connect(errors.append)

        worker.run()

        assert errors == ["Mod import returned False for an unknown reason."]

    def test_run_emits_error_when_manager_raises(self):
        manager = MagicMock()
        manager.import_mod.side_effect = RuntimeError("boom")
        worker = ModImportWorker(manager, "archive.zip")
        errors = []

        worker.signals.error.connect(errors.append)

        worker.run()

        assert errors == ["boom"]
