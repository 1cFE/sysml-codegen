package Issue22Design {
    private import ScalarValues::Real;
    private import Issue22Library::*;

    part plant {
        part assembly : WidgetAssembly {
            :>> widget.base_cost = 100.0;
        }
    }
}
