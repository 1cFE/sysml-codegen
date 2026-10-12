"""The run-study bundle holds together: every cross-reference inside it lands somewhere.

The runbook cites the package annex and the study policy by section name, and a project starts
both from the templates that ship beside it. A citation to a section the template lacks is a
step whose facts have nowhere to live, so these tests hold the citations to the templates
(design DD18). They also check what the installer and the tools read from the bundle: the
skill's frontmatter, and the digest shape the record template shows.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from agentic_mbse.cli.installation import frontmatter

from sysml_codegen.study import roots

ASSETS = roots.TOOL_HOME / "sysml_codegen" / "assets"
RUN_STUDY = ASSETS / "skills" / "run-study"
SKILL = RUN_STUDY / "SKILL.md"
RUNBOOK = RUN_STUDY / "runbook.md"
RECORD_TEMPLATE = RUN_STUDY / "record-template.md"
ANNEX_TEMPLATE = RUN_STUDY / "annex-template.md"
POLICY_TEMPLATE = ASSETS / "project_templates" / "STUDY_POLICY.md.template"
#: Where ``install-commands`` writes the policy template in a project (design Appendix D).
POLICY_PATH = "modeling_project/STUDY_POLICY.md"


def _annex_citations(text: str) -> set[str]:
    """The annex sections a text cites, written `` `§ <name>` ``."""
    return set(re.findall(r"`§ ([^`]+)`", text))


def _annex_sections(text: str) -> list[str]:
    return re.findall(r"^## § (.+)$", text, flags=re.M)


def _policy_titles(text: str) -> set[str]:
    """Each numbered policy heading's title, without its grade and date."""
    titles = re.findall(r"^## \d+\. (.+)$", text, flags=re.M)
    return {re.sub(r" — .*$", "", title) for title in titles}


def test_the_skill_frontmatter_parses_as_a_workflow_bundle() -> None:
    """``install-commands --list`` reads the skill through agentic-mbse's own parser."""
    meta, body = frontmatter(SKILL)
    assert meta["name"] == RUN_STUDY.name == "run-study"
    assert meta["metadata"] == {"kind": "workflow"}
    assert meta["user-invocable"] is True
    assert meta["description"].strip() and body.startswith("\n# Run Study")


def test_every_sibling_the_skill_names_ships_and_every_shipped_file_is_named() -> None:
    named = set(re.findall(r"^- \*\*`([\w-]+\.md)`\*\*", SKILL.read_text(), flags=re.M))
    shipped = {path.name for path in RUN_STUDY.iterdir() if path.is_file()} - {SKILL.name}
    assert named == shipped


def test_every_annex_section_the_runbook_reads_is_in_the_template() -> None:
    """And every section the template carries is one the runbook reads: no orphan either way."""
    cited = _annex_citations(RUNBOOK.read_text())
    sections = _annex_sections(ANNEX_TEMPLATE.read_text())
    assert cited == set(sections) == {"Declared ties", "Baseline pin", "Oracle", "Validity masks"}
    assert len(sections) == len(set(sections))


def test_every_annex_line_cites_sections_or_says_none() -> None:
    lines = [line for line in RUNBOOK.read_text().splitlines() if line.startswith("**Annex:**")]
    assert len(lines) == 15, "one Annex line per execute step"
    for line in lines:
        rest = line.removeprefix("**Annex:** ")
        assert rest == "none" or re.fullmatch(r"`§ [^`]+`( and `§ [^`]+`)*", rest), line


def test_the_annex_template_states_the_snapshot_rule_and_the_pieces() -> None:
    text = ANNEX_TEMPLATE.read_text()
    assert "exactly one `*.snapshot.json` beside the models root" in text
    assert "`instance_graph_snapshot.json`, does not match" in text
    pieces = text.split("## Package-owned pieces", 1)[1].split("\n## ", 1)[0]
    pieces_named = (
        "Package", "Manifest", "Axis declaration", "Route", "Oracle", "Snapshot", "Census",
    )
    for piece in pieces_named:
        assert f"\n| {piece} |" in pieces, piece


