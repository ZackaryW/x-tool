import abc
from functools import cached_property
import inspect
import typing
from xtool.ctx import XToolContext
from xtool.interface import XToolManageInterface
from xtool.exception import XToolNotImplementedException
from xtool.logger import xtoolLogger

class XToolExtension(XToolManageInterface):
    """
    an extension of XToolDB,

    the associated method will be called when XToolDB calls callExtensions

    Args:
        XToolManageInterface : the parent of the extension
    """


    _METHODS_NOT_AVAILABLE = []     # this var stores historic methods that raises not implemented exception
    _IS_INITIALIZED = False         # flag to indicate if initCls has been called

    @classmethod
    def initCls(cls):
        """
        This function will be called when the class is initialized.
        """ 
        if cls._IS_INITIALIZED:
            return

        cls._IS_INITIALIZED = True

    def __init__(self, parent : XToolManageInterface) -> None:
        if isinstance(parent, XToolManageInterface) and not isinstance(parent, XToolExtension):
            pass
        else:
            raise Exception("Parent must not be a XToolExtension")

        self._parent = parent
        self.initCls()
    

    def _actualCallMethod(self, method : str, *args, **kwargs) -> None:
        
        func = getattr(self, method)

        ctx_args, func_args = self._parseCallKwargs(func, **kwargs)

        ctxCls = XToolContext
        if hasattr(self.__class__,f"BIND_{method}"):
            ctxCls = getattr(self.__class__,f"BIND_{method}")
            if not issubclass(ctxCls, XToolContext):
                raise Exception("BIND_ method must be a subclass of XToolContext")

        self.extensionContext = ctxCls(**ctx_args)

        func(**func_args)

    def _parseCallKwargs(self, func :typing.Callable, **kwargs) -> dict:
        # get parameters of func
        inspect_result = inspect.signature(func).parameters

        ctx_args = {}
        func_args = {}
        for key, value in kwargs.items():
            if key in inspect_result:
                func_args[key] = value
            else:
                ctx_args[key] = value
                
        
        return ctx_args, func_args


    def callMethod(self, method : str, **kwargs) -> None:
        if method not in self.methods:
            raise XToolNotImplementedException("Method does not exist")

        self._actualCallMethod(method, **kwargs)

    def callMethodNoRaise(self, method : str, **kwargs) -> None:
        if method not in self.methods:
            xtoolLogger.debug(f"Method does not exist for {self.name}")
            return

        self._actualCallMethod(method, **kwargs)

    @cached_property
    def methods(self):
        return [x for x in dir(self) if not x.startswith("_")]

    @cached_property
    def name(self):
        return self.__class__.__name__

    @property
    def globalContext(self) -> XToolContext:
        return self._parent.globalContext

    @property
    def extensionContext(self) -> XToolContext:
        return self._parent.extensions.get(self)

    @extensionContext.setter
    def extensionContext(self, value : XToolContext) -> None:
        self._parent.extensions[self] = value

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, XToolExtension):
            return False

        if __o._parent is self._parent:
            return True
    
        return False