package QuotedOwnerFormulaDesign {
    private import ScalarValues::Real;
    private import QuotedOwnerFormulaLibrary::*;

    // Quoted owner part: 'Margin Part' sanitizes non-trivially to Margin_Part
    // (M3). Every unquoted segment (package, entry attrs, consumer attr) avoids
    // the accidental-change forms so the no-op / B2 reasoning holds here.
    part 'Margin Part' {
        // Entry-point literals.
        attribute revenue : Real = 100.0;
        attribute cost : Real = 60.0;

        // FORMULA computed attribute on the quoted owner (the producer). Its
        // name is quoted ('net margin' -> python_name net_margin); the
        // expression references sibling attributes, so it classifies FORMULA.
        attribute 'net margin' : Real = revenue - cost;

        // FORMULA computed attribute in the SAME part that CONSUMES 'net margin'
        // (the consumer). A computed-attribute consumer wires through the
        // in-memory resolution_map (graph_builder.py:745, consumed at :823) —
        // the Item-5 FORMULA-derivation path, per the design appendix. This is
        // deliberately NOT a calc-usage consumer: a calc usage would route
        // through the raw SysML-QN REFERENCE match sites (dependency_backtracker
        // :473/:595), which are Item 7's and untouched here.
        attribute total_payout : Real = 'net margin' * 2.0;
    }
}
