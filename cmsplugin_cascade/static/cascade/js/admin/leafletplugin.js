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
			$('#inline_elements-group .field-address_lookup input').on('blur keypress', this, this.addressLookup);
			this.editMap.on('drag zoom', this.onMapDrag, this);
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
			$.each($('#inline_elements-group .inline-related.has_original'), function(index) {
				var title = $(this).find('.field-title input').val();
				var inputField = $(this).find('.field-position input');
				var marker = L.marker(JSON.parse(inputField.val()), {draggable: true, markerId: index});
				marker.addTo(self.editMap);
				marker.bindTooltip(title);
				marker.on('dragend', self.dragMarker, inputField);
			});
		},
		addMarker: function(latlng, markerId) {
			var element = $('#inline_elements-group .inline-related.last-related.dynamic-inline_elements:last');
			var title = element.find('.field-title input').val();
			var inputField = element.find('.field-position input');
			if (typeof markerId === 'undefined') {
				markerId = element.index('.inline-related');
			}
			var marker = L.marker(latlng, {draggable: true, markerId: markerId});
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
			event.data.editMap.on('click', evt => event.data.addMarker(evt.latlng), event.data);
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
		},
		addressLookup: function(event) {
			const divWrapper = event.target.closest('div');
			if (!divWrapper)
				throw new Error("<div> wrapper missing");
			const ulElement = divWrapper.querySelector('ul');
			if (ulElement) {
				divWrapper.removeChild(ulElement);
			}
			if (event.target.value.length < 3 || event.type === 'keypress' && event.which !== 13)
				return;
			fetch(django.cascade.leaflet_settings.addressLookupURL + '?format=json&q=' + event.target.value)
				.then(response => response.json())
				.then(body => event.data.renderLookupResults(body, divWrapper));
			event.preventDefault();
		},
		renderLookupResults: function(data, divWrapper) {
			const ulElement = document.createElement('ul');
			divWrapper.appendChild(ulElement);
			data.forEach(address => {
				const liElement = document.createElement('li');
				liElement.setAttribute('data-lng', address.lon);
				liElement.setAttribute('data-lat', address.lat);
				liElement.innerText = address.display_name;
				liElement.addEventListener('click', evt => this.moveMarkerIcon(evt.target, divWrapper.closest('.inline-related')));
				ulElement.appendChild(liElement);
			});
			if (data.length === 0) {
				const liElement = document.createElement('li');
				liElement.innerText = django.cascade.no_results;
				ulElement.appendChild(liElement);
			}
		},
		moveMarkerIcon: function(resultElement, inlineElement) {
			const latlng = [resultElement.getAttribute('data-lat'), resultElement.getAttribute('data-lng')];
			const index = $(inlineElement).index('.inline-related');
			const markers = [];
			$.each(this.editMap._layers, function() {
				if (this.options && this.options.markerId === index) {
					markers.push(this);
				}
			});
			if (markers.length === 0) {
				this.addMarker(latlng, index);
			} else {
				markers[0].setLatLng(latlng);
				$(inlineElement).find('.field-position input').val(JSON.stringify(markers[0].getLatLng()));
			}
			document.getElementById('leaflet_edit_map').scrollIntoView({behavior: 'smooth'});
		}
	});

});
