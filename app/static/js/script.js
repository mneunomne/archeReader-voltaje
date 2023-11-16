
var planetarium1;
var map;

var timestamp

var default_latlng = [4.6097, -74.0817]; // Bogotá

var startDate = new Date("October 25, 2023 12:00:00");

// init socket io
var socket = io.connect('http://' + document.domain + ':' + location.port);

const initPlanetarium = function (w, h) {
  let d = new Date("October 25, 1985 12:00:00");
  planetarium1 = S.virtualsky({
    id: 'skymap',
    projection: 'stereo',
    ra: -90,
    dec: -5.3911111,
    //'dec': -5.3911111,
    latitude: default_latlng[0],
    longitude: default_latlng[1],
    showplanets: true,
    transparent: true,
    // showorbits: true,
    az: 270,
    gridlines_az: true,
    gridlines_eq: true,
    gridlines_gal: false,
    meridian: true,
    ground: true,
    magnitude: 20,
    meteorshowers: true,
    showstarlabels: true,
    scalestars: 2,
    width: w,
    height: h,
    'constellations': true,
    constellationlabels: true,
    lang: 'es',
    fontsize: '12px',
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

const updatePlanetarium = function (lat, lon, timestamp, az) {
  planetarium1.setClock(new Date(timestamp));
  planetarium1.setLatitude(lat);
  planetarium1.setLongitude(lon);
  //planetarium1.toggleAzimuthMove(az);
  //planetarium1.setRA(lat);
  //planetarium1.setDec(lon);
  planetarium1.drawImmediate();
  // pan to jupiter
  //planetarium1.panTo(83.8220833, -5.3911111); 
}

const updatePlanetariumTime = function (timestamp) {
  planetarium1.setClock(timestamp);
  planetarium1.drawImmediate();
}

S(document).ready(function () {
  let w = window.innerWidth;
  let h = window.innerHeight;
  initPlanetarium(w, h);
  initMap()

  // Update the position of the map and the planetarium
  document.addEventListener('keyup', function (event) {
    if (event.key == 't') {
      //setRandomPosition()
    }
  });

  const setRandomPosition = function () {
    // test
    let lat = default_latlng[0] + ((2 * Math.random() - 1) * 1);
    let lon = default_latlng[1] + ((2 * Math.random() - 1) * 1);
    updateMapPosition(lat, lon);
    let now = new Date().getTime()
    let nowDate = new Date(now + (Math.random() * 10000000000));
    updatePlanetariumPosition(lat, lon, nowDate);
    timestamp = nowDate.getTime()

    const duration = 5000; // 1 second duration for the transition
    const startTime = Date.now();

    const updatePosition = () => {
      const elapsed = Date.now() - startTime;
      console.log("elapsed", elapsed)
      const progress = Math.min(elapsed / duration, 1);

      const easedProgress = cubicBezierEasing(progress);

      const newTimestamp = now + progress * (nowDate.getTime() - now);
      updatePlanetariumTime(new Date(newTimestamp));
      updateMapPosition(lat, lon);

      if (progress < 1) {
        requestAnimationFrame(updatePosition);
      }
    };

    // Start the smooth transition
    // updatePosition();
  }

  // Cubic Bezier Easing Function
  const cubicBezierEasing = (t) => {
    // You can customize the cubic bezier values here
    const p0 = 0;
    const p1 = 0.42;
    const p2 = 0.58;
    const p3 = 1;

    const t1 = 1 - t;
    return 3 * t1 * t1 * t * p1 + 3 * t1 * t * t * p2 + t * t * t * p3;
  };

  // decode function
  var decode = function (string) {
    var data = string.split("|").map((item) => {
      let result = ''
      if (item[0] == '-') {
        result = '-' + item.substring(1, item.length).replace('-', '.')
      } else {
        result = item.replace('-', '.')
      }
      return parseFloat(result)
    })
    return {
      lat: data[0],
      lon: data[1],
      timestamp: data[2],
      az: data[3],
    }
  }

  // add socket events
  socket.on('connect', function () {
    console.log('connected');
  });

  socket.on('disconnect', function () {
    console.log('disconnected');
  });

  // on message 'detection_data'
  socket.on('detection_data', function (msg) {
    console.log('detection_data', msg);
    var data = decode(msg.data)
    console.log("decode data", data)
    updatePlanetarium(data.lat, data.lon, data.timestamp, data.az)
    // setRandomPosition()

  });

  // clear message
  socket.on('clear', function (msg) {
    console.log('clear', msg);
  });
});
