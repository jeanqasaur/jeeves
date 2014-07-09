<h1>Jeeves Test Projects</h1>
	<ul>
		<li>
			simpleRule: Demonstrates a rule preventing anyone seeing the Social Security Number of
			a person. Altering the jelf.models.individual.jeeves_restrict_individuallabel method can
			result in more complex restrictions on the value's visibility.
		</li>
		<li>
			foreignkkey1Child: Demonstrates a rule on a model referenced by another. This rule restricts the viewing of the last 3 digits of a zipCode.
			Altering jelf.models.Address.jeeves_restrict_Addresslabel can result in more complex restrictions on the value's visibility.
		</li>
	</ul>