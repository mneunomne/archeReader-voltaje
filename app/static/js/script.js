
var planetarium1;
var map; 

var default_latlng = [4.6097, -74.0817]; // Bogotá

const initPlanetarium = function (w, h) {
  planetarium1 = S.virtualsky({
    id: 'skymap',
    'projection': 'gnomic',
    //'ra': 83.8220833,
    //'dec': -5.3911111,
    showplanets: true,
    width: w,
    height: h / 2,
    'constellations': true,
    constellationlabels: true,
    lang: 'es',
    fontsize: '18px',
    clock: new Date("November 12, 2023 01:21:00"),
  });

  planetarium1.addPointer({
    'ra':83.8220792,
    'dec':-5.3911111,
    'label':'Orion Nebula',
    'img':'http://server7.sky-map.org/imgcut?survey=DSS2&w=128&h=128&ra=5.58813861333333&de=-5.3911111&angle=1.25&output=PNG',
    'url':'http://simbad.u-strasbg.fr/simbad/sim-id?Ident=M42',
    'credit':'Wikisky',
    'colour':'rgb(255,220,220)'
  })
}

const initMap = function () {
   // Initialize the map
  map = L.map('map').setView(default_latlng, 13); // set the initial coordinates and zoom level

  // Add the OpenStreetMap layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  // Add a marker for Bogotá
  L.marker(default_latlng).addTo(map)
    .bindPopup('Bogotá, Colombia')
    .openPopup();
}

const updateMapPosition = function (lat, lon, zoom = 13) {
  map.setView([lat, lon], zoom);
}

const updatePlanetariumPosition = function (lat, lon, timestamp) {
  planetarium1.setClock(timestamp);
  planetarium1.setRA(lat);
  planetarium1.setDec(lon);
  planetarium1.redraw();
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
      let lat = default_latlng[0] + ((2 * Math.random() - 1) * 0.1);
      let lon = default_latlng[1] + ((2 * Math.random() - 1) * 0.1);
      updateMapPosition(lat, lon);
    } 
  });
});
