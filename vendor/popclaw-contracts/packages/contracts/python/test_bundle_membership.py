"""The sealed source set ignores exactly one filename, and nothing wider.

A macOS file browser writes `.DS_Store` into any directory it displays, so a
bundle nobody edited stops verifying. The fix is one exact filename. The danger
in that fix is generalising it: a rule that skipped dotfiles, or hidden files,
or anything matching a pattern, would let a real unlisted source file ride into
the bundle unnoticed -- which is the one thing the membership check exists to
catch. Both directions are asserted here, so widening the rule turns a test red
rather than silently weakening the seal.

The end-to-end cases seal and verify a synthetic bundle in a temporary
directory, using the real scripts. They deliberately do not run against this
bundle's own manifest: that would measure whether the seal is currently fresh,
which is `verify-bundle.py`'s job and changes every time anyone edits a file,
rather than measuring the enumeration rule these tests exist to pin.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath

BUNDLE = Path(__file__).resolve().parents[3]
SCRIPTS = BUNDLE / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from bundle_files import member  # noqa: E402


class MembershipRule(unittest.TestCase):
    def test_ds_store_is_not_a_member_at_any_depth(self):
        for path in ['.DS_Store', 'packages/.DS_Store',
                     'packages/contracts/protocol/public-envelope-02/.DS_Store']:
            with self.subTest(path=path):
                self.assertFalse(member(PurePosixPath(path)))

    def test_every_other_unlisted_file_is_still_a_member(self):
        """The rule is one exact filename, not "hidden files are skipped"."""
        for path in ['foo.md', 'packages/foo.md', '.DS_Store.md', 'DS_Store',
                     '.ds_store', 'a/.DS_Store.bak', '.gitignore', '.github/x.yml',
                     '.editorconfig', 'packages/contracts/python/.hidden.py']:
            with self.subTest(path=path):
                self.assertTrue(member(PurePosixPath(path)))

    def test_build_directories_are_still_excluded(self):
        for path in ['node_modules/x', 'target/debug/y', 'dist/z', '.venv/lib/a',
                     '__pycache__/b.pyc', '.git/config', 'CONTRACT-MANIFEST.json']:
            with self.subTest(path=path):
                self.assertFalse(member(PurePosixPath(path)))


class MembershipEndToEnd(unittest.TestCase):
    """Seal and verify a synthetic bundle with the real scripts."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='bundle-membership-'))
        self.addCleanup(shutil.rmtree, self.root, True)
        (self.root / 'scripts').mkdir()
        for name in ['bundle_files.py', 'write-manifest.py', 'verify-bundle.py']:
            shutil.copy2(SCRIPTS / name, self.root / 'scripts' / name)
        (self.root / 'a.txt').write_text('reviewed source\n')
        (self.root / 'sub').mkdir()
        (self.root / 'sub' / 'b.txt').write_text('reviewed source\n')
        self.assertEqual(self.run_script('write-manifest.py').returncode, 0)

    def run_script(self, name):
        return subprocess.run([sys.executable, str(self.root / 'scripts' / name)],
                              capture_output=True, text=True)

    def verify(self):
        return self.run_script('verify-bundle.py')

    def test_a_freshly_sealed_bundle_verifies(self):
        done = self.verify()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_a_stray_ds_store_does_not_break_verification(self):
        for where in [self.root / '.DS_Store', self.root / 'sub' / '.DS_Store']:
            where.write_bytes(b'\x00\x01desktop metadata')
        done = self.verify()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_any_other_stray_file_is_still_a_membership_mismatch(self):
        (self.root / 'sub' / 'stray.md').write_text('not a reviewed source file\n')
        done = self.verify()
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('Source membership mismatch', done.stdout + done.stderr)

    def test_a_stray_dotfile_that_is_not_ds_store_is_still_a_mismatch(self):
        """Guards against relaxing the rule to "hidden files are skipped"."""
        (self.root / '.hidden').write_text('not a reviewed source file\n')
        done = self.verify()
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('Source membership mismatch', done.stdout + done.stderr)

    def test_a_removed_source_file_is_still_a_membership_mismatch(self):
        (self.root / 'sub' / 'b.txt').unlink()
        done = self.verify()
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('Source membership mismatch', done.stdout + done.stderr)


if __name__ == '__main__':
    unittest.main()
