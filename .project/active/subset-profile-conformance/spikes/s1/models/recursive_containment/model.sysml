package fx {
    private import ScalarValues::*;
    part def Node {
        attribute w : Real = 1.0;
        part child : Node;
    }
    part root : Node;
}
