window.addEventListener('DOMContentLoaded', (event) => {
	const formElement = document.getElementById(window.parent.CMS.cascade.form_id);
	const formsetElement = formElement?.closest('django-formset');
	if (!formsetElement)
		throw new Error("Used outside of <django-formset>. Check if `window.parent.CMS.cascade.form_id` is set.");

	formElement.addEventListener('submit', (event) => {
		window.requestIdleCallback(async () => {
			const response = await formsetElement.submit({name: '_save'});
			if (response?.ok) {
				const innerHTML = await response.text();
				document.body.setHTMLUnsafe(innerHTML);
				document.defaultView.frameElement?.dispatchEvent(new Event('load'));
			} else {
				document.defaultView.frameElement.style.display = 'block';
			}
		});
	});
});
