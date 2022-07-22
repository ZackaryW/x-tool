from dataclasses import dataclass
import dataclasses

@dataclass(init=False)
class XToolContext:
    """
    a cache store for persistent data

    it is intended to be used as an object with direct manipulation of variables

    class derived from XToolContext must be dataclass
    """

    def __init__(self, **kwargs) -> None:
        """
        when __init__ class is called, 

        all dataclass fields are initialized with default values if no keyword arguments are given

        """
        fields = dataclasses.fields(self)
        for field in fields:
            if field.name not in kwargs:
                setattr(self, field.name, field.default)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, key, default=None):
        """
        standard getter for the class

        (getattr is used)

        Args:
            key (str):  the key to get
            default (optional): the default value to return if key is not found
        """

        return getattr(self, key, default)
