from .metrics import metrics


def score(provider) -> float:
    """
    Compute a score for a provider.

    Higher score = higher priority.
    Unavailable providers always return -1.
    """

    if not provider.available():
        return -1.0

    m = metrics.get(provider.name)

    # Start with a perfect score
    score = 50.0 if m.requests == 0 else 100.0

    # Penalize failures
    score -= m.failures * 5

    # Penalize retries
    score -= m.retries * 2

    # Penalize latency
    score -= m.latency() * 10

    # Penalize poor success rate once we have history
    if m.requests > 0:
        success_rate = m.successes / m.requests
        score *= success_rate

    return max(score, 0.0)
