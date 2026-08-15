"""Nox sessions for supported Python versions."""

from __future__ import annotations

import nox

PYTHON_VERSIONS = ["3.11", "3.12"]

nox.options.default_venv_backend = "uv"


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite in an isolated uv-backed environment."""
    session.install("-e", ".[dev]")
    session.run("bash", "dev/test_python.sh", external=True)
