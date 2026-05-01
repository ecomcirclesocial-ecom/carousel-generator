import json
import shutil
import subprocess
from pathlib import Path

from config import CLAUDE_TIMEOUT


class ClaudeCLIError(Exception):
    pass


def ensure_available() -> str:
    path = shutil.which("claude")
    if not path:
        raise ClaudeCLIError(
            "El binario 'claude' no está en PATH. "
            "Instala Claude Code o agrégalo al PATH."
        )
    return path


def query(prompt: str, model: str | None = None) -> str:
    ensure_available()
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=CLAUDE_TIMEOUT,
    )
    if proc.returncode != 0:
        raise ClaudeCLIError(
            f"claude CLI falló (exit {proc.returncode}):\n{proc.stderr}"
        )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise ClaudeCLIError(f"Salida no-JSON de claude:\n{proc.stdout}") from e
    if data.get("is_error"):
        raise ClaudeCLIError(f"claude reportó error: {data.get('result')}")
    return data.get("result", "")


def query_json(prompt: str, model: str | None = None) -> dict:
    raw = query(prompt, model=model)
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        raw = "\n".join(lines).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(raw[start : end + 1])
        raise ClaudeCLIError(f"Respuesta no parseable como JSON:\n{raw}") from e
