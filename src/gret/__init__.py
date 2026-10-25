# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/golden_retriever
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Golden Retriever - CLI and developer toolkit."""

from __future__ import annotations

from typing import Final

LIB_NAME: Final[str] = "gret"
LIB_VERSION: Final[str] = "0.1.0"

__version__: Final[str] = LIB_VERSION

__all__ = [
    "LIB_NAME",
    "LIB_VERSION",
    "__version__",
]
