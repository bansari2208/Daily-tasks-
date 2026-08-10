import time
from contextlib import contextmanager


@contextmanager
def timer(label: str = "Operation"):
    """
    A lightweight context manager to measure and log the execution time of a code block.

    Example usage:
        with timer("Batch Processing"):
            # code to measure
    """
    start_time = time.time()
    print(f"[{label}] Started...")
    try:
        yield
    finally:
        elapsed_ms = (time.time() - start_time) * 1000.0
        print(f"[{label}] Finished in {elapsed_ms:.2f} ms")