def test_every_policy_section_the_text_cites_is_in_the_policy_template() -> None:
    """Each ``study policy's § <name>`` must open with a section title the template carries."""
    titles = _policy_titles(POLICY_TEMPLATE.read_text())
    cited: set[str] = set()
    for path in (SKILL, RUNBOOK):
        for rest in re.findall(r"study policy's § (.+)", path.read_text()):
            found = [title for title in titles if rest.startswith(title)]
            assert len(found) == 1, f"{path.name}: no policy section opens {rest[:40]!r}"
            cited.add(found[0])
    assert cited == {"Locations", "Execution routes", "Process sizing"}


def test_the_policy_template_carries_the_project_slots_and_no_verification_rule() -> None:
    titles = _policy_titles(POLICY_TEMPLATE.read_text())
    assert {"Execution routes", "Hypotheses", "Tripwire record", "Locations"} <= titles
    assert not any("Verification" in title or "oracle" in title.lower() for title in titles)


def test_the_skill_and_runbook_name_the_policy_where_the_installer_puts_it() -> None:
    for path in (SKILL, RUNBOOK):
        assert f"`{POLICY_PATH}`" in path.read_text(), path.name


def test_steps_14_and_15_carry_their_check_lines() -> None:
    """The record checks a project runs, since no shipped tool runs them (design DD12)."""
    text = RUNBOOK.read_text()
    step14 = text.split("### 14.", 1)[1].split("### 15.", 1)[0]
    step15 = text.split("### 15.", 1)[1].split("\n---\n", 1)[0]
    assert step14.count("**Check:**") == 1 and step15.count("**Check:**") == 1
    assert step15.count("\npython3 -c ") == 4
    for check in (step14, step15):
        commands = check.split("```bash\n", 1)[1].split("```", 1)[0]
        recorded = commands.replace("<study-id>", "")
        assert "<" not in recorded, "a recorded command must not add a '<'"


def test_a_literal_copy_of_the_record_template_passes_the_placeholder_check(
    tmp_path: Path,
) -> None:
    """An executor who copies the template exactly passes step 15's placeholder Check (audit F3).

    The template says to copy everything above **END OF RECORD**. Its placeholders sit in
    §§ 1–17; the text above § 1 is copied as it stands. With every placeholder replaced, the
    shipped Check, run as the runbook gives it, must print 0. The copied preamble used to hold
    four '<'.
    """
    lines = RECORD_TEMPLATE.read_text().splitlines(keepends=True)
    end = lines.index("**END OF RECORD**\n")
    first = next(i for i, line in enumerate(lines) if line.startswith("## 1."))
    placeholder = re.compile(r"<[^<>\n]+>")
    filled = lines[:first] + [placeholder.sub("filled", line) for line in lines[first:end]]
    (tmp_path / "record.md").write_text("".join(filled))

    step15 = RUNBOOK.read_text().split("### 15.", 1)[1].split("\n---\n", 1)[0]
    commands = step15.split("```bash\n", 1)[1].split("```", 1)[0].splitlines()
    label = next(i for i, line in enumerate(commands) if line.startswith("# 0: no unreplaced"))
    done = subprocess.run(["bash", "-c", commands[label + 1]], cwd=tmp_path,
                          capture_output=True, text=True, check=True)
    assert done.stdout == "0\n"


def _source_digest_blocks(text: str) -> list[str]:
    """Every ``"source_digest": { ... }`` block in the template, braces balanced."""
    blocks = []
    for match in re.finditer(r'"source_digest":\s*\{', text):
        depth, i = 1, match.end()
        while depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        blocks.append(text[match.start() : i])
    return blocks


def test_the_record_template_shows_the_emitted_digest_shape_in_both_places() -> None:
    """Moved from fusion-tea's ``tests/study/test_record_template.py`` at ``b06585709``.

    The tools emit ``{recipe, digest, files[]}``, and the template shows the shape a snapshot
    carries twice: the oracle's digest and the tools' digests. Both must show the file list,
    or a record written from the template omits what says which sources a digest covers.
    """
    blocks = _source_digest_blocks(RECORD_TEMPLATE.read_text())
    assert len(blocks) == 2, [block[:60] for block in blocks]
    for block in blocks:
        assert '"recipe": "tool-source-digest/v1"' in block, block
        assert '"digest"' in block and '"files"' in block, block
        assert '"path"' in block and '"sha256"' in block, block


def test_the_record_template_names_the_post_move_tool_path() -> None:
    assert '{ "path": "sysml_codegen/study/<tool>.py",' in RECORD_TEMPLATE.read_text()
