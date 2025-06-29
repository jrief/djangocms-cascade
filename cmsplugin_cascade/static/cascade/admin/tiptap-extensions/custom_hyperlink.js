{
	name: 'custom_hyperlink',
	priority: 1000,
	keepOnSplit: false,

	addAttributes() {
		return {
			href: {
				default: null,
			},
			cms_page: {
				default: null,
			},
			download_file: {
				default: null,
			},
		};
	},

	parseHTML() {
		return [{tag: 'a[href]:not([href *= "javascript:" i])'}];
	},

	renderHTML({HTMLAttributes}) {
		return ['a', HTMLAttributes, 0];
	},
}
