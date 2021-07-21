django.jQuery(function($) {
	'use strict';
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

			// register event handlers on changing link_type and cms_page select boxes
			$link_type.change(function(evt) {
				self.toggleLinkTypes(evt.target.value);
			});
			$cmspage_select.change(function(evt) {
				self.toggleCMSPage(evt.target.value);
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
		toggleCMSPage: function(page_id) {
			var url = django.cascade.page_sections_url + page_id,
			    $selSection = $('#id_section');

			$.get(url, function(response) {
				var k, val;

				$selSection.children('option:gt(0)').remove();
				for (k = 0; k < response.element_ids.length; k++) {
					val = response.element_ids[k];
					$selSection.append($("<option></option>").attr("value", val[0]).text(val[1]));
				}
				$selSection.val(null);
			});
		},
		validateExtUrl: function(exturl) {
			$.get(django.cascade.validate_exturl_url, {
				exturl: exturl,
			}, function(response) {
				if (response.status_code === 200) {
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
