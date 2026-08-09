package ElabIdentityCollisionProbe {
    private import ScalarValues::Real;

    // Same-named declarations in one namespace have no reload-stable SysIDE
    // declaration coordinate. The exact-ID front end must reject this shape
    // rather than choosing either declaration by name or traversal order.
    part def CollisionOwner {
        attribute repeated : Real = 1.0;
        attribute repeated : Real = 2.0;
    }

    // Anonymous containment usages exercise the other null-QN identity form.
    part : CollisionOwner;
}
