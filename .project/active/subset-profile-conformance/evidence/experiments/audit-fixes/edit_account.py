"""One-off: the final-audit account edits (two reclassified sites, one new row, line refresh)."""
import csv, io, sys
sys.path.insert(0, '.')
from tests.helpers.subset_profile import site_scan

P = 'tests/expectations/subset_profile/site_account.csv'
raw = open(P, newline='').read()
lines = raw.split('\n')
comments = [l for l in lines if l.startswith('#')]
rows = list(csv.reader(io.StringIO('\n'.join(l for l in lines if not l.startswith('#')))))
header, body = rows[0], rows[1:]
col = {name: i for i, name in enumerate(header)}

A = 'sysml_codegen/elaboration/elaborate.py::_ExactElaborator._index_constraint_associations::coded::SI_EDGE_DANGLING::6'
F = 'sysml_codegen/elaboration/graph.py::InstanceGraph._graph_failure::coded::SI_EDGE_DANGLING::1'
G = 'sysml_codegen/elaboration/graph.py::InstanceGraph._validate_occurrences::coded::SI_EDGE_DANGLING::1'
CYCLES = 'sysml_codegen/elaboration/graph.py::InstanceGraph._validate_producer_cycles::coded::SI_EDGE_DANGLING::1'

def put(row, **kw):
    for k, v in kw.items():
        row[col[k]] = v

by_id = {r[0]: r for r in body}
put(by_id[A],
    role='public_capability',
    reason='elaboration_constraint_definition_unindexed',
    evidence='sysml_codegen/elaboration/elaborate.py:684; case:blocked-predicate-unmapped-code__untyped_assert; case:blocked-predicate-unmapped-code__constraint_check_typed',
    coverage_limitation='the contract refuses both reaching shapes as constraint-predicate/blocked_predicate, but its mapped code is SI_CONSTRAINT_BLOCKED, not this site\'s SI_EDGE_DANGLING (code_unmapped)',
    note='raises when the shared constraint profile names an effective definition UUID that is not a live model ConstraintDefinition. E4 verdict (Item 2a final-audit fix, corrects P6\'s "no model found that reaches it"): public; reached by an untyped asserted constraint (`assert constraint bare;`) and by a constraint typed by the library\'s `Constraints::ConstraintCheck`, where the profile selects a library definition codegen does not index')
put(by_id[F],
    role='snapshot_integrity',
    evidence='sysml_codegen/elaboration/graph.py:1010; sysml_codegen/elaboration/occurrence.py:1018-1048; snapshot/instance_graph.py:1036',
    note='builds SI_EDGE_DANGLING diagnostics for validate()\'s occurrence-record checks (graph.py:594-640). E4 verdict (Item 2a final-audit fix): snapshot integrity. build_occurrence_index (occurrence.py:1018-1048) builds each record\'s key, parent, display and package fields together, so a live model gives consistent records and only a decoded graph can disagree. P6 recorded this row relay plumbing with "no model reached it", which was false: a valid model reached the root-package check, which now builds its own diagnostic (graph.py _validate_occurrences row); no case reaches the checks left here (test_site_reach.py)')
new = [''] * len(header)
put(new,
    site_id=G, file='sysml_codegen/elaboration/graph.py', line='616', channel='coded', code='SI_EDGE_DANGLING',
    disposition='explicit_follow_up', role='public_capability', owner='EXEC-SUBSET-CONTRACT Item 2 (proposed)',
    reason='graph_root_occurrence_package_missing',
    evidence='sysml_codegen/elaboration/graph.py:616; case:candidate-es-002__part_inside_item_usage__attribute_value; sysml_codegen/elaboration/occurrence.py:935-942',
    coverage_limitation='the contract reports the reaching model clear, and the model is valid: the refusal is a suspected generator defect (rg1-recommendations.md RG1-12)',
    note='refuses a root occurrence record with no package display. E4 verdict (Item 2a final-audit fix): public; reached by a part usage owned by an item usage (`item it : Thing { part rk : Rack; }`). Occurrence roots are the part usages not owned by a part def or part usage (occurrence.py:935-942), but only a package-owned root gets package metadata (occurrence.py:1021-1031), so the part becomes a root with none and graph validation refuses a valid model. Split out of the _graph_failure factory so it carries its own reason; refusing or accepting such models differently is RG-1')
out_rows = []
for r in body:
    if r[0] == CYCLES:
        out_rows.append(new)
    out_rows.append(r)
assert G in {r[0] for r in out_rows}

# Refresh line and first evidence pointer for rows in the two edited files whose site moved.
scan = site_scan.scan().by_id()
for r in out_rows:
    if r[col['file']] in ('sysml_codegen/elaboration/elaborate.py', 'sysml_codegen/elaboration/graph.py'):
        line = str(scan[r[0]].line)
        if r[col['line']] != line:
            ev = r[col['evidence']].split('; ')
            if ev and ev[0].startswith(r[col['file']] + ':'):
                ev[0] = f"{r[col['file']]}:{line}"
            r[col['line']] = line
            r[col['evidence']] = '; '.join(ev)

comments = [('# sites: %d' % len(out_rows)) if c.startswith('# sites:') else c for c in comments]
comments = [c.replace('reachability, which a row\'s role states from inspection, not proof;',
                      'reachability, which a row\'s role states from inspection, not proof, except that no case may reach a site whose role says none does (tests/conformance/subset_profile/test_site_reach.py);') for c in comments]
out = io.StringIO(); csv.writer(out, lineterminator='\n').writerows([header] + out_rows)
open(P, 'w', newline='').write('\n'.join(comments) + '\n' + out.getvalue())
