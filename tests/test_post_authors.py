import unittest
import yaml
from scripts.normalize_post_authors import AUTHOR, normalize


class AuthorTests(unittest.TestCase):
    def test_missing_blank_wrong_multiline_and_duplicate_authors(self):
        for field in ("", "author:\n", "author: Someone Else\n", '"author": Other\n',
                      "author:\n  name: Other\n  url: https://example.com\n",
                      "author: >\n  Someone Else\n", "author: A\nauthor: B\n"):
            with self.subTest(field=field):
                rest = 'date: 2026-09-22 12:58:00 +0800\ncategories: [EDA, SYN]\n'
                body = '\n## Body\n\nauthor: body text must remain\n'
                result = normalize('---\n' + field + rest + '---' + body)
                self.assertEqual(yaml.safe_load(result.split('---')[1])['author'], AUTHOR)
                self.assertIn(rest, result)
                self.assertTrue(result.endswith('---' + body))
                self.assertEqual(normalize(result), result)

    def test_crlf_and_unicode(self):
        text = '---\r\ntitle: 中文\r\n---\r\n正文\r\n'
        self.assertEqual(normalize(text), '---\r\nauthor: ' + AUTHOR + '\r\ntitle: 中文\r\n---\r\n正文\r\n')

    def test_reject_invalid_input(self):
        for text in ('No front matter', '---\n[not, mapping]\n---\n',
                     '---\nname: &name Other\nauthor: *name\n---\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                normalize(text)
