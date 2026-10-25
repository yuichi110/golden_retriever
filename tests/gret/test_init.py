# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/golden_retriever
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Test gret module attributes."""

import gret


def test_package_metadata() -> None:
    """Test that gret package exports version and library name."""
    assert gret.LIB_NAME == "gret"
    assert gret.LIB_VERSION == "0.1.0"
    assert gret.__version__ == "0.1.0"
