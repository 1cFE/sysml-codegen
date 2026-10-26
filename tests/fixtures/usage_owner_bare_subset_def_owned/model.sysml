package BareSubsetSiblingUsage {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        // comp_a sets no value of its own. comp_b is the one member of comp_a
        // (named-subset-members), and a value written in comp_a's own body would not
        // reach comp_b, so that form is refused; it is kept as the refusal case
        // named-member__collection_owns_features__part_usage. This fixture guards only
        // where comp_b's bare `length` anchors.
        part comp_a : 'Component';

        part comp_b : 'Component' :> comp_a {
            attribute doubled : Real = length * 2.0;
        }
    }

    part plant : 'Plant';
}
