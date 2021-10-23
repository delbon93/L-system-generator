transform + rotate 25 deg;
transform - rotate -25 deg;
transform jump_left 
    translate -1 * (random(3) + 2), 0;

var small_bias = .1;

axiom F;

rule F = F [+ F] F [- F] F;
rule F = F [- F] F [+ F] F;

rule F = F [-F] F bias small_bias;
rule F = F [+F] F bias 0.1;


length max(7 - depth, 5);

iterate  3 + random(2);