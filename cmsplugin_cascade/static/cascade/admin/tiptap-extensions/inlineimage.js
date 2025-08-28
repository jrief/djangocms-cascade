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

	// map the document state back to the dialog form.
	extract_alt_text(inputElement, attributes) {
		if (attributes.alt) {
			inputElement.value = attributes.alt;
		} else {
			const imageFileField = inputElement.form.elements.image_file;
			const setAltText = () => {
				const selectedFile = JSON.parse(imageFileField.dataset.selected_file ?? '{}');
				if (selectedFile.meta_data?.alt_text) {
					inputElement.value = selectedFile.meta_data.alt_text;
				}
			};

			// if no alt text was stored in the document, try to retrieve it from the selected file's meta data
			// wait for the data-selected_file attribute to be set on the input element
			const observer = new MutationObserver(mutations => {
				for (const mutation of mutations) {
					if (mutation.type === 'attributes' && mutation.attributeName === 'data-selected_file') {
						setAltText();
						observer.disconnect();
						break;
					}
				}
			});
			setAltText();
			observer.observe(imageFileField, {attributes: true});

			// if no alt text was provided, disconnect observer anyway to prevent memory leaks
			setTimeout(() => observer.disconnect(), 1000);
		}
	},

}
