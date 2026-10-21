package fx {
    private import ScalarValues::*;
    package a { part def Site { attribute q : Real = 1.0; attribute t : Real = q * 2; } }
    package b { part def Site { attribute q : Real = 1.0; attribute t : Real = q * 3; } }
    part s1 : a::Site;
    part s2 : b::Site;
}
