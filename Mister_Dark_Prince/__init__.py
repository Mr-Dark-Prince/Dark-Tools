from os.path import dirname, basename, isfile, join
import glob

Mister_Dark_Prince = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [
    basename(f)[:-3] for f in Mister_Dark_Prince if isfile(f) and not f.endswith("__init__.py")
]
