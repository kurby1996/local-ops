# -*- coding: utf-8 -*-
"""Windows 平台适配（仅标准库）。由 server.py 在 win32 上按需导入。"""

from __future__ import annotations

import ctypes
import os
import re
import socket
import struct
import subprocess
import sys
import time
from ctypes import wintypes

CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NEW_CONSOLE = 0x00000010
CREATE_NO_WINDOW = 0x08000000
CREATE_UNICODE_ENVIRONMENT = 0x00000400
DETACHED_PROCESS = 0x00000008
CREATE_BREAKAWAY_FROM_JOB = 0x01000000

PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_VM_READ = 0x0010
STILL_ACTIVE = 259
TOKEN_QUERY = 0x0008
TokenUser = 1

TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

JobObjectBasicProcessIdList = 3
JOB_OBJECT_QUERY = 0x0004
JOB_OBJECT_ASSIGN_PROCESS = 0x0001
JOB_OBJECT_TERMINATE = 0x0008
JOB_OBJECT_SET_ATTRIBUTES = 0x0002
JOB_OBJECT_ALL_ACCESS = 0x1F001F

AF_INET = 2
AF_INET6 = 23
TCP_TABLE_OWNER_PID_LISTENER = 3
ERROR_INSUFFICIENT_BUFFER = 122
NO_ERROR = 0
MIB_TCP_STATE_LISTEN = 2

ProcessBasicInformation = 0
ProcessCommandLineInformation = 60
STATUS_INFO_LENGTH_MISMATCH = 0xC0000004
STATUS_SUCCESS = 0

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
ntdll = ctypes.WinDLL("ntdll")
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)

kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
kernel32.GetExitCodeProcess.restype = wintypes.BOOL
kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
kernel32.TerminateProcess.restype = wintypes.BOOL
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.GetProcessTimes.argtypes = [
    wintypes.HANDLE, ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME),
    ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME)]
kernel32.GetProcessTimes.restype = wintypes.BOOL
kernel32.ReadProcessMemory.argtypes = [
    wintypes.HANDLE, wintypes.LPCVOID, wintypes.LPVOID, ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t)]
kernel32.ReadProcessMemory.restype = wintypes.BOOL
kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
kernel32.CreateJobObjectW.restype = wintypes.HANDLE
kernel32.OpenJobObjectW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.OpenJobObjectW.restype = wintypes.HANDLE
kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
kernel32.TerminateJobObject.restype = wintypes.BOOL
kernel32.QueryInformationJobObject.argtypes = [
    wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD)]
kernel32.QueryInformationJobObject.restype = wintypes.BOOL
kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL

ntdll.NtQueryInformationProcess.argtypes = [
    wintypes.HANDLE, ctypes.c_uint, wintypes.LPVOID, wintypes.ULONG,
    ctypes.POINTER(wintypes.ULONG)]
ntdll.NtQueryInformationProcess.restype = ctypes.c_long

advapi32.OpenProcessToken.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
advapi32.OpenProcessToken.restype = wintypes.BOOL
advapi32.GetTokenInformation.argtypes = [
    wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD)]
advapi32.GetTokenInformation.restype = wintypes.BOOL
advapi32.ConvertSidToStringSidW.argtypes = [wintypes.LPVOID, ctypes.POINTER(wintypes.LPWSTR)]
advapi32.ConvertSidToStringSidW.restype = wintypes.BOOL
kernel32.LocalFree.argtypes = [wintypes.HANDLE]
kernel32.LocalFree.restype = wintypes.HANDLE

psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD]
psapi.GetProcessMemoryInfo.restype = wintypes.BOOL

iphlpapi = ctypes.WinDLL("iphlpapi", use_last_error=True)
iphlpapi.GetExtendedTcpTable.argtypes = [
    wintypes.LPVOID, ctypes.POINTER(wintypes.DWORD), wintypes.BOOL,
    wintypes.ULONG, wintypes.ULONG, wintypes.ULONG]
