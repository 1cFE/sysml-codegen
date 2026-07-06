package D37Design {
    private import ScalarValues::*;
    private import D37PkgA::*;
    private import D37PkgB::*;
    private import D37Probe::*;

    part plant {
        part widget_a : D37PkgA::Widget;
        part widget_b : D37PkgB::Widget;

        calc noop : NoopCalc { in x = 1.0; }
    }
}
