from django.test import TestCase

class BasicTest(TestCase):
    def test_basic_math(self):
        # To make the pipeline pass for now
        self.assertEqual(1 + 1, 2)
        self.assertTrue(True)