from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True)
class SandboxResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str


class DockerSandbox:
    """Evaluate descendants in Docker with network disabled and hard resource limits.

    This is defense-in-depth, not a formal security proof. The Docker image must
    already exist locally; the sandbox never pulls images during an evaluation.
    """

    def __init__(self, image: str = "python:3.12-slim", timeout_s: int = 120) -> None:
        self.image = image
        self.timeout_s = timeout_s

    def available(self) -> bool:
        return shutil.which("docker") is not None

    def command(self, workspace: str | Path) -> list[str]:
        root = str(Path(workspace).resolve())
        return [
            "docker", "run", "--rm",
            "--network", "none",
            "--read-only",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--pids-limit", "128",
            "--memory", "512m",
            "--cpus", "1.0",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
            "-e", "PYTHONPATH=/workspace/src",
            "-v", f"{root}:/workspace:ro",
            "-w", "/workspace",
            self.image,
            "python", "-m", "unittest", "discover", "-s", "tests", "-v",
        ]

    def run(self, workspace: str | Path) -> SandboxResult:
        if not self.available():
            raise RuntimeError("Docker is required for Gate-4 candidate execution")
        try:
            proc = subprocess.run(self.command(workspace), capture_output=True, text=True, timeout=self.timeout_s, check=False)
        except subprocess.TimeoutExpired as exc:
            return SandboxResult(False, 124, exc.stdout or "", exc.stderr or "timeout")
        return SandboxResult(proc.returncode == 0, proc.returncode, proc.stdout, proc.stderr)
