from dataclasses import asdict

import click
import logging
import sys
from constants import *
from models import *
from runner import run


@click.command()
@click.option('--debug', '-d', default=False, help='Print debug logs', is_flag=True)
@click.option('--cpu-time', '-c', default=0, help='Set CPU time limit')
@click.option('--real-time', '-r', default=0, help='Set real time limit')
@click.option('--memory', '-m', default=0, help='Set memory limit')
@click.option('--stack', '-s', default=0, help='Set stack memory limit')
@click.option('--output-size', '-O', default=0, help='Set output limit')
@click.option('--process', '-p', default=0, help='Set process limit')
@click.option('--input', '-i', default='', help='Redirect stdin file path')
@click.option('--output', '-o', default='', help='Redirect stdout file path')
@click.option('--error', '-e', default='', help='Redirect stderr file path')
@click.option('--log', '-l', default='', help='Redirect log file path')
@click.option('--uid', '-u', default=0, help='Run command with a specified uid')
@click.option('--gid', '-g', default=0, help='Run command within a specified user group')
@click.option('--use-path-env', default=True, help='Pass system\'s PATH environment into sandbox', is_flag=True)
@click.option('--no-memory-limit', default=False, help='Compare memory usage only instead of setrlimit', is_flag=True)
@click.option('--console-log/--no-console-log', default=False, help='Print logs into console')
@click.argument('command', nargs=-1, type=click.Path(), required=True)
def main(
        debug: bool,
        cpu_time: int,
        real_time: int,
        memory: int,
        stack: int,
        output_size: int,
        process: int,
        input: str,
        output: str,
        error: str,
        log: str,
        uid: int,
        gid: int,
        use_path_env: bool,
        no_memory_limit: bool,
        console_log: bool,
        command: list,
):
    """Run your commands in the sandbox."""
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d [%(process)d:%(funcName)s] %(message)s')
    if log == '' or console_log:
        log_handler = logging.StreamHandler(sys.stderr)
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
    if log != '':
        file_handler = logging.FileHandler(log)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.info('UniJudge Sandbox Runner')
    logger.info('Version 0.0.1')
    logger.debug('Command: [%s]' % ', '.join(command))
    if len(command) == 0:
        logger.fatal('Cannot find command')
        exit(1)
    limit = ResourceLimit(
        cpu_time=cpu_time,
        real_time=real_time,
        memory=memory,
        stack=stack,
        output_size=output_size,
        process=process,
        no_memory_limit=no_memory_limit
    )
    redirect = Redirect(
        stdin=input,
        stdout=output,
        stderr=error,
    )
    logger.debug(asdict(limit).__str__())
    logger.debug(asdict(redirect).__str__())
    run(command, limit, redirect, use_path_env)


if __name__ == '__main__':
    main()
