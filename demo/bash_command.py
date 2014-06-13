import os
import subprocess
import logging
from tempfile import NamedTemporaryFile

logger = logging.getLogger(os.path.basename(__file__))

class CommandError(Exception): pass

class DevNull(object):
    name = os.devnull

class CommandResult(object):
    def __init__(self):
        self.cmd = ''
        self.err = ''
        self.out = ''
        self.return_code = 0
        self.succeeded = None
        self.failed = None
        self.captured = ''

def command(command, capture=True, ignore=False):
    logger.debug("running {0}".format(command))
    if capture is False:
        tmp_out = DevNull()
        tmp_err = DevNull()
    else:
        tmp_out = NamedTemporaryFile()
        tmp_err = NamedTemporaryFile()

    with open(tmp_out.name, 'w') as tout:
        with open(tmp_err.name, 'w') as terr:
            p = subprocess.Popen(command, stdout=tout, stderr=terr, shell=True, executable="/bin/bash")

            while True:
                if p.poll() is not None:
                    break

    if capture is False:
        stdout = ""
        stderr = ""
    else:
        with open(tmp_out.name, 'r') as f:
            stdout = ''.join(f.readlines()).strip()
        with open(tmp_err.name, 'r') as f:
            stderr = ''.join(f.readlines()).strip()

    out = CommandResult()
    out.cmd = command
    out.err = stderr
    out.out = stdout
    out.return_code = p.returncode
    out.succeeded = True if p.returncode == 0 else False
    out.failed = False if p.returncode == 0 else True
    out.captured = capture

    if out.succeeded is True or ignore is True:
        return out
    else:
        m = "{0} returned {1}".format(out.cmd, out.return_code)
        logger.error(m)
        print(out.out)
        print(out.err)        
        raise CommandError(m)