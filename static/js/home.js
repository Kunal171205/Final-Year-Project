let map;
let markers = [];
let autocomplete;
let currentLocationMarker = null;
let activeInfoWindow = null;

let userLocation = null;      // ONLY set when user clicks My Location
let locationConfirmed = false;

// ---------------- MAP STYLE ----------------
const pureMapStyle = [
  /* Hide all POIs (we add our own industry markers) */
  {
    featureType: "poi",
    elementType: "all",
    stylers: [{ visibility: "off" }]
  },

  /* Show city, state, area names */
  {
    featureType: "administrative",
    elementType: "labels.text",
    stylers: [{ visibility: "on" }]
  },

  /* Show road names */
  {
    featureType: "road",
    elementType: "labels.text",
    stylers: [{ visibility: "on" }]
  },

  /* Keep road geometry visible */
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ visibility: "on" }]
  },

  /* Keep land */
  {
    featureType: "landscape",
    elementType: "geometry",
    stylers: [{ visibility: "on" }]
  },

  /* Keep water */
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ visibility: "on" }]
  }
];


// ---------------- INDUSTRY KEYWORDS ----------------
const INDUSTRY_KEYWORDS = [
  "industrial estate",
  "manufacturing",
  "industry",
  "manufacturer",
  "warehouse"
];

const seenPlaces = new Set();

// ---------------- ZOOM CONFIG ----------------
function getIndustryConfigByZoom(zoom) {
  if (zoom <= 11) return { radius: 20000, limit: 10 };
  if (zoom <= 13) return { radius: 12000, limit: 20 };
  if (zoom <= 15) return { radius: 6000, limit: 40 };
  return { radius: 3000, limit: 80 };
}

// ================================
// INIT MAP (NO GPS HERE)
// ================================
function initMap() {
  const fallbackCenter = { lat: 18.5204, lng: 73.8567 }; // Pune / MIDC fallback

  map = new google.maps.Map(document.getElementById("map"), {
    center: fallbackCenter,
    zoom: 13,
    styles: pureMapStyle
  });

  initAutocomplete();
  initLocationButton();

  // Load industries based on map view (NOT GPS)
  google.maps.event.addListenerOnce(map, "idle", () => {
    searchIndustriesNearLocation(map.getCenter());
  });

  map.addListener("click", () => {
    if (activeInfoWindow) {
      activeInfoWindow.close();
      activeInfoWindow = null;
    }
  });
}

// ================================
// USER-TRIGGERED GPS (ONLY HERE)
// ================================
function getUserLocation() {
  if (!navigator.geolocation) {
    alert("Geolocation not supported");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    pos => {
      userLocation = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        accuracy: pos.coords.accuracy
      };

      locationConfirmed = true;

      if (currentLocationMarker) currentLocationMarker.setMap(null);

      currentLocationMarker = new google.maps.Marker({
        map,
        position: userLocation,
        icon: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
      });

      map.setCenter(userLocation);
      map.setZoom(15);

      searchIndustriesNearLocation(userLocation);
    },
    err => {
      alert("Unable to get location. Please enable GPS.");
      console.warn(err.message);
    },
    {
      enableHighAccuracy: true,
      maximumAge: 0,
      timeout: 20000
    }
  );
}

// ================================
// NEARBY INDUSTRY SEARCH
// ================================
function searchIndustriesNearLocation(location) {
  if (!google.maps.places || !location) return;

  clearMarkers();
  seenPlaces.clear();

  const { radius, limit } = getIndustryConfigByZoom(map.getZoom());
  const service = new google.maps.places.PlacesService(map);
  let count = 0;

  INDUSTRY_KEYWORDS.forEach(keyword => {
    service.nearbySearch(
      { location, radius, keyword },
      (results, status) => {
        if (status !== google.maps.places.PlacesServiceStatus.OK) return;

        results.forEach(place => {
          if (count >= limit) return;
          if (seenPlaces.has(place.place_id)) return;

          seenPlaces.add(place.place_id);
          addMarker(place.geometry.location, place.name, place.vicinity);
          count++;
        });
      }
    );
  });
}

