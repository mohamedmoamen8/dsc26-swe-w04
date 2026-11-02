## Tools
Used Kilo assistant to scaffold tests.

## What AI got wrong
Initial draft did not test problem media type or CORS origins.

## In my own words
Pick one mutant your first draft of tests did not kill. Why not, and what did you add?
The below-reserve off-by-one mutant was missed because I only checked a clearly below-reserve case; I added the exact boundary case where remaining stock equals reserve.

Why is a test that only asserts status_code == 409 weaker than one that asserts the problem type?
Because multiple distinct errors return 409, so status alone cannot distinguish which rule broke; asserting the problem type ties the failure to the specific cause.
