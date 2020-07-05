import hashlib
import os
import sys
import tempfile

import pkg_resources

import nox.virtualenv
import nox.sessions
import nox.command


def requires(*packages, python=None, silent=True):
    """
    Ensure we run in a virtualenv with the given packages installed.

    This function may call `exec()` to replace the current process. It should
    be called before you import any required packages.

    :param packages: List of packages to pass to `pip install`
    :param python: Python version to pass to `virtualenv -p`
    :param silent: Whether to suppress output from `pip`
    """

    packages = [_requirement('box')] + list(packages)

    venv = nox.virtualenv.VirtualEnv(
        location=os.path.join(
            tempfile.gettempdir(),
            'box-virtualenv',
            _sha1(python, *packages)),
        interpreter=python,
        reuse_existing=True)

    if venv.bin in os.environ['PATH']:
        return

    if venv.create():
        nox.command.run(
            args=['python', '-m', 'pip', 'install'] + list(packages),
            path=venv.bin,
            env=venv.env,
            silent=silent)

    os.environ.update(venv.env)
    os.execvp('python', ['python'] + sys.argv)


def _requirement(package):
    """
    Returns a pip requirement for the given package.
    """

    return str(pkg_resources.require(package)[0].as_requirement())


def _sha1(*args):
    """
    Returns a sha1 hex digest of the given arguments
    """

    h = hashlib.sha1()
    for arg in args:
        if arg:
            h.update(arg.encode('utf8'))
    return h.hexdigest()