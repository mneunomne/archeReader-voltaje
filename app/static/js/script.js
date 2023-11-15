
var planetarium1;
var map; 

var default_latlng = [4.6097, -74.0817]; // Bogotá

const initPlanetarium = function (w, h) {
  let d = new Date("-004235-11-14"); 
  planetarium1 = S.virtualsky({
    id: 'skymap',
    'projection': 'gnomic',
    //'ra': 83.8220833,
    //'dec': -5.3911111,
    latitude: default_latlng[0],
    longitude: default_latlng[1],
    showplanets: true,
    // showorbits: true,
    az: 0,
    width: w,
    height: h / 2,
    'constellations': true,
    constellationlabels: true,
    lang: 'es',
    fontsize: '18px',
    clock: d,
  });

}

const initMap = function () {
   // Initialize the map
  map = L.map('map').setView(default_latlng, 13); // set the initial coordinates and zoom level

  // Add the OpenStreetMap layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

}

const updateMapPosition = function (lat, lon, zoom = 13) {
  map.setView([lat, lon], zoom);
}

const updatePlanetariumPosition = function (lat, lon, timestamp) {
  planetarium1.setClock(timestamp);
  planetarium1.setLatitude(lat);
  planetarium1.setLongitude(lon);

  //planetarium1.setRA(lat);
  //planetarium1.setDec(lon);
  planetarium1.drawImmediate();
  // pan to jupiter
  //planetarium1.panTo(83.8220833, -5.3911111);
  
}

S(document).ready(function() {
  let w = window.innerWidth;
  let h = window.innerHeight;
  initPlanetarium(w, h);
  initMap()

  // Update the position of the map and the planetarium
  document.addEventListener('keyup', function(event) {
    if (event.key == 't') {
      // test
      let lat = default_latlng[0] + ((2 * Math.random() - 1) * 1);
      let lon = default_latlng[1] + ((2 * Math.random() - 1) * 1);
      updateMapPosition(lat, lon);
      let now = new Date().getTime()
      let nowDate = new Date(now + (Math.random() * 100000000000));
      updatePlanetariumPosition(lat, lon, nowDate);
    } 
  });
});
