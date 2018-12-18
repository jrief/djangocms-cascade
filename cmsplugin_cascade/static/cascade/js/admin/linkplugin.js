django.jQuery(function($) {
	'use strict';
	var $link_type = $("#id_link_type"), $cmspage_select = $("#id_cms_page");
	var $link_target = $(".glossary-widget .glossary_target");

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
			this.refreshChangeForm();
		},
		initializeLinkTypes: function() {
			this.linkTypes['cmspage'] = new this.LinkType('.form-row .field-box.field-cms_page, .form-row .field-box.field-section', true);
			this.linkTypes['exturl'] = new this.LinkType('.form-row .field-box.field-ext_url', true);
			this.linkTypes['email'] = new this.LinkType('.form-row .field-box.field-mail_to');
		},
		toggleLinkTypes: function(linkTypeName) {
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
		},
		toggleSharedGlossary: function($option) {
			var glossary = $option.data('glossary');
			try {
				$link_type.val(glossary['link']['type']);
				try {
					$cmspage_select.select2("data", {id: glossary['link']['pk'], text: glossary['link']['identifier']});
					$cmspage_select.prop('disabled', true);
				} catch(err) {
					if (!(err instanceof TypeError))
						throw err;
					$cmspage_select.val(glossary['link']['pk']);
				}
				$('#id_ext_url').val(glossary['link']['url']);
				$('#id_mail_to').val(glossary['link']['email']);
			} catch (err) {
				try {
					if (!(err instanceof TypeError))
						throw err;
					$cmspage_select.prop('disabled', false);
				} catch (err) {
					if (!(err instanceof TypeError))
						console.error(err);
				}
			}
			if (this.$super) {
				this.$super($option);
			} else {
				this.refreshChangeForm();
			}
		},
		toggleCMSPage: function(page_id) {
			var url = django.cascade.page_sections_url + page_id, $selSection = $('#id_section');

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
		refreshChangeForm: function() {
			this.toggleLinkTypes($link_type.val());
			this.$super && this.$super();
		}
	});
});
