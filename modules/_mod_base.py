# /modules/_mod_base.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Mapping, Optional, Protocol

class Logger(Protocol):
    def __call__(
        self,
        message: str,
        *,
        level: str = "INFO",
        module: Optional[str] = None,
        extra: Optional[Mapping[str, Any]] = None,
    ) -> None: ...
    def set_context(self, **ctx: Any) -> None: ...
    def get_context(self) -> Dict[str, Any]: ...

class SyncStatus(Enum):
    IDLE = auto()
    RUNNING = auto()
    SUCCESS = auto()
    WARNING = auto()
    FAILED = auto()
    CANCELLED = auto()

@dataclass
class SyncContext:
    run_id: str
    dry_run: bool = False
    timeout_sec: Optional[int] = None
    ui_hints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SyncResult:
    status: SyncStatus
    started_at: float
    finished_at: float
    duration_ms: int
    items_total: int = 0
    items_added: int = 0
    items_removed: int = 0
    items_updated: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ModuleError(RuntimeError): ...
class RecoverableModuleError(ModuleError): ...
class ConfigError(ModuleError): ...

class SyncModule(Protocol):
    name: str

    def __init__(self, config: Mapping[str, Any], logger: Logger) -> None: ...

    def validate_config(self) -> None:
        """
        Raise ConfigError with a clear message if config is invalid/missing.
        """

    def run_sync(self, ctx: SyncContext) -> SyncResult:
        """
        Execute the sync. Must be deterministic for the given 'ctx' and config.
        Should not block forever; honor ctx.timeout_sec if provided.
        """

    def get_status(self) -> Mapping[str, Any]:
        """
        Lightweight, quick status snapshot for UI (e.g., last run, counters).
        """

    def cancel(self) -> None:
        """
        Best-effort cancellation hook. Safe to call even if not running.
        """

    def set_logger(self, logger: Logger) -> None:
        """
        Allow the host app to replace or wrap the logger at runtime.
        """
