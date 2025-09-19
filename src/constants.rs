use pyo3::prelude::*;

use outfit::constants::*;

/// Register Outfit constants into the Python module.
pub fn register_constants(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // 2π, useful for trigonometric conversions
    m.add("DPI", DPI)?;

    // Number of seconds in a Julian day
    m.add("SECONDS_PER_DAY", SECONDS_PER_DAY)?;

    // Astronomical Unit in kilometers (IAU 2012)
    m.add("AU", AU)?;

    // Numerical epsilon used for floating-point comparisons
    m.add("EPS", EPS)?;

    // MJD epoch of J2000.0 (2000-01-01 12:00:00 TT)
    m.add("T2000", T2000)?;

    // Conversion factor between Julian Date and Modified Julian Date
    m.add("JDTOMJD", JDTOMJD)?;

    // Degrees → radians
    m.add("RADEG", RADEG)?;

    // Arcseconds → radians
    m.add("RADSEC", RADSEC)?;

    // Radians → arcseconds
    m.add("RAD2ARC", RAD2ARC)?;

    // Hours → radians
    m.add("RADH", RADH)?;

    // Earth equatorial radius in meters (GRS1980/WGS84)
    m.add("EARTH_MAJOR_AXIS", EARTH_MAJOR_AXIS)?;

    // Earth polar radius in meters (GRS1980/WGS84)
    m.add("EARTH_MINOR_AXIS", EARTH_MINOR_AXIS)?;

    // Earth radius expressed in astronomical units
    m.add("ERAU", (EARTH_MAJOR_AXIS / 1000.0) / AU)?;

    // Gaussian gravitational constant k
    m.add("GAUSS_GRAV", GAUSS_GRAV)?;

    // k²
    m.add("GAUSS_GRAV_SQUARED", GAUSS_GRAV_SQUARED)?;

    // Speed of light in km/s
    m.add("VLIGHT", VLIGHT)?;

    m.add("VLIGHT_AU", VLIGHT_AU)?;

    Ok(())
}
