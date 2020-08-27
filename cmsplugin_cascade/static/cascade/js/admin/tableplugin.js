django.jQuery(function($) {
	'use strict';
	var self, $headersField = $('#id_headers'), $dataField = $('#id_data');

	django.cascade.TablePlugin = ring.create(eval(django.cascade.ring_plugin_bases.TablePlugin), {
		constructor: function() {
			var options = {
				tableOverflow: true,
				fullScreen: true,
				onevent: this.spreadsheetChanged
			};
			self = this;
			this.$super();
			$.extend(options, {
				columns: [],
				data: JSON.parse($dataField.val())
			});
			$.each(JSON.parse($headersField.val()), function(index, value) {
				options.columns.push({title: value});
			});
			this.spreadsheet = $('#cascade_spreadsheet').jexcel(options);
		},
		spreadsheetChanged: function(event) {
			var watchedEvents = [
				'onafterchanges',
				'onchangeheader',
				'oninsertcolumn',
				'onmovecolumn',
				'ondeletecolumn',
				'oninsertrow',
				'onmoverow',
				'ondeleterow'
			];
			if (watchedEvents.indexOf(event) !== -1) {
				$dataField.val(JSON.stringify(self.spreadsheet.getJson()));
				$headersField.val(JSON.stringify(self.spreadsheet.getHeaders().split(',')));
			}
		}
	});

});
