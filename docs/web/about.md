This document specifies version 2.0 of a data model for exchanging climate data for building performance simulation, design, and operation. It was developed through a stakeholder consensus process by the Building Data Exchange Committee of IBPSA-USA (the US affiliate of the International Building Performance Simulation Association) and is based on the framework and vocabulary of ANSI/ASHRAE/IBPSA Standard 232. Version 2.0 is intended to be included as an informative reference in ASHRAE Standard 169.

Scope of this version:

- The committee chose not to define a required minimum set of variables. Data providers and consumers select the variables and time periods their applications need.
- The data elements cover the common use cases of building thermal and daylight modeling. Other use cases may need different data elements, and readers are invited to propose variables this model does not include.
- The data model covers metadata, location, time series variables with regular and irregular time intervals, and statistical summaries of climate variables, including design conditions.
- This document does not specify how the data model should be serialized or which file formats should be used for publication.

## Open questions

The following questions from the committee's consensus process remain open and are expected to be resolved in future revisions.

1. Are there other variables, calculations, or use cases to support, for example variables specific to district heating and cooling network design?
1. Which use cases should the model cover? Not everything need be explicit in the model itself; providers are encouraged to document specifics for their users.
1. Which products, beyond the model itself, are needed to make it usable (helpers, example datasets such as the ASHRAE design data)?
1. How should derived variables be supported? Under the working principle recorded below, they stay out of the base model. Should they instead be (a) defined but optional in the base model, (b) supported only through documented extensibility or custom fields, or (c) split into a separate auxiliary model? The current exclusion list is in the [EPW](extra-pages/10-epw-to-model-mapping.md) and [ASHRAE and DDY](extra-pages/20-ashrae-to-ddy-and-model-mapping.md) mapping notes.
1. How should the data model express confidence intervals and uncertainty? Ideally stated per quantity, they could be expressed as an arbitrary range, a confidence level, a confidence interval, or as multiples of a spread statistic away from the central estimate. The spread statistic could be the standard deviation ("n-sigma" notation) or a measure such as the interquartile range (IQR), so that a normal distribution is not always assumed.
1. Should variable names follow a stated naming convention? Version 2.0 puts the qualifier before the quantity (`ground_albedo`, as in `dry_bulb_temperature`) and keeps `liquid_precipitation_depth`, where "depth" states the dimension of the value. The alternative names `albedo_ground` and `liquid_precipitation` were proposed in [PR #4](https://github.com/IBPSA-USA/climate-information/pull/4), but the reason for dropping "depth" was not recorded. The same convention would settle spelling questions such as `sulphur_dioxide` versus `sulfur_dioxide`.

## Decisions recorded

The committee reached the following decisions during the consensus process. They are recorded here for reference and may be revisited in future revisions.

- **Derived variables.** Variables derivable from measured variables by a deterministic calculation stay out of the base model. Providers receive guidance on pre-computing them into use-case "flavors" (for example, an ASHRAE-flavor output adding enthalpy, ranges, and return periods). How derived variables should be supported is open question 4.
- **Historical trends.** The model does not carry historical trends. The committee felt they were not essential (ref: the ASHRAE design conditions table).
- **Daily values.** The model supports design days and does not carry daily (365-value) series. The committee saw no need for daily values.
- **Return periods.** n-year return periods are excluded from the base model. If they are reintroduced, the notes should reference the calculation method (a mixture of the empirical distribution and a nominal Gumbel distribution), and the committee should consider naming them by the corresponding probability.

## Working group

### Version 2

- Parag Cameron-Rastogi (Working Group Chair)
- Neal Kruis
- Chip Barnaby
- Dru Crawley
- Michael Roth

### Version 1

- Parag Rastogi (Working Group Chair)
- Sagar Rao (Building Data Exchange Committee Chair)
- Neal Kruis (Building Data Exchange Committee Vice-Chair)
- Dru Crawley
- Chip Barnaby
- Ben Brannon
- Suhaas Mathur (Building Data Exchange Committee Secretary)
- Tim McDowell

## Contributors

### Version 2

- Sagar Rao

### Version 1

- Evyatar Erell
- John Mardaljevic
- Jan Wienold
- Eleonora Brembilla
- Chris Mackey
- Matthew Dahlhausen
- Michael Roth
- Tianzhen Hong
- Joshua New
- Dorit Aviv
- Forrest Meggers

## Acknowledgments

This data model specification was developed with support from the U.S. Department of Energy.
