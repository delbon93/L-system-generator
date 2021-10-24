transform rot_left rotate 45 deg;
transform jump_left translate -5.5, 0;

transform + rotate 90;

// Variables
var name = 42.1;
var other_name = name; // unused

// Starting point
axiom F;

// Line length
length 5;

// Number of iterations
var iterate_count = 10;
iterate iterate_count;

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