iphlpapi.GetExtendedTcpTable.restype = wintypes.DWORD


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_uint64),
        ("ullAvailPhys", ctypes.c_uint64),
        ("ullTotalPageFile", ctypes.c_uint64),
        ("ullAvailPageFile", ctypes.c_uint64),
        ("ullTotalVirtual", ctypes.c_uint64),
        ("ullAvailVirtual", ctypes.c_uint64),
        ("ullAvailExtendedVirtual", ctypes.c_uint64),
    ]


class PROCESS_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("Reserved1", ctypes.c_void_p),
        ("PebBaseAddress", ctypes.c_void_p),
        ("Reserved2", ctypes.c_void_p * 2),
        ("UniqueProcessId", ctypes.c_void_p),
        ("Reserved3", ctypes.c_void_p),
    ]


class MIB_TCPROW_OWNER_PID(ctypes.Structure):
    _fields_ = [
        ("dwState", wintypes.DWORD),
        ("dwLocalAddr", wintypes.DWORD),
        ("dwLocalPort", wintypes.DWORD),
        ("dwRemoteAddr", wintypes.DWORD),
        ("dwRemotePort", wintypes.DWORD),
        ("dwOwningPid", wintypes.DWORD),
    ]


class MIB_TCP6ROW_OWNER_PID(ctypes.Structure):
    _fields_ = [
        ("ucLocalAddr", ctypes.c_ubyte * 16),
        ("dwLocalScopeId", wintypes.DWORD),
        ("dwLocalPort", wintypes.DWORD),
        ("ucRemoteAddr", ctypes.c_ubyte * 16),
        ("dwRemoteScopeId", wintypes.DWORD),
        ("dwRemotePort", wintypes.DWORD),
        ("dwState", wintypes.DWORD),
        ("dwOwningPid", wintypes.DWORD),
    ]


kernel32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32FirstW.restype = wintypes.BOOL
kernel32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32NextW.restype = wintypes.BOOL

_IS_64 = ctypes.sizeof(ctypes.c_void_p) == 8
_JOB_HANDLES = {}
_CPU_SAMPLE = {}
_SELF_SID = None
_TOTAL_PHYS = None
CURRENT_USER_UID = 1
OTHER_USER_UID = 0


def _close(handle):
    if handle:
        kernel32.CloseHandle(handle)


def _open_process(pid, access):
    handle = kernel32.OpenProcess(access, False, int(pid))
    return handle or None


def _filetime_to_unix(ft):
    ticks = (ft.dwHighDateTime << 32) | ft.dwLowDateTime
    if ticks == 0:
        return 0
    return ticks / 10_000_000 - 11644473600


def _filetime_to_seconds(ft):
    ticks = (ft.dwHighDateTime << 32) | ft.dwLowDateTime
    return ticks / 10_000_000


def _total_phys():
    global _TOTAL_PHYS
    if _TOTAL_PHYS:
        return _TOTAL_PHYS
    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    if kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        _TOTAL_PHYS = max(int(status.ullTotalPhys), 1)
    else:
        _TOTAL_PHYS = 8 * 1024 * 1024 * 1024
    return _TOTAL_PHYS


def _sid_from_handle(process):
    token = wintypes.HANDLE()
    if not advapi32.OpenProcessToken(process, TOKEN_QUERY, ctypes.byref(token)):
        return None
    try:
        needed = wintypes.DWORD(0)
        advapi32.GetTokenInformation(token, TokenUser, None, 0, ctypes.byref(needed))
        if needed.value == 0:
            return None
        buf = ctypes.create_string_buffer(needed.value)
        if not advapi32.GetTokenInformation(
                token, TokenUser, buf, needed, ctypes.byref(needed)):
            return None
        sid = ctypes.cast(buf, ctypes.POINTER(ctypes.c_void_p))[0]
        text = wintypes.LPWSTR()
        if not advapi32.ConvertSidToStringSidW(sid, ctypes.byref(text)):
            return None
        try:
            return text.value
        finally:
            kernel32.LocalFree(text)
    finally:
        _close(token)


