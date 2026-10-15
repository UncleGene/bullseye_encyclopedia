import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.build_canonical_static_site import copy_resource


class ForumLinksTest(unittest.TestCase):
    def test_resource_redirect_updates_without_mutating_archive_hardlink(self):
        original = b'<meta http-equiv="refresh" content="0;URL=http://bullseyepistol.forumotion.com/">\r\n'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "capture.htm"
            source.write_bytes(original)
            record = {"original": "http://bullseyepistol.com/bulseyel.htm",
                      "file_path": str(source), "sha256": hashlib.sha256(original).hexdigest()}
            target = root / "export" / copy_resource(record, root / "export", {})
            self.assertIn(b"https://www.bullseyeforum.net/", target.read_bytes())
            self.assertNotIn(b"forumotion.com", target.read_bytes())
            self.assertEqual(source.read_bytes(), original)
            self.assertFalse(source.samefile(target))


if __name__ == "__main__":
    unittest.main()
