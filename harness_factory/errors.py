class HarnessFactoryError(RuntimeError):
    """A deterministic harness integration operation failed."""


class CapabilityUnavailableError(HarnessFactoryError):
    """The requested harness capability is unavailable or unknown."""


class RunOwnershipError(HarnessFactoryError):
    """A run or workspace is not owned by the requesting harness."""
