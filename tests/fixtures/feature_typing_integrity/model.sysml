package FeatureTypingUserTypes {
    attribute def Real;
    attribute def Vector;
}

package FeatureTypingIntegrity {
    private import ScalarValues::*;

    calc def SupportedTypes {
        in attribute real_value : Real;
        in attribute integer_value : Integer;
        in attribute boolean_value : Boolean;
        in attribute string_value : String;
        out attribute result : Real = real_value;
    }

    calc def MissingType {
        in attribute value;
        out attribute result : Real = 0.0;
    }

    calc def UserDefinedLookalike {
        in attribute value : FeatureTypingUserTypes::Real;
        out attribute result : Real = 0.0;
    }

    calc def MultipleTypes {
        in attribute value : Real, Integer;
        out attribute result : Real = 0.0;
    }

    calc def UnsupportedType {
        in attribute value : FeatureTypingUserTypes::Vector;
        out attribute result : Real = 0.0;
    }
}
