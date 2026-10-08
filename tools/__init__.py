# tools/__init__.py — автообнаружение инструментов
import os
import importlib

TOOLS = []
FUNCTIONS = {}

_dir = os.path.dirname(__file__)

for filename in sorted(os.listdir(_dir)):
    if not filename.endswith(".py"):
        continue
    if filename.startswith("_"):
        continue
    module_name = filename[:-3]
    try:
        module = importlib.import_module(f"tools.{module_name}")
    except Exception as e:
        print(f"[tools] Не загружен {module_name}: {e}")
        continue
    if hasattr(module, "TOOLS"):
        TOOLS.extend(module.TOOLS)
    if hasattr(module, "FUNCTIONS"):
        FUNCTIONS.update(module.FUNCTIONS)
    print(f"[tools] Подключён: {module_name}")
