"""Register FreeDF in Windows: file association + Open With context menu.

Run as administrator for system-wide registration, or as normal user
for current-user-only registration.

Usage:
    python scripts/register_windows.py install
    python scripts/register_windows.py uninstall
"""

from __future__ import annotations

import shutil
import sys
import winreg

APP_NAME = "FreeDF"
APP_ID = "FreeDF.PDF.Editor"
PROG_ID = "FreeDF.pdf"
EXTENSION = ".pdf"


def _find_freedf_exe() -> str:
    """Find the freedf.exe entry point."""
    path = shutil.which("freedf")
    if path:
        return path
    # Fallback: check common pip install locations
    import site

    for scripts_dir in [
        site.getusersitepackages().replace("site-packages", "Scripts"),
        *[p.replace("site-packages", "Scripts") for p in site.getsitepackages()],
    ]:
        candidate = f"{scripts_dir}\\freedf.exe"
        import os

        if os.path.exists(candidate):
            return candidate
    print("ERROR: freedf.exe not found. Install FreeDF first: pip install freedf")
    sys.exit(1)


def install() -> None:
    """Register FreeDF in Windows registry."""
    exe_path = _find_freedf_exe()
    print(f"Found freedf at: {exe_path}")

    # 1. Register the application ProgID
    # HKCU\Software\Classes\FreeDF.pdf
    key_path = f"Software\\Classes\\{PROG_ID}"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "PDF Document (FreeDF)")

    # Shell\Open\Command
    cmd_path = f"{key_path}\\shell\\open\\command"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_path) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{exe_path}" "%1"')

    # Default icon (use the exe icon)
    icon_path = f"{key_path}\\DefaultIcon"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, icon_path) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"{exe_path},0")

    # 2. Register under Applications
    # HKCU\Software\Classes\Applications\freedf.exe
    app_path = "Software\\Classes\\Applications\\freedf.exe"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, app_path) as key:
        winreg.SetValueEx(key, "FriendlyAppName", 0, winreg.REG_SZ, APP_NAME)

    app_cmd = f"{app_path}\\shell\\open\\command"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, app_cmd) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{exe_path}" "%1"')

    # SupportedTypes
    types_path = f"{app_path}\\SupportedTypes"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, types_path) as key:
        winreg.SetValueEx(key, EXTENSION, 0, winreg.REG_SZ, "")

    # 3. Add to "Open With" list for .pdf
    # HKCU\Software\Classes\.pdf\OpenWithProgids
    ow_path = f"Software\\Classes\\{EXTENSION}\\OpenWithProgids"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, ow_path) as key:
        winreg.SetValueEx(key, PROG_ID, 0, winreg.REG_SZ, "")

    # 4. Register in RegisteredApplications
    reg_apps = "Software\\RegisteredApplications"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_apps) as key:
        winreg.SetValueEx(
            key,
            APP_NAME,
            0,
            winreg.REG_SZ,
            f"Software\\Classes\\{PROG_ID}\\Capabilities",
        )

    # 5. Capabilities
    cap_path = f"Software\\Classes\\{PROG_ID}\\Capabilities"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cap_path) as key:
        winreg.SetValueEx(key, "ApplicationName", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(
            key,
            "ApplicationDescription",
            0,
            winreg.REG_SZ,
            "Free, open-source PDF editor",
        )

    cap_fa = f"{cap_path}\\FileAssociations"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cap_fa) as key:
        winreg.SetValueEx(key, EXTENSION, 0, winreg.REG_SZ, PROG_ID)

    # Notify Windows that file associations changed
    try:
        import ctypes

        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)  # type: ignore[union-attr]
    except Exception:
        pass

    print(f"\n{APP_NAME} registered successfully!")
    print(f"  Executable: {exe_path}")
    print(f"  You can now right-click a .pdf -> 'Open with' -> {APP_NAME}")
    print("  Or run: freedf document.pdf")


def uninstall() -> None:
    """Remove FreeDF from Windows registry."""

    def _delete_key_tree(root: int, path: str) -> None:
        try:
            winreg.DeleteKey(root, path)
        except FileNotFoundError:
            pass
        except OSError:
            # Has subkeys, delete recursively
            try:
                with winreg.OpenKey(root, path) as key:
                    while True:
                        try:
                            subkey = winreg.EnumKey(key, 0)
                            _delete_key_tree(root, f"{path}\\{subkey}")
                        except OSError:
                            break
                winreg.DeleteKey(root, path)
            except FileNotFoundError:
                pass

    hkcu = winreg.HKEY_CURRENT_USER
    _delete_key_tree(hkcu, f"Software\\Classes\\{PROG_ID}")
    _delete_key_tree(hkcu, "Software\\Classes\\Applications\\freedf.exe")

    # Remove from OpenWithProgids
    try:
        with winreg.OpenKey(
            hkcu,
            f"Software\\Classes\\{EXTENSION}\\OpenWithProgids",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.DeleteValue(key, PROG_ID)
    except FileNotFoundError:
        pass

    # Remove from RegisteredApplications
    try:
        with winreg.OpenKey(
            hkcu, "Software\\RegisteredApplications", 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, APP_NAME)
    except FileNotFoundError:
        pass

    try:
        import ctypes

        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)  # type: ignore[union-attr]
    except Exception:
        pass

    print(f"{APP_NAME} unregistered from Windows.")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("install", "uninstall"):
        print("Usage: python scripts/register_windows.py install|uninstall")
        sys.exit(1)

    if sys.argv[1] == "install":
        install()
    else:
        uninstall()


if __name__ == "__main__":
    main()
