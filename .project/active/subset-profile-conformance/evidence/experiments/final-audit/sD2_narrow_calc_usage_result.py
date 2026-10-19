import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
edit("agentic-mbse/src/agentic_mbse/sysml/subset_profile.py", '''    return [
        _at_site(site, "bare_result")''', '''    return [] and [
        _at_site(site, "bare_result")''')
