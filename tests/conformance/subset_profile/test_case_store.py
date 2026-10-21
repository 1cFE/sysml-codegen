"""Every case has one model folder and one stored generator answer (Item 2a design D14).

Pure: reads the case folders and stored answers.
"""

from __future__ import annotations

from tests.helpers.subset_profile import cases


def test_every_case_has_one_model_folder_and_one_generator_answer():
    assert cases.answer_ids() == cases.model_ids()
