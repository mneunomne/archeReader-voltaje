
var planetarium1;
var map;

var timestamp

var default_latlng = [4.6097, -74.0817]; // Bogotá

var startDate = new Date("1994/12/27 00:21:00");

var currentTime = startDate.getTime();
var currentAz = 45;

const messageContainer = document.getElementById('characters')
const skyContainer = document.getElementById('skymap')

const socket = new WebSocket(
  "ws://0.0.0.0:8025/arche-scriptures"
);

const data = dates.map((date) => {
  var lat = date.lat.substring(0, 16).padEnd(16, 'X')
  var lon = date.lon.substring(0, 16).padEnd(16, 'X')
  var timestamp = (date.timestamp+'').substring(0, 18).padStart(18, 'X')
  var az = date.az.substring(0, 3).padStart(3, 'X')
  return `${lat}|${lon}|${timestamp}|${az}`
})

// init socket io
// var socket = io.connect('http://' + document.domain + ':' + location.port);

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
    az: currentAz,
    // gridlines_az: true,
    // gridlines_eq: true,
    // gridlines_gal: false,
    // meridian: true,
    ground: true,
    magnitude: 20,
    meteorshowers: true,
    showstarlabels: true,
    scalestars: 3,
    scaleplanets: 3,
    width: w ,
    height: h,// + 15,
    keyboard: true, 
    mouse: true,
    constellations: true,
    constellationlabels: true,
    lang: 'es',
    fontsize: '14px',
    clock: startDate,
    credit: false,
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

const updatePlanetariumTime = function (timestamp, az_step) {
  planetarium1.setClock(timestamp).calendarUpdate()
  //planetarium1.drawImmediate();
  // planetarium1.drawPlanets();
  // planetarium1.draw();

}

const updatePlanetariumAz = function (az_step) {
  planetarium1.changeAzimuth(az_step)
}

S(document).ready(function () {
  let w = window.innerWidth;
  let h = window.innerHeight;
  initPlanetarium(w, h);
  // initMap()

  socket.onmessage = (event) => {
    console.log("onmessage", event.data);
    if (event.data.includes("detection-")) {
      var msg = event.data.split("detection-")[1]
      onSegmentData({data: msg})
    }
  };

  // Update the position of the map and the planetarium
  document.addEventListener('keyup', function (event) {
    if (event.key == 't') {
      //setRandomPosition()
      // toggleAzimuthMove
      let s = data[0].shuffle()
      console.log("s", s)
      onSegmentData({data: s})
    }
    // if key is number 0-9, send get request to server /on_segment/<segment_number>
    if (event.key >= '0' && event.key <= '9') {
      // send get request to server
      let segment_number = parseInt(event.key)

      onSegmentData({data: data[segment_number]})
      /*
      $.get("/on_segment/" + segment_number, function (data, status) {
        console.log("data", data)
      });
      */
    } 
  });

  // shuffle string function
  String.prototype.shuffle = function () {
    var a = this.split(""), n = a.length;
    for(var i = n - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = a[i];
        a[i] = a[j];
        a[j] = tmp;
    }
    return a.join("");
  }

  const setRandomPosition = function () {
    // test
    let lat = default_latlng[0] + ((2 * Math.random() - 1) * 1);
    let lon = default_latlng[1] + ((2 * Math.random() - 1) * 1);
    updateMapPosition(lat, lon);
    let now = new Date().getTime()
    let nowDate = new Date(now + (Math.random() * 10000000000));
    updatePlanetariumPosition(lat, lon, nowDate);
    timestamp = nowDate.getTime()
    // Start the smooth transition
    // updatePosition();
  }

  const transitionPlanetarium = (data,  duration = 500) => {
    var startTime = Date.now();
    skyContainer.className = 'transition'
    var az_diff = (data.az - currentAz)
    //var total = 0
    var lastEllapsed = Date.now() - startTime
    // updateMapPosition(data.lat, data.lon);
    function updateTransition () {
      const elapsed = Date.now() - startTime;
      var lastProg = (elapsed - lastEllapsed) / duration
      var az = lastProg * az_diff
      lastEllapsed = elapsed
      
      //total += az
      const progress = Math.min(elapsed / duration, 1);
  
      const newTimestamp = startTime + progress * (data.timestamp - currentTime);
      

      updatePlanetariumAz(az)
      // updatePlanetariumTime(new Date(newTimestamp), az);
  
      if (progress < 1) {
        requestAnimationFrame(updateTransition);
      } else {
        skyContainer.className = ''
        currentTime = data.timestamp
        currentAz = data.az
        setTimeout(() => {
          updatePlanetariumTime(new Date(data.timestamp), 0);
          planetarium1.setClock(1)
        }, 1)
      }
    }
    updateTransition();
  };

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
      console.log("item", item)
      let result = ''
      if (item[0] == '-') {
        result = '-' + item.substring(1, item.length).replace('-', '.')
      } else {
        result = item.replace('-', '.')
      }
      return parseFloat(result)
    })
    return {
      lat: validateLocation(data[0]),
      lon: validateLocation(data[1]),
      timestamp: validateTimestamp(data[2]),
      az: validedAzimuth(data[3]),
    }
  }

  var validateLocation = function (num){
    if (isNaN(num) || num == undefined || num == null) {
      return 0
    }
    let s = num + ''
    if (num > 90) {
      num = parseFloat(s[0] + '.' + s.substring(1, s.length))
    }
    if (num < -90) {
      num = parseFloat(s.substring(0, 2) + '.' + s.substring(2, s.length))
    }
    if (isNaN(num) || num == undefined || num == null) {
      return 0
    }
    return num
  }

  var validateTimestamp = function (num){
    console.log("validateTimestamp", num)
    if (isNaN(num) || num == undefined || num == null) {
      return 0
    } 
    return num
  }

  var validedAzimuth = function (num){
    console.log("validedAzimuth", num)
    if (isNaN(num) || num == undefined || num == null) {
      return 0
    }
    return num % 360
  }
/*
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
    onSegmentData(msg)
  });
  */

  const onSegmentData = function (msg) {
    console.log('detection_data', msg);
    var string = msg.data.replace(/X/g, '')
    console.log('string', string);
    var data = decode(string)
    console.log("decode data", data)
    // updatePlanetarium(data.lat, data.lon, data.timestamp, data.az)

    transitionPlanetarium(data, 5000)

    hideMessage()
    setTimeout(() => {
      displayMessage(string)
    }, 5000)
  }

  const displayMessage = function (msg) {
    msg.split('').map((char, index) => {
      if (char == '0') char = '20'
      if (char == '.') char = '-'
      const img = document.createElement('img')
      img.src='templates/' + char + '.svg'
      img.style = `transition-delay: ${index * 0.025}s;`
      messageContainer.appendChild(img)
      if (char == '|') {
        const br = document.createElement('br')
        messageContainer.appendChild(br) 
      }
    })
    setTimeout(() => {
      // hideMessage()
      messageContainer.className = 'show'
    }, 100)
  }

  const hideMessage = function () {
    messageContainer.className = ''
    setTimeout(() => {
      messageContainer.innerHTML = ''
    }, 1500)
    /*messageContainer.innerHTML = ''*/
  }
  /*
  // clear message
  socket.on('clear', function (msg) {
    console.log('clear', msg);
  });
  */
});
