package zero_plant {
    private import ScalarValues::*;
    private import zero_library::*;

    part def 'Zero Plant' {
        doc /* A no-input calc usage: constant output, zero entry channels. */
        calc value_calc : 'Constant Calc' {}
    }

    // Instantiate the part so the calc usage is retained (not a dropped template).
    part zeroPlant : 'Zero Plant';
}
