#!/usr/bin/env python
# encoding: utf-8
"""

Date:
    Wed Jan  7 00:18:56 AEDT 2015

Author:
    Kian Ho <hui.kian.ho@gmail.com>

Description:
    ...

Usage:
    tests.py

Options:
    ...

"""
    
import unittest
import os
import pprint

import mdwf_lib.mdwf_functions



class Tests(unittest.TestCase):
    """
    """

    def test_get_current_job_list(self):
        test_dir = "Main1"

        job_list = mdwf_lib.mdwf_functions.get_curr_job_list(test_dir)

        pprint.pprint(job_list)

        return


def main():
    """Run the tests.

    """

    unittest.main()


if __name__ == '__main__':
    main()
