django.jQuery(function($) {
	'use strict';

	var $map_responsive = $('#id_glossary_map_shapes_0');

	django.cascade.LeafletPlugin = ring.create(eval(django.cascade.ring_plugin_bases.LeafletPlugin), {
		constructor: function() {
			var self = this;
			this.$super();
			this.leaflet = JSON.parse($('#id_leaflet').val());
			this.setup();

			// install event handlers
			$map_responsive.change(function(evt) {
				self.toggleResponsive(evt.target.checked);
			});
			this.refreshChangeForm();
		},
		setup: function() {
			this.mymap = L.map('leaflet_edit_map').setView([this.leaflet.lat, this.leaflet.lng], this.leaflet.zoom);

			L.tileLayer(
				'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}',
				django.cascade.leaflet_settings
			).addTo(this.mymap);
			this.mymap.on('zoomend moveend', this.onMapChange, this);
		},
		onMapChange: function(evt, self) {
			console.log(evt);
			$.extend(
				this.leaflet,
				this.mymap.getCenter(),
				{zoom: this.mymap.getZoom()}
			);
			$('#id_leaflet').val(JSON.stringify(this.leaflet));
		},
		toggleResponsive: function(checked) {
			var $map_width_responsive = $('#id_glossary_map_width_responsive').closest('.glossary-widget'),
				$map_width_fixed = $('#id_glossary_map_width_fixed').closest('.glossary-widget');

			// if checkbox Map Shapes: Responsive is active, show adaptive width and heights
			if (checked) {
				$map_width_responsive.show();
				$map_width_fixed.hide();
			} else {
				$map_width_responsive.hide();
				$map_width_fixed.show();
			}
		},
		refreshChangeForm: function() {
			this.toggleResponsive($map_responsive.prop('checked'));
			this.$super && this.$super();
		}
	});

});
