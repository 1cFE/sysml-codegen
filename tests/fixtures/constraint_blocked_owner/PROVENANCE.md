# Provenance

New fixture for CONSTRAINT-EXEC Item 5 (design.md D6, Appendix B: MF2). A
constraint-owning part def (`BlockedLeaf`, carrying `assert constraint nonneg`)
reached only through a `[*]` unbounded multiplicity (`BlockHost.star_member`),
mirroring `instance_index_probe`'s `BlockHost` blocking pattern
(`tests/fixtures/instance_index_probe/model.sysml:90-96`). A single, disjoint
leaf type keeps the model loadable — `nonunique` shapes emit a load-error
diagnostic and are avoided (the same note recorded in `instance_index_probe`).
