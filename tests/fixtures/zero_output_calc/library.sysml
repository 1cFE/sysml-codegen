package ZeroOutputLibrary {
    private import ScalarValues::Real;

    // A calc def with an input but no 'out attribute'. It extracts with zero
    // output attributes, which must fail fast at extraction (REQ-EXT-08) rather
    // than crashing later inside the Jinja module template.
    calc def NoOutputCalc {
        in attribute x : Real;
    }
}
