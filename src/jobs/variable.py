"""
Helper functionality for interacting with the internal mars variable service.
"""

import os
import uuid


def get_mars_var(name: str) -> str:
    """
    Fetch the value of the given variable using the internal MARS variable
    service.

    We cannot import the internal mars Python package outside the scope of a
    MARS job, and even if we could, we would have to mock out the internal
    variable API. In cases where it is not possible to import the mars package
    (i.e. local development / testing), this function will attempt to fetch
    the value from environment variables or else return a dummy value.
    :param name:
        The variable name to fetch.
    :return:
        The value of the variable. If the variable does not exist in the MARS
        variable repository, an exception is thrown.
    """
    try:
        from mars.variable import Variable

        return Variable().pull(name)
    except ImportError:
        return os.environ.get(name, f"mars-dummy-var-{uuid.uuid4()}")
