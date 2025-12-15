// Map.js - Real Map Functionalities
// This file contains all map-related functionality

let map;
let markers = [];
let infoWindow;
let autocomplete;
let currentLocationMarker = null;
let geocoder;
let directionsService;
let directionsRenderer;

// Initialize the map when the page loads
function initMap() {
    console.log("initMap called");
    try {
        // Check if Google Maps API is loaded
        if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
            console.error("Google Maps API not loaded!");
            document.getElementById("map").innerHTML = '<div style="padding: 20px; text-align: center; color: red;">Google Maps API failed to load. Please check your API key.</div>';
            return;
        }

        // Default center (Pune, India)
        const center = { lat: 18.5204, lng: 73.8567 };
        const mapElement = document.getElementById("map");
        
        if (!mapElement) {
            console.error("Map element not found!");
            return;
        }

        console.log("Creating map...");
        
        // Create map instance
        map = new google.maps.Map(mapElement, {
            center: center,
            zoom: 13,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            mapTypeControl: true,
            mapTypeControlOptions: {
                style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
                position: google.maps.ControlPosition.TOP_RIGHT,
                mapTypeIds: [
                    google.maps.MapTypeId.ROADMAP,
                    google.maps.MapTypeId.SATELLITE,
                    google.maps.MapTypeId.HYBRID,
                    google.maps.MapTypeId.TERRAIN
                ]
            },
            // streetViewControl: true,
            fullscreenControl: true,
            // zoomControl: true,
            scaleControl: true,
            rotateControl: true,
            gestureHandling: 'cooperative',
            disableDefaultUI: false
        });
        
        // Trigger resize to ensure map renders correctly
        google.maps.event.trigger(map, 'resize');

        // Initialize services
        geocoder = new google.maps.Geocoder();
        directionsService = new google.maps.DirectionsService();
        directionsRenderer = new google.maps.DirectionsRenderer();
        directionsRenderer.setMap(map);

        // Initialize info window
        infoWindow = new google.maps.InfoWindow();

        // Initialize autocomplete for search
        initAutocomplete();

        // Add default marker at center
        addMarker(center, "Default Location", "This is the default center point");

        // Add search functionality
        initSearchFunctionality();

        // Add location tracking
        initLocationTracking();

        console.log("Map initialized successfully!");
    } catch (error) {
        console.error("Error initializing map:", error);
        document.getElementById("map").innerHTML = '<div style="padding: 20px; text-align: center; color: red;">Error: ' + error.message + '</div>';
    }
}

// Initialize autocomplete for search box
function initAutocomplete() {
    const searchBox = document.getElementById("search-box");
    if (searchBox) {
        autocomplete = new google.maps.places.Autocomplete(searchBox, {
            types: ['geocode', 'establishment'],
            fields: ['geometry', 'name', 'formatted_address', 'place_id']
        });

        autocomplete.bindTo('bounds', map);

        autocomplete.addListener('place_changed', function() {
            const place = autocomplete.getPlace();
            if (!place.geometry) {
                console.log("No details available for input: '" + place.name + "'");
                return;
            }

            // Center map on selected place
            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(place.geometry.location);
                map.setZoom(17);
            }

            // Add marker for searched location
            addMarker(place.geometry.location, place.name || "Searched Location", place.formatted_address || "");
        });
    }
}

// Initialize search functionality
function initSearchFunctionality() {
    const searchBox = document.getElementById("search-box");
    const searchIcon = document.querySelector(".search-icon");

    if (searchIcon) {
        searchIcon.addEventListener('click', function() {
            performSearch();
        });
    }

    if (searchBox) {
        searchBox.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
}

// Perform search using geocoding
function performSearch() {
    const searchBox = document.getElementById("search-box");
    const query = searchBox.value.trim();

    if (!query) {
        alert("Please enter a location to search");
        return;
    }

    geocoder.geocode({ address: query }, function(results, status) {
        if (status === 'OK') {
            if (results[0]) {
                const location = results[0].geometry.location;
                
                // Center map on result
                map.setCenter(location);
                map.setZoom(15);

                // Add marker
                addMarker(location, results[0].formatted_address, results[0].formatted_address);
            } else {
                alert("No results found for: " + query);
            }
        } else {
            alert("Geocoding failed: " + status);
        }
    });
}

// Add marker to map
function addMarker(position, title, description) {
    const marker = new google.maps.Marker({
        position: position,
        map: map,
        title: title,
        animation: google.maps.Animation.DROP
    });

    // Add click listener to marker
    marker.addListener('click', function() {
        showInfoWindow(marker, title, description);
    });

    markers.push(marker);
    return marker;
}

// Show info window
function showInfoWindow(marker, title, content) {
    const infoContent = `
        <div style="padding: 10px;">
            <h3 style="margin: 0 0 10px 0; font-size: 16px;">${title}</h3>
            <p style="margin: 0; font-size: 14px; color: #666;">${content}</p>
            <button onclick="removeMarker(${markers.indexOf(marker)})" style="margin-top: 10px; padding: 5px 10px; background: #ff4444; color: white; border: none; border-radius: 5px; cursor: pointer;">Remove Marker</button>
        </div>
    `;
    
    infoWindow.setContent(infoContent);
    infoWindow.open(map, marker);
}

// Remove marker
function removeMarker(index) {
    if (index >= 0 && index < markers.length) {
        markers[index].setMap(null);
        markers.splice(index, 1);
        infoWindow.close();
    }
}

// Clear all markers
function clearAllMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
    infoWindow.close();
}

