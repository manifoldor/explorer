import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from explorer import parse_trending, github_trending_top10
import httpx


def card(i):
    return f'''<article class="Box-row"><h2><a href="/owner/repo{i}">owner / repo{i}</a></h2>
    <p>A &amp; B</p><span itemprop="programmingLanguage">Python</span>
    <a href="/owner/repo{i}/stargazers">1,234</a><a href="/owner/repo{i}/forks">56</a>
    <span>123 stars today</span></article>'''


class ParserTests(unittest.TestCase):
    def test_top10_order_numbers_and_entities(self):
        result = parse_trending(''.join(card(i) for i in range(12)))
        self.assertEqual(len(result), 10)
        self.assertEqual(result[-1]['repository'], 'owner/repo9')
        self.assertEqual(result[0]['stars'], 1234)
        self.assertEqual(result[0]['stars_today'], 123)
        self.assertEqual(result[0]['description'], 'A & B')

    def test_missing_is_null(self):
        result = parse_trending('<article class="Box-row"><h2><a href="/a/b">a/b</a></h2></article>')
        self.assertIsNone(result[0]['stars'])
        self.assertIsNone(result[0]['stars_today'])

    def test_invalid_page_and_duplicate_fail(self):
        for html in ['<html>Rate limited</html>', card(1) + card(1),
                     '<article class="Box-row"><h2>Missing link</h2></article>']:
            with self.assertRaises(ValueError):
                parse_trending(html)

    def test_readme_failure_preserves_partial_ranking(self):
        async def fake_fetch(client, url, accept='text/html'):
            if '/trending' in url:
                return card(1)
            raise httpx.ConnectError('unavailable')
        with patch('explorer.fetch_text', side_effect=fake_fetch):
            result = asyncio.run(github_trending_top10())
        self.assertTrue(result['partial'])
        self.assertEqual(result['projects'][0]['rank'], 1)
        self.assertEqual(len(result['warnings']), 2)


if __name__ == '__main__':
    unittest.main()
