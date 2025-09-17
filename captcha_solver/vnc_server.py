import os
import subprocess

class VNCServer:
    def __init__(self, password_path = "/etc/x11vnc.pass"):
        self._proc = None
        self._password_path = password_path

    async def start(self) -> None:
        vnc_command = [
            "x11vnc",
            "-rfbauth",
            self._password_path,
            "-forever",
            "-xkb",
            "-shared",
            "-o",
            "/var/log/x11vnc.log",
            "-wait",
            "50"
        ]
        print("Starting VNC server...")
        self._proc = subprocess.Popen(vnc_command)

    def stop(self) -> None:
        if self._proc and self._proc.poll() is None:
            print("Stopping VNC server...")
            try:
                self._proc.terminate()
                self._proc.wait(timeout = 5)

            except subprocess.TimeoutExpired:
                print("VNC server did not terminate gracefully, forcing kill.")
                self._proc.kill()

            finally:
                self._proc = None
        else:
            print("VNC server process is not running or has already stopped.")
