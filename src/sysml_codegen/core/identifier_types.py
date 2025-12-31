"""Identifier type transformations for ADR-003.

Provides data classes and functions for transforming SysML qualified names
to Python identifiers (module types, file paths, EQNs).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SysMLQualifiedName:
    """Raw qualified name from SysIDE (uses :: separator)."""

    value: str

    @property
    def segments(self) -> list[str]:
        """Split into individual segments (packages + element name)."""
        return self.value.split("::")

    @property
    def package_segments(self) -> list[str]:
        """Get package path segments (everything except last segment)."""
        return self.segments[:-1]

    @property
    def element_name(self) -> str:
        """Get element name (last segment)."""
        return self.segments[-1]


@dataclass(frozen=True)
class ModuleType:
    """TEAx registry key and YAML module_type."""

    value: str

    @classmethod
    def from_sysml(cls, sqn: SysMLQualifiedName) -> "ModuleType":
        """Create ModuleType from SysML qualified name."""
        namespace = ".".join(s.lower() for s in sqn.package_segments)
        class_name = f"{sqn.element_name}Module"
        return cls(f"{namespace}.{class_name}" if namespace else class_name)


@dataclass(frozen=True)
class PythonModulePath:
    """Generated Python module location."""

    directory: str
    filename: str

    @property
    def full_path(self) -> str:
        """Get full relative path including .py extension."""
        if self.directory:
            return f"{self.directory}/{self.filename}.py"
        return f"{self.filename}.py"

    @property
    def import_path(self) -> str:
        """Get Python import path (dotted, no .py extension)."""
        if self.directory:
            return f"{self.directory.replace('/', '.')}.{self.filename}"
        return self.filename

    @property
    def impl_import_path(self) -> str:
        """Get Python import path for handwritten implementation."""
        if self.directory:
            return f"{self.directory.replace('/', '.')}.{self.filename}_impl"
        return f"{self.filename}_impl"

    @classmethod
    def from_sysml(cls, sqn: SysMLQualifiedName) -> "PythonModulePath":
        """Create PythonModulePath from SysML qualified name."""
        directory = "/".join(s.lower() for s in sqn.package_segments)
        return cls(directory, sqn.element_name.lower())


@dataclass(frozen=True)
class ElementQualifiedName:
    """Internal codegen identifier (uses __ separator per ADR-001)."""

    value: str

    @classmethod
    def from_sysml(cls, sqn: SysMLQualifiedName) -> "ElementQualifiedName":
        """Create ElementQualifiedName from SysML qualified name."""
        return cls("__".join(sqn.segments))


def derive_module_type(qualified_name: str) -> str:
    """Transform SysML qualified name to namespaced module_type.

    Args:
        qualified_name: SysML qualified name (e.g., "Package::Element")

    Returns:
        Namespaced module type (e.g., "package.ElementModule")
    """
    sqn = SysMLQualifiedName(qualified_name)
    return ModuleType.from_sysml(sqn).value


def derive_python_path(qualified_name: str) -> str:
    """Transform SysML qualified name to Python file path.

    Args:
        qualified_name: SysML qualified name (e.g., "Package::Element")

    Returns:
        Relative path to Python file (e.g., "package/element.py")
    """
    sqn = SysMLQualifiedName(qualified_name)
    return PythonModulePath.from_sysml(sqn).full_path


__all__ = [
    "SysMLQualifiedName",
    "ModuleType",
    "PythonModulePath",
    "ElementQualifiedName",
    "derive_module_type",
    "derive_python_path",
]
