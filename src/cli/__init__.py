"""CLI entrypoints for Ingestion Engine.

Expose small wrapper functions so scripts can call into importable code
instead of executing package-relative logic at top-level. This makes
it trivial for tests to import functionality without executing scripts.
"""

from . import coordinator

__all__ = ["coordinator"]
