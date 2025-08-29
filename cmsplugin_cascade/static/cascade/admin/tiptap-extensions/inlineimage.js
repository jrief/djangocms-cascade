{
	// must be written in ES5 style
	name: 'inline_image',
	inline: true,
	group: 'inline',
	draggable: true,

	addAttributes() {
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
						alt: body.alt_text,
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

	fetch_thumbnail_image(inputElement, attributes) {
		console.log('fetch_thumbnail_image', inputElement, attributes);
		const altInputElement = inputElement.form.elements.alt;

		// if no alt text was stored in the document, try to retrieve it from the selected file's meta data
		// wait for the data-selected_file attribute to be set on the input element
		const observer = new MutationObserver(mutations => {
			for (const mutation of mutations) {
				if (mutation.type === 'attributes' && mutation.attributeName === 'data-selected_file') {
					const selectedFile = JSON.parse(inputElement.dataset.selected_file ?? '{}');
					if (!altInputElement.dataset.alt_text_changed) {
						altInputElement.value = selectedFile.meta_data.alt_text;
					}
					break;
				}
			}
		});
		const altInputChanged = event => altInputElement.dataset.alt_text_changed = true;
		altInputElement.addEventListener('change', altInputChanged);
		inputElement.form.closest('dialog').addEventListener('close', event => {
			console.log('Dialog closed, disconnecting observer');
			observer.disconnect();
			altInputElement.removeEventListener('change', altInputChanged);
		}, {once: true});
		observer.observe(inputElement, {attributes: true});

		inputElement.value = attributes.dataset?.file_id ?? '';
		inputElement.dispatchEvent(new Event('change'));
	},

	// map the document state back to the dialog form.
	map_from_alt_text(inputElement, attributes) {
		inputElement.value = attributes.alt;
	},

}
