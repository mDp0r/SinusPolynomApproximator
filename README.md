
Introduction
=================
In my masters class "Problemsolving with heuristics" we built a Dash App making it possible to approximate the sine function between 0 and 1 with polynomial functions of power 0 to 6. We implemented several parametrisable algorithms such as grid search, hillclimber, iterated hillclimber and pattern search (Hooke & Jeeves). The Algorithms can use two optimization functions: Maximum pointwise error and mean squared error. These are calculated of 1000 samples in the range of the approximation. Both the Frontend (Plotly Dash) and the Backend (mainly numpy) are written in Python. The Backend is used for the approximation, the frontend for the visualisation. There is also a modified version of a public stylesheet in the assets folder. 

Update 02.02.2020
=================
Wow great date today. Anyway, added a function parser with the Equation library and made the interval flexible. Can approximate any function now in any intervall.

Future Notes
=================
I might loosen up the hardcoded restrictions, to e.g. use more elements in the grid search or make higher polynomials possible. 

See App in Action
=================
I deployed the App on AWS. You can have a look at http://sinpol-dev.eu-central-1.elasticbeanstalk.com/
Might be taken down in the future though. 