// ================================
// TEXT SEARCH ("near me" ONLY IF CONFIRMED)
// ================================
function geocodePlaceAndSearch(placeDescription, fullQuery) {
  const geocoder = new google.maps.Geocoder();

  geocoder.geocode({ address: placeDescription }, (results, status) => {
    if (status !== "OK" || !results[0]) {
      runTextSearch(fullQuery, map.getCenter());
      return;
    }

    const location = results[0].geometry.location;

    // 🔒 LOCK LOCATION FIRST
    map.setCenter(location);
    map.setZoom(13);

    // 🔍 THEN SEARCH
    runTextSearch(fullQuery, location);
  });
}


function detectPlaceFromQuery(query, callback) {
  const service = new google.maps.places.AutocompleteService();

  service.getPlacePredictions(
    {
      input: query,
      types: ["geocode"], // ✅ broader & correct
    },
    (predictions, status) => {
      if (
        status === google.maps.places.PlacesServiceStatus.OK &&
        predictions &&
        predictions.length > 0
      ) {
        callback(predictions[0]);
      } else {
        callback(null);
      }
    }
  );
}


function searchByTextQuery(query) {
  const lower = query.toLowerCase();

  // ---------- CASE 1: NEAR ME ----------
  if (lower.includes("near me")) {
    if (!locationConfirmed || !userLocation) {
      alert("Click 'My Location' to enable near me search");
      return;
    }

    const cleaned = query.replace(/near me/gi, "").trim();
    runTextSearch(cleaned || query, userLocation);
    return;
  }

  // ---------- CASE 2: DETECT PLACE ----------
  detectPlaceFromQuery(query, prediction => {
    if (prediction) {
      geocodePlaceAndSearch(prediction.description, query);
    } else {
      // ---------- CASE 3: FALLBACK ----------
      runTextSearch(query, map.getCenter());
    }
  });
}

function runTextSearch(query, location) {
  if (!query || !location) return;

  clearMarkers();

  const service = new google.maps.places.PlacesService(map);

  service.textSearch(
    {
      query,
      location,
      radius: 15000,
    },
    (results, status) => {
      if (status !== google.maps.places.PlacesServiceStatus.OK) return;

      results.slice(0, 30).forEach(place => {
        addMarker(
          place.geometry.location,
          place.name,
          place.formatted_address
        );
      });
    }
  );
}


// ================================
// AUTOCOMPLETE + ENTER
// ================================
function initAutocomplete() {
  const input = document.getElementById("search-box");
  if (!input) return;

  autocomplete = new google.maps.places.Autocomplete(input);

  input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      e.preventDefault();
      searchByTextQuery(input.value.trim());
    }
  });
}

// ================================
// LOCATION BUTTON (ONLY SOURCE OF GPS)
// ================================
function initLocationButton() {
  const btn = document.createElement("button");
  btn.textContent = "📍 My Location";
  btn.style.cssText = `
    margin:10px;
    padding:8px 12px;
    background:#fff;
    cursor:pointer;
    font-weight:500;
  `;
  btn.onclick = getUserLocation;

  map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(btn);
}

// ================================
// MARKERS
// ================================
function addMarker(position, title, description = "") {
  const marker = new google.maps.Marker({ map, position, title });

  const infoWindow = new google.maps.InfoWindow({
    content: `
      <div style="font-family:Arial;min-width:220px">
        <div style="font-weight:600">${title}</div>
        <div style="font-size:13px;color:#555">${description || ""}</div>
        <a target="_blank"
           href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(title)}"
           style="color:#1a73e8;font-size:13px;text-decoration:none">
          View on Google Maps
        </a>
      </div>
    `
  });

  marker.addListener("click", () => {
    if (activeInfoWindow) activeInfoWindow.close();
    infoWindow.open(map, marker);
    activeInfoWindow = infoWindow;
  });

  markers.push(marker);
}

function clearMarkers() {
  markers.forEach(m => m.setMap(null));
  markers = [];
}

// ================================
// API ERROR
// ================================
window.gm_authFailure = function () {
  document.getElementById("map").innerHTML =
    "<h3 style='color:red'>Google Maps API key error</h3>";
};
