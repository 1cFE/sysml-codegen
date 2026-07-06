package EpKeyCollisionDesign {
    private import ScalarValues::Real;
    private import EpKeyCollisionLibrary::*;

    // SC-4 A1 trip: two DISTINCT sibling names that sanitize to one entry-point
    // key. `'a b'` (space) and `'a-b'` (hyphen) both sanitize to `a_b`. Without
    // the fail-fast guard the second would silently overwrite the first.
    part probe {
        attribute 'a b' : Real = 1.0;
        attribute 'a-b' : Real = 2.0;

        calc c : PassthroughCalc {
            in x = 'a b';
        }
    }
}
