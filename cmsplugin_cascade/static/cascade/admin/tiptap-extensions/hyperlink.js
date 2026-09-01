{
	name: 'hyperlink',
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
			anchor: {
				default: null,
			},
			download_file: {
				default: null,
			},
			mail_to: {
				default: null,
			},
			phone_number: {
				default: null,
			},
			rel: {
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

	// map richtext document state back to the dialog form using attribute `richtext-map-from` on field `link_type`
	change_link_type(inputElement, attributes) {
		if (attributes.cms_page && inputElement.value === "cmspage") {
			inputElement.checked = true;
		} else if (attributes.href && inputElement.value === "exturl") {
			inputElement.checked = true;
		} else if (attributes.download_file && inputElement.value === "download") {
			inputElement.checked = true;
		} else if (attributes.phone_number && inputElement.value === "phone") {
			inputElement.checked = true;
		} else if (attributes.mail_to && inputElement.value === "email") {
			inputElement.checked = true;
		} else {
			inputElement.checked = false;
		}
	},

}
