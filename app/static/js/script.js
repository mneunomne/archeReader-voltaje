
var planetarium1;
var planetarium2;
var map;

var timestamp

var default_latlng = [4.6097, -74.0817]; // Bogotá

var startDate = new Date("1994/12/27 00:21:00");

var currentTime = startDate.getTime();
var currentAz = 45;

const messageContainer = document.getElementById('characters')
const skyContainer = document.getElementById('skymap')

const video_width = 800
const video_height = 600

const transition_duration = 4000

var sky_height; 

window.onload = function() {
  setTimeout(() => {
    if(!window.location.hash) {
        window.location = window.location + '#loaded';
        window.location.reload();
    }
  }, 5000)
}

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
  const options = {
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
    showstarlabels: false,
    scalestars: 2,
    scaleplanets: 3,
    width: w ,
    height: sky_height + 1,// + 15,
    //;keyboard: false, 
    mouse: true,
    constellations: true,
    constellationlabels: true,
    lang: 'es',
    fontsize: '18px',
    clock: startDate,
    credit: false,
  }
  planetarium1 = S.virtualsky(options);
  planetarium2 = S.virtualsky({
    ...options,
    showposition: false,
    showplanets: false,
    showdate: false,
    id: 'skymap2',
    constellationlabels: false,
    showstarlabels: false,
    height: window.innerHeight - sky_height
  });

  //planetarium1.advanceTime(1, 100)
  //planetarium2.advanceTime(1, 100)
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
  planetarium1.setClock(timestamp)//.calendarUpdate()
  planetarium1.changeAzimuth(az_step)
  planetarium2.setClock(timestamp)//.calendarUpdate()
  planetarium2.changeAzimuth(az_step)
}

const updatePlanetariumAz = function (az_step) {
  planetarium1.changeAzimuth(az_step)
  planetarium2.changeAzimuth(az_step)
}

const resizeVideo = function () {
  var ratio = video_width / video_height

  let w = window.innerWidth
  let h = w/ratio
  let h2 = window.innerHeight - h

  sky_height = window.innerHeight - h

  document.getElementById('video').style=`width: ${w}px; height: ${h}px;`
  document.getElementById('video2').style=`width: ${w}px; height: ${h2}px;`
  
}

S(document).ready(function () {
  let w = window.innerWidth;
  let h = window.innerHeight;
  resizeVideo();
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

      //return onSegmentData({data: data[segment_number]})

      $.get("/on_segment/" + segment_number, function (data, status) {
        console.log("data", data)
        onSegmentData({data: data})
      });
    }
    n = undefined;
    // 10-19
    switch (event.key) {
      case 'q': n = 10; break;
      case 'w': n = 11; break;
      case 'e': n = 12; break;
      case 'r': n = 13; break;
      case 't': n = 14; break;
      case 'y': n = 15; break;
      case 'u': n = 16; break;
      case 'i': n = 17; break;
      case 'o': n = 18; break;
      case 'p': n = 19; break;
      default:
        break;
    }
    if (n !== undefined) {
      $.get("/on_segment/" + n, function (data, status) {
        console.log("data", data)
        onSegmentData({data: data})
      });
    }
  });

  window.addEventListener('resize', function (event) {
    console.log("resize")
    resizeVideo()
  })

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
      

      // updatePlanetariumAz(az)
      updatePlanetariumTime(new Date(newTimestamp), az);
  
      if (progress < 1) {
        requestAnimationFrame(updateTransition);
      } else {
        currentTime = data.timestamp
        currentAz = data.az
        setTimeout(() => {
          console.log("done!")
          updatePlanetariumTime(new Date(data.timestamp), 0);
          setTimeout(() => {
            planetarium1.setClock(1).calendarUpdate()
            skyContainer.className = ''
          }, 50)
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
      item = item.replace(/^(X+)/g, '')
      item = item.replace('X', '.')
      console.log("item", item)
      return parseFloat(item)
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
    var string = msg.data//.replace(/X/g, '')
    console.log('string', string);
    var data = decode(string)
    console.log("decode data", data)
    // updatePlanetarium(data.lat, data.lon, data.timestamp, data.az)

    transitionPlanetarium(data, transition_duration)

    hideMessage()
    setTimeout(() => {
      displayMessage(string)
    }, transition_duration)
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
