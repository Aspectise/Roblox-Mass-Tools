import pkgutil
import importlib

__all__ = []
for module_info in pkgutil.iter_modules(__path__):
    __all__.append(module_info.name)
    module = importlib.import_module(f"{__name__}.{module_info.name}")
    globals()[module_info.name] = module