import errno
import os
import psutil
import signal
import sys
import time


NUM_WORKERS = 4


instance = None
descendents = {}


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def wait_time():
    if os.environ.get('TRAVIS'):
        return 15
    else:
        return 3

def this_dir():
    return os.path.dirname(__file__)

def procfile_path():
    return os.path.join(this_dir(), 'scripts', 'Procfile')

def service_command_line():
    return ['honcho', '-f', procfile_path(), 'start']


def setUp():
    global instance

    logdir = 'var/log'
    mkdir_p(logdir)
    outlog = open(os.path.join(logdir, 'honcho.out'), 'w')
    errlog = open(os.path.join(logdir, 'honcho.err'), 'w')

    if not os.environ.get('SKIP_PROCFILE'):
        instance = psutil.Popen(service_command_line(),
                shell=False, stdout=outlog, stderr=errlog)
        time.sleep(wait_time())
        if instance.poll() is not None:
            raise RuntimeError("honcho instance terminated prematurely")
        else:
            descendents = get_descendents()

def signal_processes(processes, sig):
    signaled_someone = False
    for p in processes:
        try:
            p.send_signal(sig)
            signaled_someone = True
        except psutil.NoSuchProcess:
            pass

    return signaled_someone

def get_descendents():
    processes = psutil.Process(instance.pid).get_children(recursive=True)
    return dict([(x.pid, x) for x in processes])

def cleanup():
    ec = instance.poll()
    if ec is None:
        descendents.update(get_descendents())

        instance.wait(timeout=2)

        if not signal_processes(descendents, signal.SIGINT):
            return

        time.sleep(3)
        signal_processes(descendents, signal.SIGKILL)

        instance.send_signal(signal.SIGINT)
    else:
        sys.stderr.write('Unexpected exit of services:  code = (%s)\n' % ec)


# NOTE If this doesn't run then honcho will be orphaned...
def tearDown():
    if not os.environ.get('SKIP_PROCFILE'):
        cleanup()
