import importlib.metadata
import importlib.resources


def read_version() -> str:
    try:
        return importlib.metadata.version(__package__ or "tidocs")
    except importlib.metadata.PackageNotFoundError:
        return (
            importlib.resources.files("tidocs").joinpath("VERSION").read_text().strip()
        )


__version__ = read_version()
