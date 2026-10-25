# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/golden_retriever
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Test gr module attributes."""

import gr


def test_package_metadata() -> None:
    """Test that gr package exports version and library name."""
    assert gr.LIB_NAME == "golden-retriever"
    assert gr.LIB_VERSION == "0.1.0"
    assert gr.__version__ == "0.1.0"
