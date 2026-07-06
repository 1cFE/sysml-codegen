package AnonymousReturnLibrary {
    private import ScalarValues::Real;

    // Anonymous `return` — a result with no name. syside synthesizes the name
    // `result` (from the redefined base Calculation::result) but leaves
    // declared_name empty. No name means no PQN output channel, so extraction
    // raises the V8 diagnostic (REQ-EXT-11) before the generic V7 zero-output
    // error. Live-only: extraction raises, so there is no committed snapshot
    // (mirrors zero_output_calc).
    calc def AnonReturn {
        in attribute x : Real;
        return : Real = x * 2;
    }
}
