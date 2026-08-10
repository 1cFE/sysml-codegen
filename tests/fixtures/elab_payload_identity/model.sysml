package PayloadIdentityA {
    private import ScalarValues::*;
    calc def 'Normalize Payload' {
        in attribute 'same input' : Real = 2.0;
        attribute hidden_value : Real = 'same input' * 3.0;
        out attribute 'same output' : Real = hidden_value + 1.0; // W
    }

    constraint def 'Payload Guard' {
        in attribute observed : Real;
        in attribute limit : Real;
        observed == limit
    }
}

package PayloadIdentityB {
    private import ScalarValues::*;
    calc def Normalize_Payload {
        in attribute same_input : Real = 5.0;
        out attribute same_output : Real = same_input + 7.0; // m
    }


    constraint def Payload_Guard {
        in attribute observed : Real;
        in attribute limit : Real;
        observed <= limit
    }
}

package PayloadIdentityDesign {
    private import ScalarValues::*;

    part def System {
        attribute host_observed : Real = 2.0;
        attribute host_limit : Real = 3.0;
        attribute status : String = "ready";
        calc power_calc : PayloadIdentityA::'Normalize Payload';
        calc length_calc : PayloadIdentityB::Normalize_Payload;

        assert constraint blocked_guard : PayloadIdentityA::'Payload Guard' {
            in observed = host_observed;
            in limit = host_limit;
        }
        assert constraint admitted_guard : PayloadIdentityB::Payload_Guard {
            in observed = host_observed;
            in limit = host_limit;
        }
        assert constraint annotation_guard {
            status == "ready"
        }
        constraint unassessed_guard : PayloadIdentityB::Payload_Guard;
    }

    part system : System;
}
