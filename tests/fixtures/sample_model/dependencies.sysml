package TestModels {
    public import ScalarValues::*;

    /**
     * First calculation in dependency chain.
     */
    calc def FirstCalc {
        in attribute base_value : Real;
        out attribute doubled : Real = base_value * 2.0;
    }

    /**
     * Second calculation that depends on FirstCalc output.
     */
    calc def SecondCalc {
        in attribute input_val : Real;
        out attribute squared : Real = input_val * input_val;
    }

    /**
     * Final calculation combining results.
     */
    calc def FinalCalc {
        in attribute val_a : Real;
        in attribute val_b : Real;
        out attribute total : Real = val_a + val_b;
    }
}
