package OccurrenceMultiplicityIncomparable {
    private import ScalarValues::*;

    part def Cell;

    part def Root {
        attribute count : Integer default 1;
        part cell : Cell[count];
    }

    part def Left :> Root {
        attribute :>> count = 2;
    }

    part def Right :> Root {
        attribute :>> count = 3;
    }

    part def Both :> Left, Right;

    part both : Both;
}
