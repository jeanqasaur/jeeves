- `jeevesdb/JeevesModel.py`
	- The `JeevesModel` class mimics the standard django API with `save` and `delete`. It has a `JeevesManager` called `objects`. The manager is responsible for returning a `QuerySet`, and our special `JeevesManager` returns a `JeevesQuerySet` that knows how to do the special queries.
	- The `JeevesQuerySet` implements `filter`, which, again, mimics the standard django API.
	  However, it also implements `all`, which notably does _not_ implement the standard API. Instead, `all` performs the actual query and returns a Jeeves list (specifically, a `JList2`). This process also involves looking up labels.
	- `ForeignKey`s are more complicated. `JeevesForeignKey` uses the `JeevesRelatedObjectDescriptor`, which defines methods `__get__` and `__set__` which are called when you try to get or set an attribute of an object (e.g., `paper.author`). The definition of `JeevesForeignKey` also incluedes a lot of boiler-plate methods subclassing from `ForeignKey`.

TODOs
- Handle self- and circular- dependences of foreign keys.
- Fix the policy declaration API (e.g., use the one in the paper). Fairly superficial change, but crucial (especially changing the word "private" to "public").
