import win32gui
import win32con
import win32process

import ctypes

psapi = ctypes.windll.psapi
kernel = ctypes.windll.kernel32


def _get_pids_by_basename(basename):
    debug = True
    debug = False

    arr = ctypes.c_ulong * 1024
    lpidProcess = arr()
    cb = ctypes.sizeof(lpidProcess)
    cbNeeded = ctypes.c_ulong()
    hModule = ctypes.c_ulong()
    count = ctypes.c_ulong()
    modname = ctypes.create_unicode_buffer(100)
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010

    # Call Enumprocesses to get hold of process id's
    psapi.EnumProcesses(ctypes.byref(lpidProcess), cb, ctypes.byref(cbNeeded))

    # Number of processes returned
    nReturned = cbNeeded.value // ctypes.sizeof(ctypes.c_ulong())

    if debug:
        print(nReturned)

    pidProcess = [pid for index, pid in enumerate(lpidProcess) if index < nReturned]
    # pidProcess = list([i for i in lpidProcess])[:nReturned]

    pids = []

    if debug:
        module_basenames = []

    for pid in pidProcess:

        # Get handle to the process based on PID
        hProcess = kernel.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid
        )
        if not hProcess:
            continue

        psapi.EnumProcessModules(
            hProcess, ctypes.byref(hModule), ctypes.sizeof(hModule), ctypes.byref(count)
        )
        psapi.GetModuleBaseNameW(hProcess, hModule.value, modname, ctypes.sizeof(modname))
        module_basename = modname.value

        kernel.CloseHandle(hProcess)

        if debug:
            module_basenames.append(module_basename)

        if module_basename != basename:
            continue

        pids.append(pid)

    if debug:
        module_basenames.sort()
        for module_basename in module_basenames:
            print(module_basename)

    return pids


def _get_hwnds_by_pid(pid):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)

    return hwnds


def set_focus(module_basename):
    # print(module_basename)
    pids = _get_pids_by_basename(module_basename)
    print("pids:", pids)
    if not pids:
        return

    hwnds = _get_hwnds_by_pid(pids[0])
    print("hwnds:", hwnds)

    if not hwnds:
        return

    hwnd = hwnds[0]
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)


if __name__ == "__main__":
    set_focus("nvim-qt.exe")
