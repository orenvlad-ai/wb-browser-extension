#!/usr/bin/env python3
"""Model-free checks for the inert MV3 extension shell."""

import json
import pathlib
import unittest
from html.parser import HTMLParser


ROOT = pathlib.Path(__file__).resolve().parents[1]


class PopupParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.html_language = None
        self.has_main = False
        self.heading_levels = []
        self.stylesheets = []
        self.scripts = []
        self.inline_handlers = []
        self.open_tags = []
        self.badges = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "html":
            self.html_language = attributes.get("lang")
        if tag == "main":
            self.has_main = True
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_levels.append(tag)
        if tag == "link" and attributes.get("rel") == "stylesheet":
            self.stylesheets.append(attributes.get("href"))
        if tag == "script":
            self.scripts.append(attributes.get("src"))
        self.inline_handlers.extend(name for name, _ in attrs if name.startswith("on"))
        if "prototype-badge" in attributes.get("class", "").split():
            self.badges.append(
                {
                    "tag": tag,
                    "attributes": attributes,
                    "inside_interactive": any(
                        open_tag in {"a", "button", "input", "select", "textarea"}
                        for open_tag in self.open_tags
                    ),
                    "text": "",
                }
            )
        self.open_tags.append(tag)

    def handle_endtag(self, tag):
        self.open_tags.pop()

    def handle_data(self, data):
        if self.badges and self.open_tags[-1:] == [self.badges[-1]["tag"]]:
            self.badges[-1]["text"] += data


class MV3ShellTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_manifest_is_minimal_mv3_popup(self):
        self.assertEqual(self.manifest["manifest_version"], 3)
        self.assertEqual(self.manifest["action"]["default_popup"], "popup/popup.html")
        for forbidden_key in (
            "permissions",
            "optional_permissions",
            "host_permissions",
            "optional_host_permissions",
            "background",
            "content_scripts",
            "externally_connectable",
        ):
            self.assertNotIn(forbidden_key, self.manifest)

    def test_popup_assets_are_local_and_accessible(self):
        popup_path = ROOT / self.manifest["action"]["default_popup"]
        parser = PopupParser()
        parser.feed(popup_path.read_text(encoding="utf-8"))

        self.assertTrue(parser.html_language)
        self.assertTrue(parser.has_main)
        self.assertEqual(parser.heading_levels[0], "h1")
        self.assertEqual(parser.scripts, [])
        self.assertEqual(parser.inline_handlers, [])
        self.assertGreaterEqual(len(parser.stylesheets), 1)
        for asset in parser.stylesheets:
            self.assertNotIn("://", asset)
            self.assertTrue((popup_path.parent / asset).is_file())

    def test_popup_has_noninteractive_prototype_badge(self):
        popup_path = ROOT / self.manifest["action"]["default_popup"]
        parser = PopupParser()
        parser.feed(popup_path.read_text(encoding="utf-8"))

        self.assertEqual(len(parser.badges), 1)
        badge = parser.badges[0]
        self.assertEqual(badge["tag"], "span")
        self.assertEqual(badge["text"], "Локальный прототип")
        self.assertFalse(badge["inside_interactive"])
        for forbidden_attribute in ("href", "role", "tabindex", "contenteditable"):
            self.assertNotIn(forbidden_attribute, badge["attributes"])


if __name__ == "__main__":
    unittest.main()
