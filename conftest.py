from doctest import UnexpectedException

import pytest
from _pytest.doctest import DoctestItem, MultipleDoctestFailures

from ests.exceptions import DatasetNotFoundError


def _needs_dataset(error: BaseException) -> bool:
    # A missing model of spaCy is a missing test dependency and fails as it is
    failures = error.failures if isinstance(error, MultipleDoctestFailures) else [error]
    return any(
        isinstance(failure, UnexpectedException)
        and isinstance(failure.exc_info[1], DatasetNotFoundError)
        and str(failure.exc_info[1]).startswith("The dataset ")
        for failure in failures
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    An example of a docstring that fails because a dataset is not downloaded is skipped
    """
    outcome = yield
    report = outcome.get_result()
    if (
        isinstance(item, DoctestItem)
        and call.when == "call"
        and call.excinfo is not None
        and _needs_dataset(call.excinfo.value)
    ):
        report.outcome = "skipped"
        report.longrepr = (str(item.path), item.reportinfo()[1], "the dataset is not downloaded")
