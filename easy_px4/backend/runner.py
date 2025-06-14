import subprocess
from typing import Union, List, Optional
from dataclasses import dataclass, field

@dataclass
class CommandResult:
    returncode: int
    stdout: str = ''
    stderr: str = ''
    error: Optional[str] = None
    obj: Optional[object] = field(default=None)  # Store process object

def run_command(
    cmd: Union[str, List[str]],
    live: bool = False,
    logger: Optional[object] = None,
    **kwargs
) -> CommandResult:
    """
    Run a subprocess command.

    Args:
        cmd: Command string or list of arguments.
        live: If True, print output live on the same line.
        logger: Optional logger object with .info(str) method to override print.
        **kwargs: Additional args passed to subprocess.

    Returns:
        CommandResult object.
    """
    def make_result(returncode, stdout='', stderr='', error=None, obj=None):
        return CommandResult(returncode, stdout, stderr, error, obj)

    if isinstance(cmd, str):
        cmd = cmd.split()

    if live:
        kwargs.setdefault('stdout', subprocess.PIPE)
        kwargs.setdefault('stderr', subprocess.STDOUT)
        kwargs.setdefault('text', True)
        kwargs.setdefault('bufsize', 1)

        try:
            process = subprocess.Popen(cmd, **kwargs)
            last_len = 0

            use_logger_debug = logger and logger.getEffectiveLevel() <= 10  # 10 = DEBUG

            for line in process.stdout:
                line = line.rstrip('\n')

                clear = ' ' * max(last_len - len(line), 0)
                last_len = len(line)

                if use_logger_debug:
                    logger.debug(line)
                else:
                    print(f'\r{line}{clear}', end='', flush=True)

            process.wait()
            if not use_logger_debug:
                print()

            return make_result(process.returncode, obj=process)
        except Exception as e:
            return make_result(-1, error=str(e))
    else:
        kwargs.setdefault('capture_output', True)
        kwargs.setdefault('text', True)

        try:
            result = subprocess.run(cmd, **kwargs)

            return make_result(result.returncode, result.stdout, result.stderr, obj=result)
        except subprocess.CalledProcessError as e:
            return make_result(e.returncode, e.stdout or '', e.stderr or '', str(e))
        except Exception as e:
            return make_result(-1, error=str(e))

