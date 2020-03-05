django.jQuery(function($) {
	'use strict';

	django.cascade.LeafletPlugin = ring.create(eval(django.cascade.ring_plugin_bases.LeafletPlugin), {
		constructor: function() {
			this.$super();
			this.mapPosition = JSON.parse($('#id_map_position').val());
			this.startPosition = $.extend({}, this.mapPosition);
			this.editMap = L.map('leaflet_edit_map', {scrollWheelZoom: false});
			L.tileLayer(
				django.cascade.leaflet_settings.tilesURL,
				django.cascade.leaflet_settings
			).addTo(this.editMap);
			L.easyButton('<span class="map-button" title="Center">&target;</span>', this.resetCenter, this).addTo(this.editMap);
			this.resetCenter();
			this.setMarkers();
			$('#inline_elements-group .add-row a').on('click', this, this.addInlineElement);
			$('#inline_elements-group .field-use_icon input').on('change', this, this.changeUseIcon);
			$.each($('#inline_elements-group .inline-related'), this.changeUseIcon);
			this.editMap.on('drag', this.onMapDrag, this);
		},
		resetCenter: function(event) {
			var self = event ? event.options : this;
			self.editMap.setView([self.startPosition.lat, self.startPosition.lng], self.startPosition.zoom);
		},
		onMapDrag: function(evt) {
			$.extend(
				this.mapPosition,
				this.editMap.getCenter(),
				{zoom: this.editMap.getZoom()}
			);
			$('#id_map_position').val(JSON.stringify(this.mapPosition));
		},
		setMarkers: function() {
			var self = this;
			$.each($('#inline_elements-group .inline-related.has_original'), function() {
				var title = $(this).find('.field-title input').val();
				var inputField = $(this).find('.field-position input');
				var marker = L.marker(JSON.parse(inputField.val()), {draggable: true});
				marker.addTo(self.editMap);
				marker.bindTooltip(title);
				marker.on('dragend', self.dragMarker, inputField);
			});
		},
		addMarker: function(event) {
			var element = $('#inline_elements-group .inline-related.last-related.dynamic-inline_elements:last');
			var title = element.find('.field-title input').val();
			var inputField = element.find('.field-position input');
			var marker = L.marker(event.latlng, {draggable: true});
			inputField.val(JSON.stringify(marker.getLatLng()));
			marker.addTo(this.editMap);
			marker.bindTooltip(title);
			marker.on('dragend', this.dragMarker, inputField);

			$('#leaflet_edit_map').removeClass('leaflet-crosshair');
			$('#inline_elements-group .add-row a').removeClass('disable-click');
			this.editMap.off('click');
		},
		dragMarker: function(event) {
			var marker = event.target;
			this.val(JSON.stringify(marker.getLatLng()));
		},
		addInlineElement: function(event) {
			var $this = $(this);
			$this.addClass('disable-click');
			$('#inline_elements-group .inline-deletelink').one('click', function() {
				$this.removeClass('disable-click');
			});
			$('#leaflet_edit_map').addClass('leaflet-crosshair');
			event.data.editMap.on('click', event.data.addMarker, event.data);
		},
		changeUseIcon: function(event) {
			var checkbox, markerImage;
			if (event.target) {
				checkbox = $(event.target);
				markerImage = checkbox.parents('.inline-related').find('.field-marker_image')
					.add(checkbox.parents('.inline-related').find('.field-marker_width'))
					.add(checkbox.parents('.inline-related').find('.field-marker_anchor'));
			} else {
				checkbox = $(this).find('.field-use_icon input');
				markerImage = $(this).find('.field-marker_image')
					.add($(this).find('.field-marker_width'))
					.add($(this).find('.field-marker_anchor'));
			}
			if (checkbox.is(':checked')) {
				markerImage.show();
			} else {
				markerImage.hide();
			}
		}
	});

});