// Initialize location tracking
function initLocationTracking() {
    if (navigator.geolocation) {
        // Add button for getting current location
        addLocationButton();
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

// Add location button to map
function addLocationButton() {
    const locationButton = document.createElement("button");
    locationButton.textContent = "📍 My Location";
    locationButton.style.cssText = `
        margin: 10px;
        padding: 10px 15px;
        background-color: #fff;
        border: 2px solid #fff;
        border-radius: 3px;
        box-shadow: 0 2px 6px rgba(0,0,0,.3);
        
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
    `;
    
    locationButton.addEventListener("click", getCurrentLocation);
    
    // Place the custom location button in the bottom-right corner.
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(locationButton);
}

// Get current location
function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };

                // Remove previous location marker
                if (currentLocationMarker) {
                    currentLocationMarker.setMap(null);
                }

                // Add current location marker
                currentLocationMarker = new google.maps.Marker({
                    position: pos,
                    map: map,
                    title: "Your Current Location",
                    icon: {
                        url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
                    },
                    animation: google.maps.Animation.BOUNCE
                });

                // Center map on current location
                map.setCenter(pos);
                map.setZoom(15);

                // Show info window
                geocoder.geocode({ location: pos }, function(results, status) {
                    if (status === 'OK' && results[0]) {
                        showInfoWindow(currentLocationMarker, "Your Current Location", results[0].formatted_address);
                    } else {
                        showInfoWindow(currentLocationMarker, "Your Current Location", "Lat: " + pos.lat + ", Lng: " + pos.lng);
                    }
                });

                // Stop bounce animation after 2 seconds
                setTimeout(function() {
                    if (currentLocationMarker) {
                        currentLocationMarker.setAnimation(null);
                    }
                }, 2000);
            },
            function() {
                alert("Error: The Geolocation service failed.");
            }
        );
    } else {
        alert("Error: Your browser doesn't support geolocation.");
    }
}

// Calculate distance between two points
function calculateDistance(point1, point2) {
    return google.maps.geometry.spherical.computeDistanceBetween(
        new google.maps.LatLng(point1.lat, point1.lng),
        new google.maps.LatLng(point2.lat, point2.lng)
    );
}

// Get directions between two points
function getDirections(origin, destination, travelMode = 'DRIVING') {
    directionsService.route({
        origin: origin,
        destination: destination,
        travelMode: google.maps.TravelMode[travelMode]
    }, function(response, status) {
        if (status === 'OK') {
            directionsRenderer.setDirections(response);
        } else {
            alert('Directions request failed due to ' + status);
        }
    });
}

// Clear directions
function clearDirections() {
    directionsRenderer.setDirections({ routes: [] });
}

// Fit map to show all markers
function fitBoundsToMarkers() {
    if (markers.length === 0) return;

    const bounds = new google.maps.LatLngBounds();
    markers.forEach(marker => {
        bounds.extend(marker.getPosition());
    });
    map.fitBounds(bounds);
}

// Change map type
function setMapType(mapTypeId) {
    map.setMapTypeId(mapTypeId);
}

// Set map zoom level
function setZoom(level) {
    map.setZoom(level);
}

// Pan to location
function panToLocation(lat, lng) {
    map.panTo({ lat: lat, lng: lng });
}

// Export functions for global access
window.mapFunctions = {
    addMarker,
    removeMarker,
    clearAllMarkers,
    getCurrentLocation,
    performSearch,
    getDirections,
    clearDirections,
    fitBoundsToMarkers,
    setMapType,
    setZoom,
    panToLocation,
    calculateDistance
};

// Handle API loading errors
window.gm_authFailure = function() {
    console.error("Google Maps API authentication failed. Please check your API key.");
    const mapElement = document.getElementById("map");
    if (mapElement) {
        mapElement.innerHTML = '<div style="padding: 20px; text-align: center; color: red; background: white; border-radius: 10px; margin: 20px;">Google Maps API authentication failed. Please check your API key in the HTML file.</div>';
    }
};