def current_user_sid():
    global _SELF_SID
    if _SELF_SID is not None:
        return _SELF_SID
    handle = kernel32.GetCurrentProcess()
    _SELF_SID = _sid_from_handle(handle) or ""
    return _SELF_SID


def process_sid(pid):
    handle = _open_process(pid, PROCESS_QUERY_LIMITED_INFORMATION)
    if not handle:
        return None
    try:
        return _sid_from_handle(handle)
    finally:
        _close(handle)


def process_uid(pid):
    sid = process_sid(pid)
    if sid is None:
        return None
    return CURRENT_USER_UID if sid == current_user_sid() else OTHER_USER_UID


def pid_alive(pid):
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    handle = _open_process(pid, PROCESS_QUERY_LIMITED_INFORMATION)
    if not handle:
        return ctypes.get_last_error() == 5
    try:
        code = wintypes.DWORD()
        if kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
            return code.value == STILL_ACTIVE
        return True
    finally:
        _close(handle)


def enumerate_processes():
    """→ {pid: {ppid, name}}。"""
    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if not snap or snap == INVALID_HANDLE_VALUE:
        return {}
    result = {}
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        if not kernel32.Process32FirstW(snap, ctypes.byref(entry)):
            return {}
        while True:
            pid = int(entry.th32ProcessID)
            result[pid] = {
                "ppid": int(entry.th32ParentProcessID),
                "name": entry.szExeFile or "",
            }
            if not kernel32.Process32NextW(snap, ctypes.byref(entry)):
                break
        return result
    finally:
        _close(snap)


def _query_image_path(handle):
    size = wintypes.DWORD(32768)
    buf = ctypes.create_unicode_buffer(size.value)
    if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
        return buf.value
    return ""


def _query_command_line(handle):
    retlen = wintypes.ULONG(0)
    status = ntdll.NtQueryInformationProcess(
        handle, ProcessCommandLineInformation, None, 0, ctypes.byref(retlen))
    status = status & 0xFFFFFFFF
    if status != STATUS_INFO_LENGTH_MISMATCH or retlen.value == 0:
        return ""
    buf = ctypes.create_string_buffer(retlen.value)
    status = ntdll.NtQueryInformationProcess(
        handle, ProcessCommandLineInformation, buf, retlen, ctypes.byref(retlen))
    if (status & 0xFFFFFFFF) != STATUS_SUCCESS:
        return ""
    if retlen.value < 8:
        return ""
    length = struct.unpack_from("<H", buf, 0)[0]
    if _IS_64:
        ptr = struct.unpack_from("<Q", buf, 8)[0]
        header = 16
    else:
        ptr = struct.unpack_from("<I", buf, 4)[0]
        header = 8
    buf_addr = ctypes.addressof(buf)
    if length == 0:
        return ""
    if ptr and buf_addr <= ptr < buf_addr + retlen.value:
        offset = ptr - buf_addr
    else:
        offset = header
    end = min(offset + length, retlen.value)
    try:
        return buf.raw[offset:end].decode("utf-16-le", errors="replace")
    except Exception:
        return ""


def _read_memory(handle, address, size):
    if not address or size <= 0:
        return None
    buf = ctypes.create_string_buffer(size)
    read = ctypes.c_size_t(0)
    if not kernel32.ReadProcessMemory(
            handle, ctypes.c_void_p(address), buf, size, ctypes.byref(read)):
        return None
    return buf.raw[:read.value]


def _unicode_from_remote(handle, length, buffer_addr):
    if not buffer_addr or length <= 0:
        return ""
    data = _read_memory(handle, buffer_addr, length)
    if not data:
        return ""
    try:
        return data.decode("utf-16-le", errors="replace")
    except Exception:
        return ""


