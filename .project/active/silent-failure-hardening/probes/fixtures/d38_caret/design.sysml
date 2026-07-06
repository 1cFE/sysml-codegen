package D38Design {
    private import ScalarValues::*;
    private import D38Lib::*;

    part plant {
        part pack : 'Pack' {
            :>> cell.base_cost = 50.0;
        }
    }
}
