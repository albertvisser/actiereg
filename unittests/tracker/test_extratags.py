"""unittests for ./tracker/templatetags/extratags.py
"""
import os
import pytest
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'actiereg.settings')
django.setup()
import pytest
from tracker.templatetags import extratags as testee


def test_return_me():
    """unittest for extratags.return_me
    """
    assert testee.return_me('x') == 'x'


def test_trim_at(monkeypatch, capsys):
    """unittest for extratags.trim_at
    """
    def mock_escape(text):
        """stub
        """
        print(f'called conditional_escape on `{text}`')
        return f'**{text}**'
    def mock_me(text):
        """stub
        """
        print(f'called return_me on `{text}`')
        return text
    def mock_mark(text):
        """stub
        """
        print(f'called mark_safe on `{text}`')
        return f'>>{text}<<'
    monkeypatch.setattr(testee, 'conditional_escape', mock_escape)
    monkeypatch.setattr(testee, 'return_me', mock_me)
    monkeypatch.setattr(testee, 'mark_safe', mock_mark)
    assert testee.trim_at('hello world', 10) == '>>hello worl...<<'
    assert capsys.readouterr().out == ('called return_me on `hello worl...`\n'
                                       'called mark_safe on `hello worl...`\n')
    assert testee.trim_at('hello world', 10, True) == '>>**hello worl...**<<'
    assert capsys.readouterr().out == ('called conditional_escape on `hello worl...`\n'
                                       'called mark_safe on `**hello worl...**`\n')
    assert testee.trim_at('hello world', 30) == '>>hello world<<'
    assert capsys.readouterr().out == ('called return_me on `hello world`\n'
                                       'called mark_safe on `hello world`\n')
    assert testee.trim_at('hello world', 30, True) == '>>**hello world**<<'
    assert capsys.readouterr().out == ('called conditional_escape on `hello world`\n'
                                       'called mark_safe on `**hello world**`\n')

