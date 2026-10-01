#!/usr/bin/env python3
"""Linux/Python 3.12 teaching trace; no external dependencies.
Run: python3 scripts/experiments/k001/process_lifecycle.py
Only creates/kills its own direct children, in a temporary directory.
"""
import json
import os
from pathlib import Path
import platform
import queue
import signal
import sys
import tempfile
import threading


def worker(directory):
    directory = Path(directory)
    stop = threading.Event()
    ready = queue.Queue()

    def background():
        ready.put({'tid': threading.get_native_id(),
                   'proc_tid': int(read_fields('/proc/thread-self/status')['Pid'])})
        stop.wait()

    thread = threading.Thread(target=background)
    thread.start()
    thread_ids = ready.get(timeout=5)
    (directory / 'result.tmp').write_text('partial\n')
    print(json.dumps({'pid': os.getpid(), 'ppid': os.getppid(),
                      'main_tid': threading.get_native_id(),
                      'worker_tid': thread_ids['tid'],
                      'proc_pid': int(read_fields('/proc/self/status')['Pid']),
                      'proc_worker_tid': thread_ids['proc_tid']}), flush=True)
    command = sys.stdin.readline().strip()
    stop.set()
    thread.join(timeout=5)
    if command == 'finish':
        (directory / 'result.tmp').write_text('complete\n')
        os.replace(directory / 'result.tmp', directory / 'result.txt')
        return 0
    return 2


def read_fields(path):
    fields = {}
    for line in Path(path).read_text().splitlines():
        key, _, value = line.partition(':')
        if key in ('State', 'Tgid', 'Pid', 'PPid', 'Threads'):
            fields[key] = value.strip()
    return fields


def attempt(directory, fail):
    command_r, command_w = os.pipe()
    report_r, report_w = os.pipe()
    sys.stdout.flush()
    pid = os.fork()  # Parent is single-threaded at this point.
    if pid == 0:
        os.close(command_w)
        os.close(report_r)
        os.dup2(command_r, 0)
        os.dup2(report_w, 1)
        os.close(command_r)
        os.close(report_w)
        try:
            os.execv(sys.executable, [sys.executable, __file__, '--worker', str(directory)])
        except OSError:
            os._exit(127)
    os.close(command_r)
    os.close(report_w)
    reaped = False
    try:
        with os.fdopen(report_r) as report:
            identity = json.loads(report.readline())
        proc_pid = identity['proc_pid']
        snapshot = read_fields(f'/proc/{proc_pid}/status')
        tids = sorted(int(p.name) for p in Path(f'/proc/{proc_pid}/task').iterdir())
        assert identity['pid'] == pid
        assert identity['ppid'] == os.getpid()
        assert identity['main_tid'] == pid
        assert int(snapshot['Threads']) == 2
        assert tids == sorted([proc_pid, identity['proc_worker_tid']])
        if fail:
            os.kill(pid, signal.SIGKILL)
        else:
            os.write(command_w, b'finish\n')
        # Observe termination without consuming the child's exit status.
        os.waitid(os.P_PID, pid, os.WEXITED | os.WNOWAIT)
        zombie = read_fields(f'/proc/{proc_pid}/status')['State']
        assert zombie.startswith('Z')
        waited_pid, raw_status = os.waitpid(pid, 0)
        reaped = True
        code = os.waitstatus_to_exitcode(raw_status)
        assert waited_pid == pid
        assert code == (-signal.SIGKILL if fail else 0)
        assert not Path(f'/proc/{proc_pid}').exists()
        names = sorted(p.name for p in directory.iterdir())
        expected = ['result.tmp'] if fail else ['result.txt']
        assert names == expected
        return {'case': 'killed' if fail else 'normal',
                'identity': identity, 'live': snapshot, 'task_ids': tids,
                'before_waitpid': zombie, 'exit_code': code,
                'after_waitpid_proc_exists': False, 'files': names}
    finally:
        os.close(command_w)
        if not reaped:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            os.waitpid(pid, 0)


def main():
    print(json.dumps({'kernel': platform.release(), 'python': platform.python_version()}))
    with tempfile.TemporaryDirectory(prefix='k001-') as directory:
        root = Path(directory)
        for fail in (False, True):
            attempt_directory = root / ('killed' if fail else 'normal')
            attempt_directory.mkdir()
            print(json.dumps(attempt(attempt_directory, fail)), flush=True)
        # Application-level recovery: discard the failed attempt and run a new one.
        (root / 'killed' / 'result.tmp').unlink()
        print(json.dumps(attempt(root / 'killed', False)), flush=True)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--worker':
        sys.exit(worker(sys.argv[2]))
    main()
