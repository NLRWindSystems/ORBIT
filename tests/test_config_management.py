__author__ = "Jake Nunemaker"
__copyright__ = "Copyright 2020, National Renewable Energy Laboratory"
__maintainer__ = "Jake Nunemaker"
__email__ = "jake.nunemaker@nrel.gov"


from ORBIT import ProjectManager, load_config, save_config
from ORBIT.config import prepare_config_for_save
from ORBIT.core.library import extract_library_specs


def test_save_and_load_equality(subtests, tmp_yaml_del):

    complete_project = extract_library_specs("config", "complete_project")
    save_config(complete_project, "tmp.yaml", overwrite=True)
    new = load_config("tmp.yaml")

    with subtests.test("Check direct file equality"):
        assert new == complete_project

    with subtests.test("Check ProjectManager equality"):
        new_project = ProjectManager(new)
        new = prepare_config_for_save(new_project.config)

        expected_project = ProjectManager(complete_project)
        complete_project = prepare_config_for_save(expected_project.config)
        assert new == complete_project


def test_orbit_version_ProjectManager():

    config = ProjectManager.compile_input_dict(
        ["MonopileDesign", "MonopileInstallation"]
    )
    assert "orbit_version" in config.keys()
