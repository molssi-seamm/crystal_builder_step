#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `crystal_builder_step` package."""

import pytest  # noqa: F401
import crystal_builder_step  # noqa: F401


def test_construction():
    """Just create an object and test its type."""
    result = crystal_builder_step.CrystalBuilder()
    assert str(type(result)) == (
        "<class 'crystal_builder_step.crystal_builder.CrystalBuilder'>"  # noqa: E501
    )