def _query_cwd(handle):
    info = PROCESS_BASIC_INFORMATION()
    retlen = wintypes.ULONG(0)
    status = ntdll.NtQueryInformationProcess(
        handle, ProcessBasicInformation, ctypes.byref(info),
        ctypes.sizeof(info), ctypes.byref(retlen))
    if (status & 0xFFFFFFFF) != STATUS_SUCCESS or not info.PebBaseAddress:
        return ""
    params_off = 0x20 if _IS_64 else 0x10
    raw = _read_memory(handle, info.PebBaseAddress + params_off,
                       ctypes.sizeof(ctypes.c_void_p))
    if not raw:
        return ""
    params = struct.unpack_from("<Q" if _IS_64 else "<I", raw, 0)[0]
    if not params:
        return ""
    # RTL_USER_PROCESS_PARAMETERS.CurrentDirectory.DosPath
    dos_off = 0x38 if _IS_64 else 0x24
    ust_size = 16 if _IS_64 else 8
    ust = _read_memory(handle, params + dos_off, ust_size)
    if not ust or len(ust) < ust_size:
        return ""
    length = struct.unpack_from("<H", ust, 0)[0]
    buf_addr = struct.unpack_from("<Q" if _IS_64 else "<I", ust, 8 if _IS_64 else 4)[0]
    return _unicode_from_remote(handle, length, buf_addr).rstrip("\\\0")


def _cpu_percent(pid, cpu_seconds):
    now = time.monotonic()
    prev = _CPU_SAMPLE.get(pid)
    _CPU_SAMPLE[pid] = (now, cpu_seconds)
    if not prev:
        return 0.0
    dt = now - prev[0]
    if dt <= 0:
        return 0.0
    ncpu = os.cpu_count() or 1
    return max(0.0, (cpu_seconds - prev[1]) / dt / ncpu * 100.0)


def _fill_details(pid, name=""):
    access = (PROCESS_QUERY_INFORMATION | PROCESS_QUERY_LIMITED_INFORMATION
              | PROCESS_VM_READ)
    handle = _open_process(pid, access)
    if not handle:
        handle = _open_process(pid, PROCESS_QUERY_LIMITED_INFORMATION)
    entry = {
        "uid": OTHER_USER_UID,
        "comm": name,
        "args": name,
        "cpu": 0.0,
        "mem": 0.0,
        "etime": 0,
        "cwd": "",
    }
    if not handle:
        return entry
    try:
        image = _query_image_path(handle)
        if image:
            entry["comm"] = image
        args = _query_command_line(handle)
        entry["args"] = args or image or name
        sid = _sid_from_handle(handle)
        if sid == current_user_sid():
            entry["uid"] = CURRENT_USER_UID
        creation = wintypes.FILETIME()
        exit_t = wintypes.FILETIME()
        kernel = wintypes.FILETIME()
        user = wintypes.FILETIME()
        if kernel32.GetProcessTimes(
                handle, ctypes.byref(creation), ctypes.byref(exit_t),
                ctypes.byref(kernel), ctypes.byref(user)):
            created = _filetime_to_unix(creation)
            if created > 0:
                entry["etime"] = max(0, int(time.time() - created))
            cpu_sec = _filetime_to_seconds(kernel) + _filetime_to_seconds(user)
            entry["cpu"] = round(_cpu_percent(pid, cpu_sec), 1)
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(counters)
        if psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            entry["mem"] = round(
                counters.WorkingSetSize / _total_phys() * 100.0, 1)
        cwd = _query_cwd(handle)
        if cwd:
            entry["cwd"] = cwd
        return entry
    finally:
        _close(handle)


def ps_snapshot(pids=None, with_uid=True):
    table = enumerate_processes()
    if pids is None:
        wanted = list(table)
    else:
        wanted = [int(p) for p in pids]
    snap = {}
    for pid in wanted:
        info = table.get(pid, {})
        details = _fill_details(pid, info.get("name") or "")
        if not with_uid:
            details.pop("uid", None)
        snap[pid] = details
    return snap


