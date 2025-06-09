import subprocess

def run_command(cmd, **kwargs):
    """
    Wrapper around subprocess.run that captures errors gracefully.

    Args:
        cmd (str | list): Command to run.
        **kwargs: Passed directly to subprocess.run.

    Returns:
        dict: {
            'returncode': int,
            'stdout': str,
            'stderr': str,
            'error': str or None
        }
    """
    if isinstance(cmd, str):
        cmd = cmd.split()

    # defaults, allow override
    kwargs.setdefault('capture_output', True)
    kwargs.setdefault('text', True)

    try:
        result = subprocess.run(cmd, **kwargs)
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'error': None
        }
    except subprocess.CalledProcessError as e:
        return {
            'returncode': e.returncode,
            'stdout': e.stdout or '',
            'stderr': e.stderr or '',
            'error': str(e)
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': '',
            'error': str(e)
        }
