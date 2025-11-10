import sys
from pathlib import Path
print("cwd:", Path.cwd())
print("sys.path[0]:", sys.path[0])
try:
    import usuarios.users as mod
    print("usuarios.users import OK")
    print("names:", [n for n in dir(mod) if not n.startswith('_')])
except Exception as e:
    print("IMPORT ERROR:", type(e).__name__, e)