from unyt.unit_systems import *

def create_code_unit_system(unit_registry, current_mks_unit=None):
    code_unit_system = UnitSystem(unit_registry.unit_system_id, "code_length",
                                  "code_mass", "code_time", "code_temperature",
                                  current_mks_unit=current_mks_unit,
                                  registry=unit_registry)
    code_unit_system["velocity"] = "code_velocity"
    if current_mks_unit:
        code_unit_system["magnetic_field_mks"] = "code_magnetic"
    else:
        code_unit_system["magnetic_field_cgs"] = "code_magnetic"
    code_unit_system["pressure"] = "code_pressure"
    return code_unit_system
