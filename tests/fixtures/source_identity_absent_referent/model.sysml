package source_identity_absent_referent {
    private import ScalarValues::*;

    // SOURCE-IDENTITY Item 4 genuine-miss fixture (see PROVENANCE.md).
    // C18: an aggregation term whose reference resolves to no modeled feature.
    // The term must produce an honest ABSENT_REFERENT input for policy — never
    // a mint and never a same-named capture.

    part def 'Ghost Widget' {
        attribute real_cost : Real = 5.0;
    }

    part def 'Absent Rollup' {
        attribute rollup_total : Real;
    }

    part def 'Absent Assembly' :> 'Absent Rollup' {
        part widget : 'Ghost Widget';
        // `ghost_cost` is genuinely absent from 'Ghost Widget'.
        :>> rollup_total = widget.ghost_cost + 1.0;
    }

    part absent_assembly : 'Absent Assembly';
}
