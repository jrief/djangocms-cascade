/// <reference path="../../django-formset/client/declaration.d.ts" />

window.djangoFormsetComponents = window.djangoFormsetComponents || [];
window.djangoFormsetComponents.push({
	selector: 'input[is="cascade-select-glyph"]',
	loader: (fragmentRoot) => new Promise((resolve, reject) => {
		import('./formset/GlyphSelector').then(({CascadeGlyphInputElement}) => {
			if (!window.customElements.get('cascade-select-glyph')) {
				window.customElements.define('cascade-select-glyph', CascadeGlyphInputElement, {extends: 'input'});
			}
			window.customElements.whenDefined('cascade-select-glyph').then(() => resolve());
		}).catch(err => reject(err));
	}),
});
