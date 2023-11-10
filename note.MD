# RUNNING THE MODEL
Please use pipenv, one of the dependencies used in web visualization recently had a bad release (mesa-viz-tornado).
Appropriate version is referenced by ref and git link is provided in Pipfile.

The issue is being taken care of by the maintainer

`pipenv install` - create venv and install dependencies

`pipenv shell` - use venv

or use

`pipenv run <command>`

## Running visualizations
### web visualization
` python visualization_web.py ` - will output a link to a localhost website

variables can bez easily changed using various inputs on the left of the webpage.

**Apply them by clicking "Reset" in top nav menu.**

Start button - runs the model.
Stop button - stops the model.
Slider at the top of the grid allows for changing framerate


### matplotlib visualization
` python matplotlib_visualization.py` - will run the provided demo using matplotlib animations


variables can be edited by changing values in `matplolib_visualization.py`

### variables:

- V - distance agent can move ( can be different for each)
- d - distance below which agent can contract illness 
- p  - probability of getting sick if below distance d
- t<sub>1</sub> - incubation time
- t<sub>2</sub> - time till dead or immune
- m - probability of death


possible health states of agent:
- healthy
- developing (incubating)
- ill
- immune
- dead


### plots:
- [x] total cases
- [x] active cases
- [x] deaths
- [x] average density
- [x] number R<sub>0</sub> (reproduction number)

### ideas
- implement social distancing (possibility of contraction would have to depend on distance?)
- implement walls/barriers
- input of vaccinated agents as percentage
- different contraction_probability for each agent
- different death_probability for each agent
- no immunity
- introduce more variables for R<sub>0</sub>