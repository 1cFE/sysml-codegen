package ProbePkg {
    part def 'IFE Driver' {
        attr power : Real;
    }
    part def 'HIF Driver' :> 'IFE Driver' {
        attr torque : Real;
    }
    part def Facility {
        part driver : 'IFE Driver';
    }
    part def Variant :> Facility {
        part :>> driver : 'HIF Driver';
    }
}
