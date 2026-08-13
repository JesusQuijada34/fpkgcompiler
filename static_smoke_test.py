import ast
from pathlib import Path

source = Path("fpkgcompiler.py").read_text(encoding="utf-8")
ast.parse(source)
assert "AlphaCube es una distribución de código fuente universal" in source
assert 'package_name = f"{self.metadata[\'publisher\']}.{self.metadata[\'app\']}.{self.metadata[\'version\']}.AlphaCube"' in source
assert 'if target_platform != "AlphaCube":' in source
assert 'No se instalará automáticamente ni se usará sudo' in source
assert 'self._copy_package_files(package_path, "AlphaCube")' in source
print("FPKGCOMPILER_ALPHACUBE_STATIC_CHECK_OK")
