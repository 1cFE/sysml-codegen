"""The subset-profile conformance harness (EXEC-SUBSET-CONTRACT Item 2a).

``observe`` runs the two halves of a case: the generator, through ``run_codegen``, and the
screen, through agentic-mbse's public subset functions. ``cases`` holds the stored answer
schema those observations are compared with.
"""
