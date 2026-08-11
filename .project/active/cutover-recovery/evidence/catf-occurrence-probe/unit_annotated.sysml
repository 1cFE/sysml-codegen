package PartDefUnit {
    private import ScalarValues::*;
    private import SI::*;
    calc def Span { in attribute lo : Real; out attribute width : Real = lo * 2.0; }
    part def Layer { attribute thickness : Real = 0.5 [m]; }
    part def Stack;
    part the_stack : Stack {
        part layer_a : Layer;
        calc span_calc : Span { in lo = layer_a::thickness; }
    }
}
