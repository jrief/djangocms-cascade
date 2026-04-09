import capitalize from 'lodash.capitalize';
import template from 'lodash.template';
import '../../assets/scss/iconfont.scss';


class GlyphSelector {
	private readonly element: HTMLInputElement;
	private readonly previewElement: HTMLDivElement;
	private readonly fontIconField: HTMLSelectElement;
	private readonly cssLinkElement: HTMLLinkElement;
	private readonly endpoint: string;
	private readonly renderTemplate = template([
		'<% Object.entries(families).forEach(([family, glyphs]) => { %>',
			'<h2><%= capitalize(family) %></h2>',
			'<ul>',
			'<% glyphs.forEach(glyph => { %>',
				'<li title="<%= glyph %>" data-font_id="<%= font_id %>" data-prefix="<%= css_prefix_text %>">',
					'<i class="<%= css_prefix_text %><%= glyph %>"></i>',
				'</li>',
			'<% }); %>',
			'</ul>',
		'<% }); %>',
	].join(''), {imports: {capitalize}});

	constructor(element: HTMLInputElement) {
		this.element = element;
		this.endpoint = element.getAttribute('fonticon-endpoint');
		const observedField = this.element.getAttribute('fonticon-field');
		const fontIconField = this.element.form?.elements.namedItem(observedField);
		if (!(fontIconField instanceof HTMLSelectElement))
			throw new Error(`Attribute 'fonticon-field' on ${this.element} does not point onto a <select> element`);
		this.fontIconField = fontIconField;
		this.element.classList.add('dj-concealed');
		this.cssLinkElement = document.createElement('LINK') as HTMLLinkElement;
		this.cssLinkElement.setAttribute('rel', 'stylesheet');
		this.cssLinkElement.setAttribute('type', 'text/css');
		document.head.appendChild(this.cssLinkElement);
		this.previewElement = document.createElement('DIV') as HTMLDivElement;
		this.previewElement.classList.add('preview-iconfont');
		this.element.insertAdjacentElement('afterend', this.previewElement);
	}

	public async connectedCallback() {
		await this.loadIconFont(this.fontIconField.value);
		this.element.addEventListener('change', this.handleGlyphChanged);
		this.fontIconField.addEventListener('change', this.handleFontChanged);
		this.element.form.addEventListener('submit', this.handleSubmit);
	}

	public disconnectedCallback() {
		this.fontIconField.removeEventListener('change', this.handleFontChanged);
		this.previewElement.querySelectorAll('ul > li').forEach(liElement => liElement.removeEventListener('click', this.handleSelectGlyph));
		this.element.form?.removeEventListener('submit', this.handleSubmit);
	}

	private handleGlyphChanged = (event: Event) => {
		if (event.target !== this.element)
			return;
		this.previewElement.querySelectorAll('ul > li').forEach(liElement => liElement.ariaSelected = null);
		const preselected = this.previewElement.querySelector(`ul > li[title="${this.element.value}"]`);
		if (preselected instanceof HTMLLIElement) {
			preselected.ariaSelected = 'true';
		}
	};

	private handleFontChanged = async (event: Event) => {
		if (event.target instanceof HTMLSelectElement) {
			this.previewElement.querySelectorAll('ul > li').forEach(liElement => liElement.removeEventListener('click', this.handleSelectGlyph));
			if (!isNaN(Number(event.target.value))) {
				await this.loadIconFont(event.target.value);
			} else {
				this.previewElement.innerHTML = '';
				this.cssLinkElement.setAttribute('href', '');
			}
		}
	};

	private handleSelectGlyph = (event: Event) => {
		const target = event.target as HTMLElement;
		const liElement = target.tagName === 'LI' ? target : target.closest('li');
		if (liElement instanceof HTMLLIElement) {
			this.previewElement.querySelectorAll('ul > li').forEach(liElement => liElement.ariaSelected = null);
			liElement.ariaSelected = 'true';
			this.element.value = liElement.getAttribute('title');
			this.element.dataset.prefix = liElement.dataset.prefix;
			this.element.dispatchEvent(new Event('change', {bubbles: true}));
		}
	};

	private handleSubmit = () => {
		if (this.previewElement.querySelector(`ul > li[title="${this.element.value}"]`)?.ariaSelected !== 'true') {
			// the selected glyph is not part of the selected font icon, to prevent confusion
			// reset the value and submit an empty string, so that the form validation can catch the error
			this.element.value = '';
		}
	};

	private async loadIconFont(value: string) {
		if (isNaN(Number(value)))
			return;
		const response = await fetch(this.endpoint + value);
		if (response.ok) {
			const data = await response.json();
			this.renderSymbols(data);
			const preselected = this.previewElement.querySelector(`ul > li[title="${this.element.value}"]`);
			if (preselected instanceof HTMLLIElement) {
				preselected.ariaSelected = 'true';
			}
			this.previewElement.querySelectorAll('ul > li').forEach(liElement => liElement.addEventListener('click', this.handleSelectGlyph));
		}
	}

	private renderSymbols(data: any) {
		this.cssLinkElement.setAttribute('href', data.css_source);
		this.previewElement.innerHTML = this.renderTemplate(data);
	}
}

export class CascadeGlyphInputElement extends HTMLInputElement {
	#selector: GlyphSelector;

	connectedCallback() {
		this.#selector = new GlyphSelector(this);
		this.#selector.connectedCallback();
	}

	disconnectedCallback() {
		this.#selector.disconnectedCallback();
	}
}
