{
	name: 'inline_image',
	inline: true,
	group: 'inline',
	draggable: true,

	addAttributes() {
		console.log('inline_image addAttributes');
		return {
			src: {
				default: null,
			},
			alt: {
				default: null,
			},
			width: {
				default: null,
			},
			height: {
				default: null,
			},
			dataset: {
				default: {},
			},
		};
	},

	parseHTML() {
		return [{tag: 'img[src]'}];
	},

	renderHTML({HTMLAttributes}) {
		return ['img', HTMLAttributes];
	},

	// map the dialog form values to the richtext document state using attribute `richtext-map-to` on field `image_file`
	insert_image_file(elements) {
		const selected_file = JSON.parse(elements.image_file.dataset.selected_file);
		console.log('insert_image_file (selected_file)', selected_file);
		return {
			src: selected_file.thumbnail_url,
			dataset: {file_id: selected_file.id},
		};
	},

}
