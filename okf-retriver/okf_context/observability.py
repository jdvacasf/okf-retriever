import logging


logger = logging.getLogger("okf_context")

REASONING_OUTCOMES = {
    "success",
    "no_evidence",
    "provider_not_configured",
    "provider_failure",
    "invalid_provider_output",
}


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level)


def record_reasoning_outcome(outcome: str, elapsed_seconds: float) -> None:
    if outcome not in REASONING_OUTCOMES or elapsed_seconds < 0:
        raise ValueError("invalid reasoning diagnostic")
    logger.info("reasoning outcome=%s elapsed_seconds=%.6f", outcome, elapsed_seconds)