def process_cwds(pids):
    result = {}
    for pid in {int(p) for p in pids}:
        access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
        handle = _open_process(pid, access)
        if not handle:
            continue
        try:
            cwd = _query_cwd(handle)
            if cwd:
                result[pid] = cwd
        finally:
            _close(handle)
    return result


def _fill_command_line(pid, name=""):
    access = (PROCESS_QUERY_INFORMATION | PROCESS_QUERY_LIMITED_INFORMATION
              | PROCESS_VM_READ)
    handle = _open_process(pid, access)
    if not handle:
        handle = _open_process(pid, PROCESS_QUERY_LIMITED_INFORMATION)
    if not handle:
        return name
    try:
        args = _query_command_line(handle)
        if args:
            return args
        return _query_image_path(handle) or name
    finally:
        _close(handle)


def origin_snapshot():
    table = enumerate_processes()
    result = {}
    for pid, info in table.items():
        name = info.get("name") or ""
        result[pid] = (info.get("ppid") or 0, _fill_command_line(pid, name))
    return result


def pgid_members_map():
    table = enumerate_processes()
    children = {}
    for pid, info in table.items():
        children.setdefault(info.get("ppid") or 0, []).append(pid)

    def collect(root):
        out = [root]
        stack = [root]
        seen = {root}
        while stack:
            cur = stack.pop()
            for child in children.get(cur, []):
                if child not in seen:
                    seen.add(child)
                    out.append(child)
                    stack.append(child)
        return out

    return {pid: collect(pid) for pid in table}


def job_name(token):
    return "Local\\console-run-" + str(token)


def create_named_job(token):
    handle = kernel32.CreateJobObjectW(None, job_name(token))
    if not handle:
        return None
    _JOB_HANDLES[token] = handle
    return handle


def open_named_job(token):
    cached = _JOB_HANDLES.get(token)
    if cached:
        return cached
    access = JOB_OBJECT_QUERY | JOB_OBJECT_TERMINATE | JOB_OBJECT_ASSIGN_PROCESS
    handle = kernel32.OpenJobObjectW(access, False, job_name(token))
    if handle:
        _JOB_HANDLES[token] = handle
    return handle or None


def assign_process_to_job(job, pid):
    if not job:
        return False
    handle = _open_process(pid, PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_TERMINATE | 0x0800)
    if not handle:
        handle = _open_process(pid, PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_TERMINATE)
    if not handle:
        return False
    try:
        return bool(kernel32.AssignProcessToJobObject(job, handle))
    finally:
        _close(handle)


def job_pids(token):
    if not token:
        return set()
    handle = open_named_job(token)
    if not handle:
        return set()
    count = 64
    while count <= 4096:
        class _List(ctypes.Structure):
            _fields_ = [
                ("NumberOfAssignedProcesses", wintypes.DWORD),
                ("NumberOfProcessIdsInList", wintypes.DWORD),
                ("ProcessIdList", ctypes.c_size_t * count),
            ]
        buf = _List()
        retlen = wintypes.DWORD(0)
        ok = kernel32.QueryInformationJobObject(
            handle, JobObjectBasicProcessIdList, ctypes.byref(buf),
            ctypes.sizeof(buf), ctypes.byref(retlen))
        if ok:
            n = min(buf.NumberOfProcessIdsInList, count)
            return {int(buf.ProcessIdList[i]) for i in range(n) if buf.ProcessIdList[i]}
        if ctypes.get_last_error() != ERROR_INSUFFICIENT_BUFFER:
            assigned = int(buf.NumberOfAssignedProcesses or 0)
            if assigned > count:
                count = assigned + 8
                continue
            return set()
        count *= 2
    return set()


def terminate_job(token, exit_code=1):
    handle = open_named_job(token)
    if not handle:
        return False
    return bool(kernel32.TerminateJobObject(handle, exit_code))


def _hidden_run(args, timeout=10):
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    return subprocess.run(
        args, capture_output=True, text=True, timeout=timeout,
        startupinfo=startup, creationflags=CREATE_NO_WINDOW,
        errors="replace")


