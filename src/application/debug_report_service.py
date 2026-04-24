from src.application.use_cases.debug_report import ApplicationDebugReportUseCase
from src.utils import app_paths as app_paths


class ApplicationDebugReportService(ApplicationDebugReportUseCase):
    def build_report(self):
        return self.build()
