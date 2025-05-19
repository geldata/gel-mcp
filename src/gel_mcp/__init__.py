from . import server
import asyncio


def main() -> None:
    """Main entry point for the package."""
    asyncio.run(server.main())
    return None


# Optionally expose other important items at package level
__all__ = ["main", "server"]