def stop_process_tree(pid, force=False):
    """结束进程树。Windows 控制台进程没有可靠的 SIGTERM，统一 TerminateProcess。"""
    pid = int(pid)
    table = enumerate_processes()
    children = {}
    for proc_id, info in table.items():
        children.setdefault(info.get("ppid") or 0, []).append(proc_id)
    stack = [pid]
    seen = []
    seen_set = set()
    while stack:
        current = stack.pop()
        if current in seen_set:
            continue
        seen_set.add(current)
        seen.append(current)
        stack.extend(children.get(current, []))
    killed_any = False
    last_error = None
    for current in reversed(seen):
        handle = _open_process(current, PROCESS_TERMINATE)
        if not handle:
            if not pid_alive(current):
                continue
            last_error = "没有权限停止 PID %d" % current
            continue
        try:
            if kernel32.TerminateProcess(handle, 1):
                killed_any = True
            else:
                last_error = "结束 PID %d 失败" % current
        finally:
            _close(handle)
    if killed_any or not pid_alive(pid):
        return True, None
    return False, last_error or "停止受控进程组失败"


def kill_process(pid, force):
    pid = int(pid)
    handle = _open_process(pid, PROCESS_TERMINATE | PROCESS_QUERY_LIMITED_INFORMATION)
    if not handle:
        if not pid_alive(pid):
            return False, "进程不存在"
        return False, "没有权限结束该进程"
    try:
        if kernel32.TerminateProcess(handle, 1 if force else 15):
            return True, None
        return False, "结束失败"
    finally:
        _close(handle)


def _ntohs_port(value):
    return socket.ntohs(int(value) & 0xFFFF)


def _ipv4_host(dw):
    packed = struct.pack("<I", int(dw) & 0xFFFFFFFF)
    host = socket.inet_ntoa(packed)
    if host == "0.0.0.0":
        return "*"
    return host


def _ipv6_host(octets):
    raw = bytes(octets)
    if raw == b"\x00" * 16:
        return "*"
    if raw == b"\x00" * 15 + b"\x01":
        return "::1"
    try:
        return socket.inet_ntop(socket.AF_INET6, raw)
    except OSError:
        return ""


