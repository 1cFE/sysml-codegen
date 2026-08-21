package OccurrenceExecutionMatrix {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;

    calc def Double {
        in attribute x : Real;
        out attribute y : Real = x * 2.0;
    }

    calc def Increment {
        in attribute x : Real;
        out attribute y : Real = x + 1.0;
    }

    part def Child {
        attribute value : Real default 3.0;

        calc local : Double {
            in x = value;
        }
    }

    part def Unit {
        attribute local_value : Real default 5.0;
        part child : Child;

        calc same : Double {
            in x = local_value;
        }

        calc definition_local : Double {
            in x = Unit::local_value;
        }

        calc nested_sibling : Double {
            in x = child.value;
        }

        calc producer : Increment {
            in x = local_value;
        }

        calc output_consumer : Double {
            in x = producer.y;
        }
    }

    part unit : Unit[2];

    attribute package_source : Real = 7.0;

    calc package_calc : Double {
        in x = package_source;
    }

    part def CostCell {
        attribute cost : Real default 2.0;
    }

    attribute root_count : Integer = 2;
    part root_cell : CostCell[root_count];

    part def BankRollup {
        attribute total : Real;
    }

    part def Bank :> BankRollup {
        attribute count : Integer = 2;
        part cell : CostCell[count];
        :>> total = sum(cell.cost);
    }

    part bank : Bank;
}
