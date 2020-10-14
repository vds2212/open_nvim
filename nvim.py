import os
import sys
import neovim
import set_focus
import time
import datetime

try:
    import fcntl
except ImportError:
    fcntl = None


NVIM_FOLDER = os.path.abspath(os.path.dirname(sys.argv[0]))
LOCK_PATH = os.path.join(NVIM_FOLDER, "nvim.lock")
SERVERNAME_PATH = os.path.join(NVIM_FOLDER, "nvim.txt")
LOG_PATH = os.path.join(NVIM_FOLDER, "nvim.log")
NEOVIM_PATH = r"bin\nvim-qt.exe"


OS_WIN = False
if 'win32' in sys.platform.lower():
    OS_WIN = True


def nvim():
    now = datetime.datetime.now()
    log("-" * 20)
    log("Today: %s" % now.strftime("%Y/%m/%d %H:%M:%S"))

    si = SingleInstance()
    try:
        if si.is_running:
            log("Error: nvim.py is already running: abort")
            return 2  # Retry later

        servername_path = SERVERNAME_PATH

        if not os.path.isfile(servername_path):
            log("Server-Log: %s not found" % SERVERNAME_PATH)
            log("Start Neovim")
            server_id = start_vim(servername_path)
            return 0

        log("Server-Log: %s found" % SERVERNAME_PATH)

        with open(servername_path, mode="rt") as f:
            line = f.readline()
            server_id = line.strip("\r\n ")
            log("Server-ID: %s" % server_id)

        try:
            log("Open connection")
            nvim = neovim.attach("socket", path=server_id)

        except Exception:
            log("Error: Neovim not found at: %s" % server_id)
            os.remove(servername_path)
            return 0  # Fail

        if len(sys.argv) > 1:
            path = sys.argv[1]
            command = ':e %s' % path
            log("Command: %s" % command)
            try:
                nvim.command(command)

            except Exception as e:
                log("Error: Fail to run: %s" % str(e))

        else:
            log("No file to open")

        nvim.close()
        log("Close connection")

        folder, exe = os.path.split(NEOVIM_PATH)
        set_focus.set_focus(exe)
        log("Set Focus")

        log("Success:")

    finally:
        si.clean_up()

    return 0


def start_vim(servername_path):
    """
    Start neovim
    Return the server id if found
    Return None otherwise
    """
    if len(sys.argv) > 1:
        os.system(r'start "%s" "%s"' % (NEOVIM_PATH, sys.argv[1]))
    else:
        os.system(r'start "%s"' % NEOVIM_PATH)

    # Wait that SERVERNAME_PATH is created before continuing
    i = 0
    while True:
        if os.path.isfile(servername_path):
            break

        i += 0.5
        time.sleep(0.5)
        if i < 10:
            continue

        # Stop waiting after 10 seconds
        log("Error: Fail to find the Server-Log")
        return None

    server_id = None
    with open(servername_path) as f:
        server_id = f.readline()
        server_id = server_id.rstrip("\r\n")
        if server_id != "":
            log("Success: Server ID: %s" % server_id)
        else:
            log("Error: Invalid Server ID")

    return server_id


class SingleInstance:
    def __init__(self):
        self.fh = None
        self.is_running = False
        self.do_magic()

    def do_magic(self):
        if OS_WIN:
            try:
                if os.path.exists(LOCK_PATH):
                    os.unlink(LOCK_PATH)
                self.fh = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            except EnvironmentError as err:
                if err.errno == 13:
                    self.is_running = True
                else:
                    raise
        else:
            try:
                self.fh = open(LOCK_PATH, 'w')
                fcntl.lockf(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except EnvironmentError:
                if self.fh:
                    self.is_running = True
                else:
                    raise

    def clean_up(self):
        # this is not really needed
        try:
            if OS_WIN and self.fh:
                self.fh.close()
                os.unlink(LOCK_PATH)
            elif self.fh:
                fcntl.lockf(self.fh, fcntl.LOCK_UN)
                self.fh.close()  # ???
                os.unlink(LOCK_PATH)

        except Exception:
            pass


def main():
    try:
        print("nvim.py")
        while True:
            ret = nvim()
            if ret != 2:
                break

            time.sleep(0.1)

        message = "Return %d" % ret
        sys.exit(ret)

    except set_focus.FocusException as e:
        message = str(e)
        sys.exit(0)

    except Exception as e:
        message = "Exception: %s, %s" % (str(type(e)), repr(e))
        log(message)
        sys.exit(0)

    finally:
        print("Finally")
        pass


def log(message):
    with open(LOG_PATH, mode="at") as g:
        print(message)
        g.write(message + "\n")


if __name__ == "__main__":
    main()