def _tcp_table(family, row_cls):
    size = wintypes.DWORD(0)
    code = iphlpapi.GetExtendedTcpTable(
        None, ctypes.byref(size), False, family,
        TCP_TABLE_OWNER_PID_LISTENER, 0)
    if code not in (NO_ERROR, ERROR_INSUFFICIENT_BUFFER):
        return []
    buf = ctypes.create_string_buffer(size.value)

    class _Table(ctypes.Structure):
        _fields_ = [
            ("dwNumEntries", wintypes.DWORD),
            ("table", row_cls * max(1, (size.value // max(ctypes.sizeof(row_cls), 1)))),
        ]

    code = iphlpapi.GetExtendedTcpTable(
        buf, ctypes.byref(size), False, family,
        TCP_TABLE_OWNER_PID_LISTENER, 0)
    if code != NO_ERROR:
        return []
    table = ctypes.cast(buf, ctypes.POINTER(_Table)).contents
    return [table.table[i] for i in range(table.dwNumEntries)]


def scan_listeners():
    found = {}
    try:
        for row in _tcp_table(AF_INET, MIB_TCPROW_OWNER_PID):
            if int(row.dwState) not in (0, MIB_TCP_STATE_LISTEN):
                # TCP_TABLE_OWNER_PID_LISTENER already filters; keep all rows.
                pass
            port = _ntohs_port(row.dwLocalPort)
            pid = int(row.dwOwningPid)
            if port <= 0:
                continue
            found.setdefault((pid, port), set()).add(_ipv4_host(row.dwLocalAddr))
        for row in _tcp_table(AF_INET6, MIB_TCP6ROW_OWNER_PID):
            port = _ntohs_port(row.dwLocalPort)
            pid = int(row.dwOwningPid)
            if port <= 0:
                continue
            found.setdefault((pid, port), set()).add(_ipv6_host(row.ucLocalAddr))
        if found:
            return found
    except Exception:
        pass
    return parse_netstat_listeners(_netstat_output())


def _netstat_output():
    try:
        r = _hidden_run(["netstat", "-ano", "-p", "TCP"], timeout=8)
        return r.stdout or ""
    except Exception:
        return ""


def parse_netstat_listeners(out):
    """解析 ``netstat -ano`` 的 LISTENING 行。"""
    found = {}
    for line in (out or "").splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        if parts[0].upper() != "TCP":
            continue
        state = parts[3].upper()
        if state != "LISTENING":
            continue
        try:
            pid = int(parts[4])
        except ValueError:
            continue
        host, port = split_netstat_addr(parts[1])
        if port is None:
            continue
        found.setdefault((pid, port), set()).add(host)
    return found


def split_netstat_addr(value):
    value = (value or "").strip()
    if not value:
        return "", None
    if value.startswith("["):
        match = re.match(r"^\[([^\]]+)\]:(\d+)$", value)
        if not match:
            return "", None
        host, port = match.group(1), int(match.group(2))
    else:
        # IPv6 without brackets: [::]:80 already handled; 0.0.0.0:80 / [::1]:80
        if value.count(":") > 1:
            host, sep, port_s = value.rpartition(":")
            if not sep or not port_s.isdigit():
                return "", None
            host = host.strip("[]")
            port = int(port_s)
        else:
            host, sep, port_s = value.rpartition(":")
            if not sep or not port_s.isdigit():
                return "", None
            port = int(port_s)
    if host in ("0.0.0.0", "::"):
        host = "*"
    return host, port


def acquire_instance_lock(path, pid):
    import msvcrt
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    lock_file = os.fdopen(fd, "r+", encoding="ascii")
    try:
        lock_file.seek(0)
        if lock_file.read(1) == "":
            lock_file.write("0")
            lock_file.flush()
        lock_file.seek(0)
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        lock_file.close()
        return None
    try:
        lock_file.seek(0)
        lock_file.truncate()
        lock_file.write("%d\n" % int(pid))
        lock_file.flush()
        os.fsync(lock_file.fileno())
    except OSError:
        try:
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        lock_file.close()
        raise
    return lock_file


def release_instance_lock(lock_file):
    if lock_file is None:
        return
    try:
        import msvcrt
        lock_file.seek(0)
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
    except OSError:
        pass
    finally:
        lock_file.close()


def pick_path(what):
    try:
        return _pick_tk(what)
    except Exception:
        return _pick_powershell(what)


def _pick_tk(what):
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass
    if what == "dir":
        path = filedialog.askdirectory(title="选择工作目录", parent=root)
    else:
        path = filedialog.askopenfilename(
            title="选择批处理脚本",
            filetypes=[
                ("脚本", "*.py *.ps1 *.bat *.cmd *.js *.mjs *.cjs *.sh"),
                ("全部文件", "*.*"),
            ],
            parent=root)
    root.destroy()
    if not path:
        return None, True
    return os.path.normpath(path), False


def _pick_powershell(what):
    if what == "dir":
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$d = New-Object System.Windows.Forms.FolderBrowserDialog; "
            "$d.Description = '选择工作目录'; "
            "$d.ShowNewFolderButton = $true; "
            "if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { "
            "[Console]::Out.Write($d.SelectedPath); exit 0 }; exit 2"
        )
    else:
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$d = New-Object System.Windows.Forms.OpenFileDialog; "
            "$d.Title = '选择批处理脚本'; "
            "$d.Filter = 'Scripts|*.py;*.ps1;*.bat;*.cmd;*.js;*.mjs;*.cjs;*.sh|All|*.*'; "
            "if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { "
            "[Console]::Out.Write($d.FileName); exit 0 }; exit 2"
        )
    try:
        r = subprocess.run(
            ["powershell", "-STA", "-NoProfile", "-WindowStyle", "Hidden",
             "-Command", script],
            capture_output=True, text=True, timeout=180, errors="replace",
            creationflags=CREATE_NO_WINDOW)
    except Exception:
        return None, False
    if r.returncode == 2:
        return None, True
    if r.returncode != 0:
        return None, False
    path = (r.stdout or "").strip().strip('"')
    return (os.path.normpath(path) if path else None), False


def launcher_dialog(message):
    try:
        return _launcher_dialog_tk(message)
    except Exception:
        return _launcher_dialog_ps(message)


def _launcher_dialog_tk(message):
    import tkinter as tk
    result = {"value": None}
    root = tk.Tk()
    root.title("总控台")
    root.resizable(False, False)
    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass
    frame = tk.Frame(root, padx=18, pady=16)
    frame.pack()
    tk.Label(frame, text=message, justify="left", wraplength=420).pack(anchor="w")
    row = tk.Frame(frame)
    row.pack(fill="x", pady=(14, 0))

    def choose(value):
        result["value"] = value
        root.destroy()

    tk.Button(row, text="打开控制台", width=12, command=lambda: choose("打开控制台")).pack(side="right", padx=4)
    tk.Button(row, text="重新启动", width=10, command=lambda: choose("重新启动")).pack(side="right", padx=4)
    tk.Button(row, text="取消", width=8, command=lambda: choose(None)).pack(side="right", padx=4)
    root.protocol("WM_DELETE_WINDOW", lambda: choose(None))
    root.mainloop()
    return result["value"]


def _launcher_dialog_ps(message):
    safe = (message or "").replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "$r = [System.Windows.Forms.MessageBox]::Show('%s','总控台',"
        "'YesNoCancel','Information'); "
        "if ($r -eq 'Yes') { '打开控制台' } "
        "elseif ($r -eq 'No') { '重新启动' }"
    ) % safe
    try:
        r = subprocess.run(
            ["powershell", "-STA", "-NoProfile", "-WindowStyle", "Hidden",
             "-Command", script],
            capture_output=True, text=True, timeout=180, errors="replace",
            creationflags=CREATE_NO_WINDOW)
    except Exception:
        return None
    return (r.stdout or "").strip() or None


