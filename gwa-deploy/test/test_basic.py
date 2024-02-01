import unittest
import util


class TestUtil(unittest.TestCase):
    def test_list_to_dict(self):
        test_cases = [
            [["project_bgd", "env_dev"], {"project": "bgd", "env": "dev"}],
            [["project_bgd", "env_dev", "nounderscoretag"], {"project": "bgd", "env": "dev"}],
            [["nounderscoretag"], {}],
            [["key_value", "key_value"], "ExceptionExpected"],
        ]
        for test_case in test_cases:
            if test_case[1] == "ExceptionExpected":  # Special logic for an expected Exception
                is_success = None
                try:
                    util.tags_as_dict(test_case[0])
                    is_success = False  # No exception but one was expected
                except:  # noqa: E722
                    is_success = True  # Exception - as expected

                if is_success:
                    self.assertTrue(True)
                else:
                    self.assertTrue(False, f"The test case {test_case[0]} did not throw an Exception")
            else:
                self.assertTrue(util.tags_as_dict(test_case[0]) == test_case[1])


if __name__ == "__main__":
    unittest.main()
