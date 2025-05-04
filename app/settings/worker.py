from pydantic import Field

from .app import AppSettings


class WorkerSettings(AppSettings):
    enabled_workers: set[str] = Field(
        default={"customer"},
        title="Workers que devem ser inicializados",
    )


worker_settings = WorkerSettings()
