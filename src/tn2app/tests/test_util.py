from django.test import TestCase

from ..util import sanitize_comment, PermissiveURLValidator

class UtilTestCase(TestCase):
    def test_sanitize_comment_doesnt_let_evil_through(self):
        self.assertEqual(
            sanitize_comment('<script>evil()</script>'),
            '&lt;script&gt;evil()&lt;/script&gt;'
        )

    def test_sanitize_comment_linkifies_with_blank_and_nofollow(self):
        self.assertEqual(
            sanitize_comment('http://www.example.com'),
            '<a href="http://www.example.com" rel="nofollow" target="_blank">http://www.example.com</a>'
        )

    def test_PermissiveURLValidator(self):
        # Don't raise a validation error
        PermissiveURLValidator()('http://essais_erreurs.eklablog.com/')

