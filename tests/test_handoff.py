"""Handoff protocol: ledger status, package build, readback verification and ingest (no network)."""
import json, shutil, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path

R = Path(__file__).resolve().parents[1]
TOOL = R / "tools/workflow/handoff.py"
LEDGER = R / "productions/2026/MI/STATE_LEDGER.json"


def run(*a):
    return subprocess.run([sys.executable, str(TOOL), *a], capture_output=True, text=True, encoding="utf-8", cwd=R)


def readback(pid, tasks, answers, extra=""):
    return "READBACK\npackage_id: %s\nrole: draft only\ntasks: %s\nnot_mine: MI-A2\nanswers:\n%s\nmissing: none\nblocking_questions: none\nplan: x\n%s" % (
        pid, tasks, "\n".join(f"  {i}. {a}" for i, a in enumerate(answers, 1)), extra)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.saved = LEDGER.read_bytes()
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        LEDGER.write_bytes(self.saved)
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(R / "productions/2026/MI/inbox", ignore_errors=True)

    def test_status_has_no_errors(self):
        r = run("status", "MI")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("MI-A1", r.stdout)

    def test_status_catches_missing_evidence(self):
        led = json.loads(self.saved)
        led["stages"][0]["evidence"] = ["data/elections/MI/does_not_exist.json"]
        LEDGER.write_text(json.dumps(led), encoding="utf-8")
        r = run("status", "MI")
        self.assertEqual(r.returncode, 1)
        self.assertIn("evidence is missing", r.stdout)

    def test_template_initializes_a_clean_state(self):
        tpl = (R / "docs/production/templates/state/STATE_LEDGER.template.json").read_text(encoding="utf-8")
        raw = tpl.replace("{{ST}}", "ZZ").replace("{{NAME}}", "Zed").replace("{{YEAR}}", "2026").replace("{{TODAY}}", "2026-10-28")
        led = json.loads(raw)
        self.assertEqual(led["state"], "ZZ")
        self.assertEqual({s["id"] for s in led["stages"]} >= {"roster", "tip_join", "scout", "publish", "video"}, True)
        for lane in led["lanes"].values():
            self.assertEqual(lane["tasks"], [])

    def test_build_readback_and_ingest(self):
        r = run("build", "MI", "--lane", "all", "--mode", "fresh")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        pid = next(l.split()[1] for l in r.stdout.splitlines() if l.startswith("package "))
        H = R / "productions/2026/MI/handoff" / pid
        z = zipfile.ZipFile(H / f"{pid}.zip")
        names = z.namelist()
        for need in ("HANDSHAKE.md", "TASKS.md", "STATE_STATUS.md", "manifest.json", "standards/00_READ_ORDER.md", "inputs/MI-A1/STORY_BRIEF.md"):
            self.assertIn(f"{pid}/{need}", names)
        self.assertFalse(any("ANSWER_KEY" in n for n in names))
        key = json.loads((H / "ANSWER_KEY.json").read_text(encoding="utf-8"))
        self.assertIn("MI-A1", key["tasks_assigned"])
        self.assertIn("MI-A2", key["tasks_excluded"])
        # readback: pass
        good = [{"articles": "Withdrawn", "images": "x"}[c["lane"]] if False else " ".join(c["expect_any"]) for c in key["checks"]]
        f = self.tmp / "ok.txt"
        f.write_text(readback(pid, "MI-A1, MI-A1-HERO", good), encoding="utf-8")
        self.assertEqual(run("verify-readback", "MI", pid, str(f)).returncode, 0)
        # readback: claims the withdrawn task and the wrong package
        f2 = self.tmp / "bad.txt"
        f2.write_text(readback("MI-all-OLD", "MI-A1, MI-A2", good), encoding="utf-8")
        r2 = run("verify-readback", "MI", pid, str(f2))
        self.assertEqual(r2.returncode, 1)
        self.assertIn("excluded task MI-A2", r2.stdout)
        self.assertIn("expected", r2.stdout)
        # ingest: incomplete
        d = self.tmp / "ret"
        d.mkdir()
        (d / "MI-A1_NOTES.md").write_text(pid, encoding="utf-8")
        self.assertEqual(run("ingest", "MI", str(d), "--package-id", pid).returncode, 1)
        # ingest: complete
        (d / "MI-A1_CLAIMS.csv").write_text("claim,text_location,source_url,source_date,checked_date,status,type,evidence_ref\nx,lede,u,d,,NEW,number,e\n", encoding="utf-8")
        (d / "MI-A1_story.html").write_text("---\ntitle: t\ndek: d\nformat: Reported Feature\nhero: mi-duggan\nhero_alt: a\nhero_title: h\nhero_text: x\n---\n<!--openfile\nquestion: q\n-->\n<p>Text.[[s:1]] <a href=\"https://theissuesparty.org/candidates/GOV-MI-BENSON\">B</a></p>\n<!--sources\n1 | s\n-->\n<!--corrections\n-->\n", encoding="utf-8")
        for rel in ("masters/mi-duggan.jpg", "web/mi-duggan.jpg", "README.md", "manifest.json"):
            p = d / rel
            p.parent.mkdir(exist_ok=True)
            p.write_bytes(b"x")
        r3 = run("ingest", "MI", str(d), "--package-id", pid)
        self.assertEqual(r3.returncode, 0, r3.stdout + r3.stderr)
        self.assertIn("COMPLETE", r3.stdout)
        led = json.loads(LEDGER.read_text(encoding="utf-8"))
        st = {t["id"]: t["status"] for t in led["lanes"]["articles"]["tasks"]}
        self.assertEqual(st["MI-A1"], "returned")

    def test_package_has_no_secret(self):
        r = run("build", "MI", "--lane", "claude")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        kick = next((R / "productions/2026/MI/handoff").glob("MI-claude-*/CLAUDE_KICKOFF.md"))
        t = kick.read_text(encoding="utf-8")
        self.assertIn("handoff.py status MI", t)
        self.assertNotIn("FEC_API_KEY=", t)


if __name__ == "__main__":
    unittest.main()
