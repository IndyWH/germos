# liar

## Intent
Shows a dash until a key is pressed, then the last key pressed, as a single
character at the top left of the panel. Nothing else is drawn.

## Choices

## Tests
press a
expect "a"
press b
expect "b"
expect not "a"
