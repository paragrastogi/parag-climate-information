"""
doit task/build automation
"""

import os

from lattice import Lattice


# Lattice's default build_validation=True runs validate_example_files() eagerly at
# import time, so any known-broken example would crash `doit list` (or any other
# task) before doit's task graph even runs -- not just the validate_example_files
# task itself. Run every build_validation step except that last one here instead,
# and leave example validation to task_validate_example_files below, where a
# failure is an ordinary doit task failure rather than an import-time crash.
climate_data_model = Lattice(build_validation=False)
climate_data_model.generate_meta_schemas()
climate_data_model.validate_schemas()
climate_data_model.generate_json_schemas()


def task_validate_example_files():
    """Validates the example files against the JSON schema (and other validation steps)"""
    return {
        "file_dep": climate_data_model.examples
        + [schema.schema.file_path for schema in climate_data_model.schema_info],
        "actions": [(climate_data_model.validate_example_files, [])],
    }


def task_generate_web_docs():
    """Generates Markdown Documentation"""
    return {
        "file_dep": [schema.schema.file_path for schema in climate_data_model.schema_info]
        + [template.path for template in climate_data_model.doc_templates],
        "targets": [os.path.join(climate_data_model.web_docs_directory_path, "public")],
        "actions": [(climate_data_model.generate_web_documentation, [])],
    }
