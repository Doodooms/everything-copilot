from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType

from .errors import RegistryError
from .ir import PackReference, PackSource


class LocalPackRegistry:
    """Immutable index of locally available pack sources; it performs no installation."""

    def __init__(
        self,
        packs: Iterable[PackSource],
        *,
        known_agents: set[str] | frozenset[str] | None = None,
    ):
        indexed: dict[PackReference, PackSource] = {}
        for pack in packs:
            reference = pack.reference
            if reference in indexed:
                raise RegistryError(
                    f"duplicate local pack source for {reference.id}@{reference.version}"
                )
            indexed[reference] = pack
        self._packs: Mapping[PackReference, PackSource] = MappingProxyType(
            dict(sorted(indexed.items()))
        )
        providers: dict[str, list[PackReference]] = {}
        for reference, pack in self._packs.items():
            for capability in pack.ir.capabilities:
                providers.setdefault(capability.id, []).append(reference)
        self._providers: Mapping[str, tuple[PackReference, ...]] = MappingProxyType(
            {
                capability: tuple(sorted(references))
                for capability, references in sorted(providers.items())
            }
        )
        if known_agents is None:
            known_agents = frozenset().union(
                *(pack.known_agents for pack in self._packs.values())
            )
        self.agent_ids = frozenset(known_agents)

    @property
    def references(self) -> tuple[PackReference, ...]:
        return tuple(self._packs)

    def get(self, reference: PackReference) -> PackSource:
        try:
            return self._packs[reference]
        except KeyError as exc:
            raise RegistryError(
                f"pack source is not registered: {reference.id}@{reference.version}"
            ) from exc

    def providers_for(self, capability: str) -> tuple[PackReference, ...]:
        return self._providers.get(capability, ())
