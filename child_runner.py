import os
import sys
import math
import resource
import logging

from models import *
from enums import *
from constants import *

log = logging.getLogger(logger_name)


def run_child_process(
        command=(),
        limit: ResourceLimit = ResourceLimit,
        redirect: Redirect = Redirect(),
        use_path_env: bool = False
):
    if len(command) == 0:
        log.fatal('Invalid command')
        sys.exit(ErrorCode.INVALID_CONFIG)
    try:
        if limit.cpu_time > 0:
            cpu_over_time = int(math.ceil(limit.cpu_time / 1000 + 0.5))
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_over_time, cpu_over_time))
        if limit.memory > 0 and not limit.no_memory_limit:
            resource.setrlimit(resource.RLIMIT_AS, (limit.memory, limit.memory))
        # if limit.process > 0:
        #     resource.setrlimit(resource.RLIMIT_NPROC, (limit.process, limit.process))
        # if limit.stack > 0:
        #     resource.setrlimit(resource.RLIMIT_STACK, (limit.stack, limit.stack))
        # if limit.output_size > 0:
        #     resource.setrlimit(resource.RLIMIT_FSIZE, (limit.output_size, limit.output_size))
    except ValueError as e:
        log.fatal('Resource limit failed: ' + e.__str__())
        sys.exit(ErrorCode.RESOURCE_LIMIT_FAILED)
    except resource.error as e:
        log.fatal('Set resource limit failed: ' + e.__str__())
        sys.exit(ErrorCode.RESOURCE_LIMIT_FAILED)

    try:
        if redirect.stdin != '':
            input_fd = os.open(redirect.stdin, os.O_RDONLY)
            os.dup2(input_fd, sys.stdin.fileno())
        if redirect.stdout != '':
            output_fd = os.open(redirect.stdout, os.O_CREAT | os.O_WRONLY)
            os.dup2(output_fd, sys.stdout.fileno())
        if redirect.stderr != '':
            error_fd = os.open(redirect.stderr, os.O_CREAT | os.O_WRONLY)
            os.dup2(error_fd, sys.stderr.fileno())
    except OSError as e:
        log.fatal('Dup2 failed: ' + e.__str__())

    # TODO: setuid & setgid
    # TODO: seccomp load

    env = {'PATH': os.getenv('PATH')}
    os.execve(command[0], command[0:], env)
    log.fatal('Execve failed')
    sys.exit(ErrorCode.EXEC_FAILED)
