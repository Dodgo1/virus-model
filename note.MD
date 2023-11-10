# variables:

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
- [x] ? number R<sub>0</sub> (reproduction number)

### ideas
- implement social distancing (possibility of contraction would have to depend on distance?)
- implement walls/barriers
- number of vaccinated as percentage
- different contraction_probability for each agent
- different death_probability for each agent
- no immunity
- introduce more variables for R<sub>0</sub>