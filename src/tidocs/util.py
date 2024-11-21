import importlib.resources


def get_reference_doc() -> str:
    """Get the path to the reference doc in the package."""
    try:
        files = importlib.resources.files("tidocs")
        reference_path = files / "resources" / "custom-pdf-reference.docx"
        return str(reference_path)
    except Exception as e:
        raise RuntimeError(f"Failed to locate reference doc: {str(e)}")
