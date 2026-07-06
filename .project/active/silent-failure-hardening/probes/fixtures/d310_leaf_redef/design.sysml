package D310Design {
    private import ScalarValues::*;
    private import D310PkgA::*;
    private import D310PkgB::*;

    part rig {
        part motor_a : D310PkgA::Motor;
        part motor_b : D310PkgB::Motor;
    }
}
