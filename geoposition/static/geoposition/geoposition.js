if (typeof jQuery != 'undefined' && typeof django == 'undefined') {
    var django = {
        'jQuery': jQuery,
    };
}


(function($) {

    $(document).ready(function() {

        try {
            google;
        } catch (ReferenceError) {
            console.log('geoposition: "google" not defined.  You might not be connected to the internet.');
            return;
        }

        $('.geoposition-widget').each(function() {
            $(this).geopositionWidget();
        });

    });

    var mapDefaults = {
        'mapTypeId': google.maps.MapTypeId.ROADMAP,
        'scrollwheel': false,
        'streetViewControl': false,
        'panControl': false
    };

    var markerDefaults = {
        'draggable': true,
        'animation': google.maps.Animation.DROP
    };

    $.fn.geopositionWidget = function() {
        return this.filter(function() {
            var $container = $(this),
                $mapContainer = $('<div class="geoposition-map" />'),
                $addressRow = $('<div class="geoposition-address" />'),
                $searchRow = $('<div class="geoposition-search" />'),
                $searchInput = $('<input>', {'type': 'search', 'placeholder': 'Start typing an address …', 'results': 5}),
                $latitudeField = $container.find('input.geoposition:eq(0)'),
                $longitudeField = $container.find('input.geoposition:eq(1)'),
                latitude = parseFloat($latitudeField.val()) || null,
                longitude = parseFloat($longitudeField.val()) || null,
                map,
                mapLatLng,
                mapOptions,
                mapCustomOptions,
                markerOptions,
                markerCustomOptions,
                marker;

            if ($latitudeField.attr('id').indexOf('__prefix__') >= 0) {
                return false;
            }
            if ($latitudeField.attr('id').indexOf('-empty') >= 0) {
                return false;
            }
            if ($container.data('geoposition')) {
                return false;
            }
            $mapContainer.css('height', $container.attr('data-map-widget-height') + 'px');
            mapCustomOptions = JSON.parse($container.attr('data-map-options'));
            markerCustomOptions = JSON.parse($container.attr('data-marker-options'));

            function doSearch() {
                var gc = new google.maps.Geocoder();
                $searchInput.parent().find('ul.geoposition-results').remove();
                gc.geocode({
                    'address': $searchInput.val()
                }, function(results, status) {
                    if (status == 'OK') {
                        var updatePosition = function(result) {
                            if (result.geometry.bounds) {
                                map.fitBounds(result.geometry.bounds);
                            } else {
                                map.panTo(result.geometry.location);
                                map.setZoom(18);
                            }
                            marker.setPosition(result.geometry.location);
                            google.maps.event.trigger(marker, 'dragend');
                        };
                        if (results.length == 1) {
                            updatePosition(results[0]);
                        } else {
                            var $ul = $('<ul />', {'class': 'geoposition-results'});
                            $.each(results, function(i, result) {
                                var $li = $('<li />');
                                $li.text(result.formatted_address);
                                $li.bind('click', function() {
                                    updatePosition(result);
                                    $li.closest('ul').remove();
                                });
                                $li.appendTo($ul);
                            });
                            $searchInput.after($ul);
                        }
                    }
                });
            }

            function doGeocode() {
                var gc = new google.maps.Geocoder();
                gc.geocode({
                    'latLng': marker.position
                }, function(results, status) {
                    $addressRow.text('');
                    if (results && results[0]) {
                        $addressRow.text(results[0].formatted_address);
                    }
                });
            }

            var autoSuggestTimer = null;
            $searchInput.bind('keydown', function(e) {
                if (autoSuggestTimer) {
                    clearTimeout(autoSuggestTimer);
                    autoSuggestTimer = null;
                }

                // if enter, search immediately
                if (e.keyCode == 13) {
                    e.preventDefault();
                    doSearch();
                }
                else {
                    // otherwise, search after a while after typing ends
                    autoSuggestTimer = setTimeout(function(){
                        doSearch();
                    }, 1000);
                }
            }).bind('abort', function() {
                $(this).parent().find('ul.geoposition-results').remove();
            });
            $searchInput.appendTo($searchRow);
            $container.prepend($searchRow);
            $container.append($mapContainer, $addressRow);

            mapLatLng = new google.maps.LatLng(latitude, longitude);

            mapOptions = $.extend({}, mapDefaults, mapCustomOptions);

            if (!(latitude === null && longitude === null && mapOptions['center'])) {
                mapOptions['center'] = mapLatLng;
            } else if ($.isArray(mapOptions['center']) && mapOptions['center'].length == 2) {
                mapOptions['center'] = new google.maps.LatLng(mapOptions.center[0], mapOptions.center[1]);
            }

            if (!mapOptions['minZoom']) {
                mapOptions['minZoom'] = 1;
            }
            if (!mapOptions['maxZoom']) {
                mapOptions['maxZoom'] = 15;
            }

            if (!mapOptions['initialZoom']) {
                mapOptions['initialZoom'] = mapOptions['minZoom'];
            }

            if (!mapOptions['zoom']) {
                mapOptions['zoom'] = (latitude && longitude) ? mapOptions.maxZoom : mapOptions.initialZoom;
            }

            map = new google.maps.Map($mapContainer.get(0), mapOptions);
            markerOptions = $.extend({}, markerDefaults, markerCustomOptions, {
                'map': map
            });

            if (!(latitude === null && longitude === null && markerOptions['position'])) {
                markerOptions['position'] = mapLatLng;
            }

            marker = new google.maps.Marker(markerOptions);
            google.maps.event.addListener(marker, 'dragend', function() {
                $latitudeField.val(this.position.lat().toFixed(7));
                $longitudeField.val(this.position.lng().toFixed(7));
                doGeocode();
            });
            if ($latitudeField.val() && $longitudeField.val()) {
                google.maps.event.trigger(marker, 'dragend');
            }

            $latitudeField.add($longitudeField).bind('keyup', function(e) {
                var latitude = parseFloat($latitudeField.val()) || 0;
                var longitude = parseFloat($longitudeField.val()) || 0;
                var center = new google.maps.LatLng(latitude, longitude);
                map.setCenter(center);
                map.setZoom(15);
                marker.setPosition(center);
                doGeocode();
            });

            $container.data('geoposition', {
                'map': map,
                'marker': marker,
            });

            return true;
        });
    };

})((typeof grp == 'object' && grp.jQuery) ? grp.jQuery : django.jQuery);
