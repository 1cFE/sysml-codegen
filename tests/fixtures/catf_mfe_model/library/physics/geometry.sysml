/**
 * Geometry Calculations for Fusion Reactor Components
 *
 * Core geometric calculations for tokamak radial builds: minor radius,
 * toroidal volume, and surface area calculations for elongated tori.
 *
 * These calculations support ADR-002 compliance by providing reusable
 * calc defs for geometry expressions that would otherwise be inline
 * derived expressions in design files.
 *
 * **Package Naming**: Uses unique name (FusionPhysicsGeometry) to avoid
 * namespace collisions per SysML v2 requirements.
 *
 * **Qualified Names**:
 *   - FusionPhysicsGeometry::TorusMinorRadius
 *   - FusionPhysicsGeometry::TorusVolume
 *   - FusionPhysicsGeometry::TorusSurfaceArea
 *   - FusionPhysicsGeometry::MagnetSurfaceArea
 *
 * Created: 2025-12-22
 * Sources: Standard tokamak geometry, PyFECONS radial_build.sysml
 */
package FusionPhysicsGeometry {
    public import ScalarValues::*;
    public import SI::*;
    public import ISQ::*;

    /**
     * Toroidal Minor Radius Calculation
     *
     * Calculates the minor radius (a) of a toroidal annular layer from its
     * inner and outer radii relative to the major radius. The minor radius
     * represents the half-width of the layer cross-section at the midplane.
     *
     * Formula: a = (r_inner + r_outer) / 2.0 - r_major
     *
     * Where:
     *   r_inner = inner radius of the annular layer [m]
     *   r_outer = outer radius of the annular layer [m]
     *   r_major = major radius (center of torus/plasma) [m]
     *   a = minor radius (distance from major radius to layer center) [m]
     *
     * Source: Standard tokamak geometry convention
     * Reference: Used in radial build volume calculations
     * Typical Values:
     *   r_inner = 3.0-8.0 m (varies by layer, CATF MFE)
     *   r_outer = 3.1-8.55 m (varies by layer, CATF MFE)
     *   r_major = 3.0 m (CATF MFE)
     *   a = 0.5-4.0 m (varies by layer)
     * Last Updated: 2025-12-22
     */
    calc def TorusMinorRadius {
        in attribute r_inner : Real;      // [m] - Inner radius of layer
        in attribute r_outer : Real;      // [m] - Outer radius of layer
        in attribute r_major : Real;      // [m] - Major radius of torus

        out attribute a : Real = (r_inner + r_outer) / 2.0 - r_major;  // [m] - Minor radius

        constraint PositiveRadii {
            doc /* Inner radius must be non-negative, outer > inner, major > 0 */
            r_inner >= 0 and r_outer > r_inner and r_major > 0
        }
    }

    /**
     * Elongated Torus Volume Calculation
     *
     * Calculates the volume of an elongated toroidal shell with elliptical
     * cross-section. Used for computing radial build layer volumes in tokamaks.
     *
     * Formula: V = 2 * pi^2 * R * a^2 * kappa
     *
     * Where:
     *   R = major radius (center of torus) [m]
     *   a = minor radius (half-width at midplane) [m]
     *   kappa = elongation (vertical/horizontal aspect ratio)
     *   V = volume [m^3]
     *
     * Physical Basis: This is the volume of an elliptical torus. For a
     * circular torus (kappa=1), this reduces to V = 2*pi^2*R*a^2.
     *
     * Note: Uses pi * pi as a static expression, which is valid per ADR-002
     * (true static expressions with only literals are allowed).
     *
     * Source: Standard elliptical torus volume formula
     * Reference: PyFECONS radial_build.sysml lines 91-94
     * Typical Values:
     *   R = 3.0 m (CATF MFE major radius)
     *   a = 0.5-4.0 m (varies by layer)
     *   kappa = 3.0 (CATF MFE elongation)
     *   V = 50-2500 m^3 (varies by layer)
     * Last Updated: 2025-12-22
     */
    calc def TorusVolume {
        in attribute r_major : Real;      // [m] - Major radius
        in attribute a : Real;            // [m] - Minor radius
        in attribute kappa : Real;        // Dimensionless - Elongation

        out attribute volume : Real = 2.0 * 3.14159265359 * 3.14159265359 * r_major * a * a * kappa;  // [m^3]

        constraint PositiveInputs {
            doc /* Major radius, minor radius, and elongation must be positive */
            r_major > 0 and a > 0 and kappa > 0
        }

        constraint ReasonableElongation {
            doc /* Elongation typically 1.0 to 5.0 for tokamaks */
            kappa >= 1.0 and kappa <= 5.0
        }
    }

    /**
     * Elongated Torus Surface Area Calculation
     *
     * Calculates the surface area of an elongated toroidal surface.
     * Used for first wall area and other plasma-facing surface estimates.
     *
     * Formula: A = 2 * pi * R * a * kappa (simplified approximation)
     *
     * Where:
     *   R = major radius [m]
     *   a = minor radius (or effective radius parameter) [m]
     *   kappa = elongation
     *   A = surface area [m^2]
     *
     * Note: This is a simplified formula for the inner surface of a torus.
     * For a true elliptical torus, the exact formula involves elliptic integrals.
     * This approximation is consistent with PyFECONS usage.
     *
     * Source: PyFECONS radial_build.sysml lines 449-452
     * Reference: Tokamak first wall surface area estimation
     * Typical Values:
     *   R = 3.0 m (CATF MFE)
     *   a = 0.5-2.0 m
     *   kappa = 3.0 (CATF MFE)
     *   A = 30-100 m^2
     * Last Updated: 2025-12-22
     */
    calc def TorusSurfaceArea {
        in attribute r_major : Real;      // [m] - Major radius
        in attribute a : Real;            // [m] - Minor radius (or effective radius)
        in attribute kappa : Real;        // Dimensionless - Elongation

        out attribute area : Real = 2.0 * 3.14159265359 * r_major * a * kappa;  // [m^2]

        constraint PositiveInputs {
            doc /* All inputs must be positive */
            r_major > 0 and a > 0 and kappa > 0
        }
    }

    /**
     * Magnet Surface Area Calculation
     *
     * Calculates exposed surface area of magnet coils for nuclear heating
     * and cryogenic load estimates. Uses a fraction factor to account for
     * the portion of magnet surface exposed to radiation.
     *
     * Formula: A = 2 * pi * r_inner * thickness * kappa * f_exposed
     *
     * Where:
     *   r_inner = inner radius of magnet layer [m]
     *   thickness = radial thickness of magnet layer [m]
     *   kappa = elongation
     *   f_exposed = fraction of surface exposed (default 0.5)
     *   A = exposed surface area [m^2]
     *
     * Source: PyFECONS radial_build.sysml lines 455-457
     * Reference: Magnet nuclear heating surface area estimation
     * Typical Values:
     *   r_inner = 6.5 m (CATF MFE TF coil inner radius)
     *   thickness = 0.25 m (CATF MFE TF coil thickness)
     *   kappa = 3.0 (CATF MFE)
     *   f_exposed = 0.5 (half of surface faces inward)
     * Last Updated: 2025-12-22
     */
    calc def MagnetSurfaceArea {
        in attribute r_inner : Real;      // [m] - Inner radius of magnet layer
        in attribute thickness : Real;    // [m] - Radial thickness of magnet layer
        in attribute kappa : Real;        // Dimensionless - Elongation
        in attribute f_exposed : Real default := 0.5;  // Fraction of surface exposed

        out attribute area : Real = 2.0 * 3.14159265359 * r_inner * thickness * kappa * f_exposed;  // [m^2]

        constraint PositiveInputs {
            doc /* All inputs must be positive, f_exposed between 0 and 1 */
            r_inner > 0 and thickness > 0 and kappa > 0 and f_exposed > 0 and f_exposed <= 1.0
        }
    }
} // package FusionPhysicsGeometry
