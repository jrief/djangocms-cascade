/// <reference path="../../django-formset/client/declaration.d.ts" />

window.djangoFormsetComponents = window.djangoFormsetComponents || [];
window.djangoFormsetComponents.push({
	selector: 'input[is="cascade-select-glyph"]',
	loader: fragmentRoot => new Promise((resolve, reject) => {
		import('./formset-extensions/GlyphSelector').then(({CascadeGlyphInputElement}) => {
			if (!window.customElements.get('cascade-select-glyph')) {
				window.customElements.define('cascade-select-glyph', CascadeGlyphInputElement, {extends: 'input'});
			}
			window.customElements.whenDefined('cascade-select-glyph').then(() => resolve());
		}).catch(err => reject(err));
	}),
});


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
				// replace body with <script> containing the data-bridge
				document.body.setHTMLUnsafe(innerHTML);
				document.defaultView.frameElement?.dispatchEvent(new Event('load'));
			} else {
				// prevent closing the iframe in order to show the error message(s)
				document.defaultView.frameElement.style.display = 'block';
			}
		});
		event.preventDefault();
		event.stopPropagation();
	});
});
