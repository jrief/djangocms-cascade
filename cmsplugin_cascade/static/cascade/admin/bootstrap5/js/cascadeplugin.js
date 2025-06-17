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
				const Window = window.parent || window;
				// the dataBridge is used to access plugin information from different resources
				Window.CMS.API.Helpers.dataBridge = JSON.parse(document.getElementById('data-bridge').textContent);
				// make sure we're doing after the "modal" mechanism kicked in
				setTimeout(()=> {
					// save current plugin
					Window.CMS.API.Helpers.onPluginSave();
					document.defaultView.frameElement?.dispatchEvent(new Event('load'));
				}, 100); // eslint-disable-line no-magic-numbers
			} else {
				document.defaultView.frameElement.style.display = 'block';
			}
		});
	});
});
