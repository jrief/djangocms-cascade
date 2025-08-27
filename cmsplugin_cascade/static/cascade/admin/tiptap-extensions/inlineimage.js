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
	insert_cropped_image(elements) {
		// must be written in ES5 style
		const headers = new Headers();
		const match = document.cookie.match(/csrftoken=([0-9a-zA-Z]+);/);
		headers.append('X-CSRFToken', match ? match[1] : 'force2fail');
		const formData = new FormData();
		formData.append('width', elements.width.value);
		formData.append('height', elements.height.value);

		return new Promise((resolve, reject) => {
			const fileId = elements.image_file.value;
			if (fileId) {
				// fetch a cropped version of the file from the server
				const url = elements.image_file.parentElement.getAttribute('base-url') + fileId + '/crop';
				fetch(url, {
					method: 'POST',
					headers: headers,
					body: formData,
				}).then(response => response.json()).then(body => {
					resolve({
						src: body.cropped_image_url,
						alt: elements.alt_text.value,
						width: body.width,
						height: body.height,
						dataset: {file_id: body.image_id},
					});
				}).catch(error => {
					console.error("Error while fetching from: " + url, error);
					reject(error);
				});
			} else {
				resolve({dataset: null});
			}
		});
	},

}
