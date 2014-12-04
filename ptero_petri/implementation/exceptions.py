class PetriBackendError(Exception):
    pass


class InvalidColor(PetriBackendError):
    pass


class InvalidPlace(PetriBackendError):
    pass
