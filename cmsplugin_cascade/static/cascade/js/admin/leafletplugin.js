django.jQuery(function($) {
	'use strict';

	var $map_responsive = $('#id_glossary_map_shapes_0');

	django.cascade.LeafletPlugin = ring.create(eval(django.cascade.ring_plugin_bases.LeafletPlugin), {
		constructor: function() {
			var self = this;
			this.$super();
			this.setup();

			// install event handlers
			$map_responsive.change(function(evt) {
				self.toggleResponsive(evt.target.checked);
			});
			this.refreshChangeForm();
		},
		setup: function() {
			this.mymap = L.map('leaflet_edit_map').setView([$('#id_glossary_latitude').val(), $('#id_glossary_longitude').val()], $('#id_glossary_zoomlevel').val());

			L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
				maxZoom: 21,
				attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
					'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
					'Imagery © <a href="http://mapbox.com">Mapbox</a>',
				id: 'mapbox.streets'
			}).addTo(this.mymap);

			this.mymap.on('zoomend moveend', this.onMapChange, this);
		},
		onMapChange: function(evt, self) {
			console.log(evt);
			var center = this.mymap.getCenter();
			$('#id_glossary_latitude').val(center.lat);
			$('#id_glossary_longitude').val(center.lng);
			$('#id_glossary_zoomlevel').val(this.mymap.getZoom());
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
