from contextlib import contextmanager
import time
import logging


@contextmanager
def timer(operation_name: str):
    """Context manager for timing operations."""
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        logging.info(f"{operation_name} completed in {elapsed_time:.3f} seconds")
