# calculator

## Intent
A four-function calculator for whole numbers. The panel shows a single line: the
number being typed, or the result of the last sum; it shows 0 before anything is
typed and after c clears. Digits 0 to 9 type a number. The keys + - * / choose
an operation. = shows the result, which may be negative. c clears everything.
Division is whole-number division; dividing by zero shows the word error until
the next key, which clears it. Numbers larger than nine digits show error the
same way. Nothing else is drawn.

## Choices
= result
c clear

## Tests
press 2+3=
expect "5"
press c
expect not "5"
press 12*12=
expect "144"
press 7/0=
expect "error"
press 9-10=
expect "-1"
