{
	// must be written in ES5 style
	name: 'glyph',
	inline: true,
	atom: true,
	marks: '',
	group: 'inline',
	draggable: true,
	keepOnSplit: false,

	addAttributes() {
		return {
			'aria-hidden': true,
			['class']: {
				default: null,
			},
			dataset: {
				default: {},
			},
		};
	},

	parseHTML() {
		return [{tag: 'i[class][aria-hidden="true"][data-font_id][data-prefix]'}];
	},

	renderHTML({HTMLAttributes}) {
		return ['i', HTMLAttributes];
	},

	// map richtext document state back to the dialog form using attribute `richtext-map-from` on field `icon_font`
	change_icon_font(selectElement, attributes) {
		if (selectElement.value != attributes.dataset.font_id) {
			selectElement.value = attributes.dataset.font_id;
			selectElement.dispatchEvent(new Event('change'));
		}
	},
}
