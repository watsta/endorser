class ConversionError(Exception):
    """Exception to raise when conversion fails."""

    def __init__(self, errors: list):
        self.errors = errors
