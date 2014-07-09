<h1>Jeeves Test Projects</h1>
<ul>
	<li>
		simpleRule: Demonstrates a rule preventing anyone seeing the Social Security Number of
		a person. Altering the jelf.models.individual.jeeves_restrict_individuallabel method can
		result in more complex restrictions on the value's visibility.
	</li>
	<li>
		foreignkkey1Child: Demonstrates a rule on a model referenced by another. This rule restricts the viewing of the last 3 digits of an address's zipCode.
		Altering jelf.models.Address.jeeves_restrict_Addresslabel can result in more complex restrictions on the value's visibility.
	</li>
	<li>
		foreignkkey2Parent: Demonstrates a rule on a model that references another. This rule restricts the viewing of the last 3 digits of a person's address's zipCode.
		Altering jelf.models.Individual.jeeves_restrict_Individuallabel can result in more complex restrictions on the value's visibility.<br>
		This rule has the same result as the above, but means a different rule. With a larger project, the developer would have to decide which rule accurately describes the needed policies.
	</li>
</ul>