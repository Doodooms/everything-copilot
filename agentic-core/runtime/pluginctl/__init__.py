"""Deterministic, local lifecycle control plane for managed Expertise Packs."""

from .controller import PluginController
from .models import (
    ActiveSet,
    EffectiveProfile,
    ManagedEffectiveIR,
    PluginControlError,
    TrustedRegistry,
    TrustedSource,
)

__all__ = [
    "ActiveSet",
    "EffectiveProfile",
    "ManagedEffectiveIR",
    "PluginControlError",
    "PluginController",
    "TrustedRegistry",
    "TrustedSource",
]
