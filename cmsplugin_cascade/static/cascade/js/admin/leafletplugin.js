django.jQuery(function($) {
	'use strict';

	django.cascade.LeafletPlugin = ring.create(eval(django.cascade.ring_plugin_bases.LeafletPlugin), {
		constructor: function() {
			this.$super();
			this.leaflet = JSON.parse($('#id_leaflet').val());
			this.setup();
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
		}
	});

});
