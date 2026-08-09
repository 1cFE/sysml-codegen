package ElabUnresolvedMultiplicity {
    private import ScalarValues::*;

    part def Cell;

    part host {
        attribute count : Integer;
        part cell : Cell[count];
    }
}
