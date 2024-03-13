django.jQuery(function($) {
	'use strict';
	var $document = $(document);
	var $link_type = $("#id_link_type"), $cmspage_select = $("#id_cms_page");
	var $link_ext_url = $('#id_ext_url');
	var $link_type_row = $('.form-row.field-link_type');
	var $link_target = $(".form-row.field-link_target");
	var $link_title = $(".form-row.field-link_title");

	django.cascade.LinkPluginBase = ring.create({
		LinkType: ring.create({
			constructor: function(selector, addTarget) {
				this.$element = $(selector);
				this.addTarget = Boolean(addTarget);
			},
			show: function() {
				this.$element.show();
				if (this.addTarget) {
					$link_target.show();
				}
				$link_title.show();
				this.$element.find('input').focus();
			},
			hide: function() {
				this.$element.hide();
			}
		}),
		constructor: function() {
			var self = this;
			this.linkTypes = {};
			this.$super();
			this.initializeLinkTypes();

			$document.on('select2:open', function() {
				$('.select2-search__field').get(0).focus();
			});

			// register event handlers on changing link_type and cms_page select boxes
			$link_type.change(function(evt) {
				self.toggleLinkTypes(evt.target.value);
			});
			$cmspage_select.change(function(evt) {
				self.toggleCMSPage(evt.target.value, evt.target.lang);
			});
			$link_ext_url.on('blur', function(evt) {
				self.validateExtUrl(evt.target.value);
			});
			this.refreshChangeForm();
		},
		initializeLinkTypes: function() {
			this.linkTypes['cmspage'] = new this.LinkType('.form-row.field-cms_page, .form-row.field-section', true);
			this.linkTypes['download'] = new this.LinkType('.form-row.field-download_file');
			this.linkTypes['exturl'] = new this.LinkType('.form-row.field-ext_url', true);
			this.linkTypes['email'] = new this.LinkType('.form-row.field-mail_to');
			this.linkTypes['phonenumber'] = new this.LinkType('.form-row.field-phone_number');
		},
		toggleLinkTypes: function(linkTypeName) {
			if (linkTypeName) {
				$link_type_row.removeClass('no-link');
			} else {
				$link_type_row.addClass('no-link');
			}
			$.each(this.linkTypes, function(name, linkType) {
				if (name === linkTypeName) {
					linkType.show();
				} else {
					linkType.hide();
				}
			});
			if (!this.linkTypes[linkTypeName] || !this.linkTypes[linkTypeName].addTarget) {
				$link_target.hide();
			}
			if (!this.linkTypes[linkTypeName]) {
				$link_title.hide();
			}
		},
		toggleCMSPage: function(page_id, language_code) {
			const url = django.cascade.page_sections_url + page_id + '/?language=' + language_code;
			const $selSection = $('#id_section');
			const lookupUrl = (function() {
				try {
					return new URL($('.select2-search__field').val());
				} catch (e) {
					return null;
				}
			})();

			$.get(url, function(response) {
				let preselected = null;
				$selSection.children('option:gt(0)').remove();
				for (let k = 0; k < response.element_ids.length; k++) {
					const val = response.element_ids[k];
					const option = $("<option></option>").attr("value", val[0]).text(val[1]);
					if (lookupUrl && '#' + val[1] === lookupUrl.hash) {
						preselected = val[0];
					}
					$selSection.append(option);
				}
				$selSection.val(preselected);
			});
		},
		validateExtUrl: function(exturl) {
			if (!exturl) {
				$link_ext_url.removeClass('valid').removeClass('invalid');
				return;
			}
			$.get(django.cascade.validate_exturl_url, {
				exturl: exturl,
			}, function(response) {
				if (!response.status_code) {
					$link_ext_url.removeClass('valid').removeClass('invalid');
				} else if (response.status_code === 200) {
					$link_ext_url.addClass('valid').removeClass('invalid');
				} else {
					$link_ext_url.addClass('invalid').removeClass('valid');
				}
			});
		},
		refreshChangeForm: function() {
			this.toggleLinkTypes($link_type.val());
			this.validateExtUrl($link_ext_url.val());
			this.$super && this.$super();
		}
	});
});
