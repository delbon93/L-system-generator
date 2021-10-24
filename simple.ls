// Variables
var name = 42.1;
var other_name = name; // unused

// Rules
rule F = [-F] [+F] F;

rule F = F F bias 0.5;
rule x;
rule F bias 0.05;

rule F =
    x // just x
    [+x -x] // wiggly line
    bias name // likelihood dependend on variable
    ;

// End of file