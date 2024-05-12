def arange(start: float, stop: float, step: float):
    """Yield numbers from start to stop by step, supporting floats and negative steps."""
    current = start
    if step > 0:
        while current < stop:
            yield round(current, 10)  # rounding to maintain precision
            current += step
    elif step < 0:
        while current > stop:
            yield round(current, 10)  # rounding to maintain precision
            current += step
