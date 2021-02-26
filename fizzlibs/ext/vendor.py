import os.path
import site
import sys


PYTHON_VERSION = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])


def add(path, index=1):
    """Insert site dir or virtualenv at a given index in sys.path.

    Args:
      path: relative path to a site dir or virtualenv.
      index: sys.path position to insert the site dir.

    Raises:
      ValueError: path doesn't exist.
    """
    venv_path = os.path.join(path, 'lib', PYTHON_VERSION, 'site-packages')
    if os.path.isdir(venv_path):
        site_dir = venv_path
    elif os.path.isdir(path):
        site_dir = path
    else:
        raise ValueError('virtualenv: cannot access %s: '
                         'No such virtualenv or site directory' % path)

    sys_path = sys.path[:]
    del sys.path[index:]
    site.addsitedir(site_dir)
    sys.path.extend(sys_path[index:])
