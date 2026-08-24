from enum import Enum, auto

class ISLState(Enum):
    ACTIVE = auto()
    FAILED = auto()
    DEGRADED = auto()
    RECOVERING = auto()