def launcher_alert(message):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
        except tk.TclError:
            pass
        messagebox.showerror("总控台", message, parent=root)
        root.destroy()
        return
    except Exception:
        pass
    safe = (message or "").replace("'", "''")
    try:
        subprocess.run(
            ["powershell", "-STA", "-NoProfile", "-WindowStyle", "Hidden",
             "-Command",
             "Add-Type -AssemblyName System.Windows.Forms; "
             "[System.Windows.Forms.MessageBox]::Show('%s','总控台','OK','Error')" % safe],
            capture_output=True, timeout=30, creationflags=CREATE_NO_WINDOW)
    except Exception:
        pass


def popen_creationflags(hidden=True, interactive=False):
    """Build CreateProcess flags for launched apps.

    interactive=True opens a real console window (CREATE_NEW_CONSOLE) so
    scripts can accept keyboard input. That mode is mutually exclusive with
    CREATE_NO_WINDOW.
    """
    flags = CREATE_NEW_PROCESS_GROUP | CREATE_UNICODE_ENVIRONMENT
    if interactive:
        flags |= CREATE_NEW_CONSOLE
    elif hidden:
        flags |= CREATE_NO_WINDOW
    return flags


def popen_startupinfo(show=False):
    """Optional STARTUPINFO; show=True forces the new window visible (SW_SHOWNORMAL)."""
    if not show:
        return None
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = 1  # SW_SHOWNORMAL
    return info


def detached_creationflags(breakaway=False):
    flags = (CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
             | CREATE_UNICODE_ENVIRONMENT | CREATE_NO_WINDOW)
    if breakaway:
        flags |= CREATE_BREAKAWAY_FROM_JOB
    return flags
