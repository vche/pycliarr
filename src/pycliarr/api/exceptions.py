class CliArrError(Exception):
    pass


class CliDecodeError(CliArrError):
    pass


class CliServerError(CliArrError):
    def __init__(self, message: str, status_code: int):
        self.status_code = status_code
        super().__init__(message)


class SonarrCliError(CliArrError):
    pass


class RadarrCliError(CliArrError):
    pass
