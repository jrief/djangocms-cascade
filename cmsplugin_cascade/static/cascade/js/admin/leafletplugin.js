django.jQuery(function($) {
	'use strict';

	django.cascade.LeafletPlugin = ring.create(eval(django.cascade.ring_plugin_bases.LeafletPlugin), {
		constructor: function() {
			this.$super();
			this.leafletStart = JSON.parse($('#id_leaflet').val());
			this.leaflet = $.extend({}, this.leafletStart);
			this.editMap = L.map('leaflet_edit_map');
			L.tileLayer(
				'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}',
				django.cascade.leaflet_settings
			).addTo(this.editMap);
			L.easyButton('<span class="map-button" title="Center">&target;</span>', this.resetCenter, this).addTo(this.editMap);
			this.resetCenter();
			this.setMarkers();
			$('#inline_elements-group .add-row a').on('click', this, this.addInlineElement);
			this.editMap.on('drag', this.onMapDrag, this);
		},
		resetCenter: function(event) {
			var self = event ? event.options : this;
			self.editMap.setView([self.leafletStart.lat, self.leafletStart.lng], self.leafletStart.zoom);
		},
		onMapDrag: function(evt) {
			$.extend(
				this.leaflet,
				this.editMap.getCenter(),
				{zoom: this.editMap.getZoom()}
			);
			$('#id_leaflet').val(JSON.stringify(this.leaflet));
		},
		setMarkers: function() {
			var self = this;
			$.each($('#inline_elements-group .inline-related.has_original'), function() {
				var title = $(this).find('.field-title input').val();
				var inputField = $(this).find('.field-leaflet input');
				var marker = L.marker(JSON.parse(inputField.val()), {draggable: true});
				marker.addTo(self.editMap);
				marker.bindTooltip(title);
				marker.on('dragend', self.dragMarker, inputField);
			});
		},
		addMarker: function(event) {
			var element = $('#inline_elements-group .inline-related.last-related.dynamic-inline_elements:last');
			var title = element.find('.field-title input').val();
			var inputField = element.find('.field-leaflet input');
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
		}
		/*
		selectInlineElement: function(event) {
			var self = event.data,
				inlineElement = $('#' + event.currentTarget.id),
				isSelected = inlineElement.hasClass('selected-inline'),
				leafletInputField = inlineElement.find('.field-leaflet').find('input');

			$('#inline_elements-group').find('.inline-related').removeClass('selected-inline');
			if (!isSelected) {
				inlineElement.addClass('selected-inline');
				if (leafletInputField.val()) {
					self.editMap.on('click', self.changeMarker, {self: self, input: leafletInputField});
				} else {
					$('#leaflet_edit_map').addClass('leaflet-crosshair');
					self.editMap.on('click', self.addMarker, {self: self, input: leafletInputField});
				}
			}
		}
		*/
	});

});
