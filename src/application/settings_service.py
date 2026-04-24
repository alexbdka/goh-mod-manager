from src.application.use_cases.settings import ApplicationSettingsUseCase


class ApplicationSettingsService(ApplicationSettingsUseCase):
    def apply_settings(self, settings):
        return self.apply(settings)
