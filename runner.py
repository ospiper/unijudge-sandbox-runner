import signal
import os
import sys
import logging
from dataclasses import asdict
import json
import time
import resource

from models import *
from enums import *
from constants import *
from timer import Timer
from child_runner import run_child_process

log = logging.getLogger(logger_name)


def run(command=(), limit: ResourceLimit = ResourceLimit(), redirect: Redirect = Redirect(), use_path_env = False):
    log.debug('Runner start')
    log.debug('Limits: %s' % asdict(limit))
    log.debug('Redirect: %s', asdict(redirect))

    uid = 0
    # uid = os.getuid()
    if uid != 0:
        log.fatal('Root required')
        ret = RunResult(result=ResultCode.SYSTEM_ERROR, error=ErrorCode.ROOT_REQUIRED)
        print(json.dumps(asdict(ret)))
        sys.exit(0)

    start = time.time()
    ret = RunResult()
    try:
        child = os.fork()
        if child < 0:
            log.fatal('Fork failed')
            ret.result = ResultCode.SYSTEM_ERROR
            ret.error = ErrorCode.FORK_FAILED
            print(json.dumps(asdict(ret)))
            sys.exit(0)
        elif child == 0:
            log.debug('Child process successfully forked')
            run_child_process(command, limit, redirect, use_path_env)
        else:
            try:
                timer = None
                if limit.real_time > 0:
                    timer = Timer(child, limit.real_time)
                    timer.start()
                child_id, stop_status, resource_usage = os.wait4(child, 0)
                if timer is not None:
                    timer.stop()
                end = time.time()
                if os.WIFSIGNALED(stop_status):
                    ret.signal = os.WTERMSIG(stop_status)
                if ret.signal == signal.SIGUSR1:
                    ret.result = ResultCode.SYSTEM_ERROR
                else:
                    ret.exit_code = os.WEXITSTATUS(stop_status)
                    ret.cpu_time = resource_usage.ru_utime * 1000
                    ret.memory = resource_usage.ru_maxrss
                    ret.real_time = (end - start) * 1000
                    if ret.exit_code != 0:
                        ret.result = ResultCode.RUNTIME_ERROR
                    if ret.signal == signal.SIGSEGV:
                        if 0 < limit.memory < ret.memory:
                            ret.result = ResultCode.MEMORY_LIMIT_EXCEEDED
                        else:
                            ret.result = ResultCode.RUNTIME_ERROR
                    else:
                        if ret.signal != 0:
                            ret.result = ResultCode.RUNTIME_ERROR
                        if 0 < limit.memory < ret.memory:
                            ret.result = ResultCode.MEMORY_LIMIT_EXCEEDED
                        if 0 < limit.real_time < ret.real_time:
                            ret.result = ResultCode.REAL_TIME_LIMIT_EXCEEDED
                        if 0 < limit.cpu_time < ret.cpu_time + 15:
                            ret.result = ResultCode.CPU_TIME_LIMIT_EXCEEDED
            except OSError as e:
                log.fatal('Wait failed: ' + e.__str__())
                ret = RunResult(result=ResultCode.SYSTEM_ERROR, error=ErrorCode.WAIT_FAILED)
                print(json.dumps(asdict(ret)))
                sys.exit(0)
    except OSError as e:
        log.fatal('Fork failed: ' + e.__str__())
        ret = RunResult(result=ResultCode.SYSTEM_ERROR, error=ErrorCode.FORK_FAILED)
        print(json.dumps(asdict(ret)))
        sys.exit(0)
    log.debug('Return: ' + asdict(ret).__str__())
    print(json.dumps(asdict(ret)))
    sys.exit(0)
