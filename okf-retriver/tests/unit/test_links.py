import unittest

from okf_context.parsing.links import extract_links


class LinkTests(unittest.TestCase):
    def test_internal_links_only(self):
        links = extract_links("[Redis](../infra/redis.md) [External](https://example.com)", "services/auth.md")
        self.assertEqual(links, ["infra/redis"])
