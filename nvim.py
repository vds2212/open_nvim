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

LOCK_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "nvim.lock")

SERVERNAME_PATH = "nvim.txt"

OS_WIN = False
if 'win32' in sys.platform.lower():
    OS_WIN = True


def main():
    now = datetime.datetime.now()
    with open("nvim.log", mode="at") as g:
        log(g, "-" * 20)
        log(g, "Today: %s" % now.strftime("%Y/%m/%d %H:%M:%S"))

        si = SingleInstance()
        try:
            if si.is_running:
                log(g, "Error: nvim.py is already running: abort")
                return 2  # Retry later

            # time.sleep(2)
            servername_path = SERVERNAME_PATH

            if not os.path.isfile(servername_path):
                log(g, "Server-Log: %s not found" % SERVERNAME_PATH)
                log(g, "Start Neovim")
                server_id = start_vim(servername_path)
                if server_id is not None:
                    log(g, "Success: Server ID: %s" % server_id)
                    return 0
                else:
                    log(g, "Error: Fail to find the Server-Log")
                    return 0

            log(g, "Server-Log: %s found" % SERVERNAME_PATH)

            with open(servername_path, mode="rt") as f:
                line = f.readline()
                server_id = line.strip("\r\n ")
                log(g, "Server-ID: %s" % server_id)

            try:
                log(g, "Open connection")
                nvim = neovim.attach("socket", path=server_id)

            except Exception:
                log(g, "Error: Neovim not found at: %s" % server_id)
                os.remove(servername_path)
                return 0  # Fail

            if len(sys.argv) > 1:
                path = sys.argv[1]
                command = ':e %s' % path
                log(g, "Command: %s" % command)
                try:
                    nvim.command(command)

                except Exception as e:
                    log(g, "Error: Fail to run: %s" % str(e))

            else:
                log(g, "No file to open")

            nvim.close()
            log(g, "Close connection")

            set_focus.set_focus("nvim-qt.exe")
            log(g, "Set Focus")

            log(g, "Success:")

        finally:
            si.clean_up()
            # log(g, "Unlock")

        return 0


def start_vim(servername_path):
    """
    Start neovim
    Return the server id if found
    Return None otherwise
    """
    if len(sys.argv) > 1:
        os.system(r'start bin\nvim-qt.exe "%s"' % sys.argv[1])
    else:
        os.system(r'start bin\nvim-qt.exe')

    # Wait that SERVERNAME_PATH is created before continuing
    i = 0
    while True:
        if os.path.isfile(servername_path):
            with open(servername_path) as f:
                server_id = f.readline()
                server_id = server_id.rstrip("\r\n")
                if server_id != "":
                    return server_id
        i += 0.5
        time.sleep(0.5)
        if i < 10:
            continue

        break

    return None


def log(g, message):
    print(message)
    g.write(message + "\n")


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
            # logger.exception(err)
            pass


if __name__ == "__main__":
    try:
        print("nvim.py")
        while True:
            ret = main()
            if ret != 2:
                break

            time.sleep(0.1)

        message = "Return %d" % ret
        with open("nvim.log", mode="at") as g:
            print(message)
            g.write(message + "\n")
        sys.exit(ret)

    except set_focus.FocusException as e:
        message = str(e)
        with open("nvim.log", mode="at") as g:
            print(message)
            g.write(message + "\n")
        sys.exit(0)

    except Exception as e:
        message = "Exception: %s, %s" % (str(type(e)), repr(e))
        with open("nvim.log", mode="at") as g:
            print(message)
            g.write(message + "\n")
        # raise e
        sys.exit(0)

    finally:
        print("Finally")
        pass
