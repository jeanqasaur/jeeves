Jeeves 1.0
======
Jeeves is a programming language for automatically enforcing privacy policies.

Jeeves helps programmers enforce _information flow policies_ describing where values may flow through a program.
An information flow policy can talk about not just whether Alice can see a sensitive value, but whether Alice can see a value computed from a sensitive value. For instance, a Jeeves policy may describe who can see a user's location in a social network. This policy is enforced not just when a viewer tries to access the location directly, but also when the viewer accesses values computed from the location, for instance the result of a search over all locations. Jeeves policies talk about whether a viewer may see a value. Policies are functions that take an argument corresponding to the output channel and produce a Boolean result.

Jeeves makes it easier for the programmer to enforce privacy policies by making the runtime responsible for producing the appropriate outputs. Jeeves has a _policy-agnostic programming model_: the programmer implements information flow policies separately from the other functionality. The runtime system becomes responsible for enforcing the policies. To allow for policy-agnostic programming, Jeeves asks the programmer to provide multiple views of sensitive values: a _high-confidentiality value_ corresponding to the secret view and a _low-confidentiality value_ corresponding to the public view. For instance, the high-confidentiality view of a user location could be the GPS location and the low-confidentiality view could be the corresponding country. The programmer provides policies about when the high-confidentiality view may be shown. The runtime then executes simultaneously on both views, yielding results that are appropriately guarded by policies. The Jeeves runtime guarantees that a value may only flow to a viewer if the policies allow.

This separation of policy and core functionality relieves programmer burden in keeping track of which policies need to be enforced where. The programmer can separately update policy and core functionality and rely on the runtime to handle the interaction of policies with each other and with the program. We invite you to try out our implementation of Jeeves as an embedded language in Python!

## Installing Jeeves.
We have the following dependencies.
### Python libraries
* macropy
* mock (for testing)

### Other
* The [Z3 SMT Solver](http://z3.codeplex.com/releases). You will need to build from source to use the Python Z3 library.


