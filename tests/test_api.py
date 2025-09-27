# -*- coding: utf-8 -*-

from s3vectorm import api


def test():
    _ = api


if __name__ == "__main__":
    from s3vectorm.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3vectorm.api",
        preview=False,
    )
