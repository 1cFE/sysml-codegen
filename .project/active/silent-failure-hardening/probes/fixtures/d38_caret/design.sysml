package D38Design {
    private import ScalarValues::*;
    private import D38Lib::*;
    private import D38Probe::*;

    part plant {
        part pack : 'Pack' {
            :>> cell.base_cost = 50.0;
        }

        calc noop : NoopCalc { in x = 1.0; }
    }
}
