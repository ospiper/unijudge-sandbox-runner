from dataclasses import dataclass
from enums import *


@dataclass
class ResourceLimit:
    cpu_time: int = 0
    real_time: int = 0
    memory: int = 0
    stack: int = 0
    output_size: int = 0
    process: int = 0
    no_memory_limit: bool = False


@dataclass
class Redirect:
    stdin: str = ''
    stdout: str = ''
    stderr: str = ''


@dataclass
class RunResult:
    result: ResultCode = ResultCode.SUCCESS
    error: ErrorCode = ErrorCode.SUCCESS
    exit_code: int = 0
    signal: int = 0
    cpu_time: int = 0
    real_time: int = 0
    memory: int = 0
