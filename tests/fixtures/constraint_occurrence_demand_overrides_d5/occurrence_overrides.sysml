package OccurrenceOverride {
    private import ScalarValues::*;

    calc def PassThrough {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def AtLeastFive {
        in attribute reading_in : Real;
        reading_in >= 5.0
    }

    part def Cell {
        attribute reading : Real;
        assert constraint threshold : AtLeastFive {
            in reading_in = reading;
        }
    }

    calc keep_pipeline : PassThrough {
        in x = 1.0;
    }

    part plant {
        part low : Cell {
            :>> reading = 4.0;
        }
        part high : Cell {
            :>> reading = 6.0;
        }
    }
}
