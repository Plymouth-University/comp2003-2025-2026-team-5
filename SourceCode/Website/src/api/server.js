const net = require('net');
const http = require('http');
const fs = require('fs');
const pool = require('./db.js');

const TCP_PORT = 5000;
const HTTP_PORT = 3000;

let clients = [];
let circle = null; //only one circle can exist
let currentDeviceId = 1;

// geofence logic
async function isInsideGeofence(currentdeviceid, lat, lon) {
  const device_query = 'SELECT * FROM `device` WHERE `device_id` = ?';
  const id = currentdeviceid;
  const geofence_query = 'SELECT * FROM `geofence` where `patient_id` = ?';
  const broken_geofence = 'INSERT IGNORE INTO `broken_geofences`(patient_id, latitude, longitude) VALUES (?, ?, ?)';
  try { 
    const [device_rows] = await pool.query(device_query, [id]);
    if (!device_rows.length) {
      console.error("Device not found");
      return;
    }
    const patient_id = device_rows[0].patient_id;

     const broken_geo_values = [patient_id, lat, lon];

    const [geofence_rows] = await pool.query(geofence_query, [patient_id]);
    if (!geofence_rows.length) {
      console.error("Geofences not found for patient");
      return;
  }  else {
      for (const geofence of geofence_rows) {
        const d = haversine(lat, lon, geofence.latitude, geofence.longitude);
        console.log("Distance:", d, "Radius:", geofence.radius);
        if (d > geofence.radius) {
          console.log("Device is outside geofence:", geofence.geofence_id);
          await pool.query(broken_geofence, broken_geo_values);
          break; 
        };
  }
}
  } catch (err) {
    console.error("Database error:", err);
  }
}


// Function to check if device even exists in the database
async function doesDeviceExist(deviceid) {
  // Query to see if table has data
  const exists_query = 'SELECT * FROM  `device`';

  // Query to check if device exists within database
  const query = 'SELECT * FROM `device` WHERE `device_id` = ?';
  const id = deviceid;
  try {

    const [exists_rows] = await pool.query(exists_query);

    if (!exists_rows.length) {
      console.error("Device table does not have data");
      return false;
    } else {
      console.log("Device table has data");
    }

    const [device_rows] = await pool.query(query, [id]);

    if (!device_rows.length) {
      console.error("Device not found");
      return false;
    } else {
      console.log("Device found");
      return device_rows.length > 0;
    }
  } catch (err) {
    console.error("Database error:", err);
    return false;
  }
}

// Function to retrieve geofence from database
async function retrieveGeofence(deviceid) {
  const device_query = 'SELECT * FROM `device` WHERE `device_id` = ?';
  const device_query_values = [deviceid];
  const get_patient_id_query = 'SELECT patient_id FROM `device` WHERE `device_id` = ?';
  const geofence_query = 'SELECT * FROM `geofence` where `patient_id` = ?';

  try {
    const [device_rows] = await pool.query(device_query, device_query_values);
    if (!device_rows.length) {
      console.error("Device not found");
      return null;
    }

    const patient_id = await pool.query(get_patient_id_query, device_query_values);

    const [geofence_rows] = await pool.query(geofence_query, patient_id);

    if (!geofence_rows.length) {
      console.error("Geofences not found for patient");
      return null;
    }

    geofence_lat = geofence_rows[0].latitude;
    geofence_lon = geofence_rows[0].longitude;
    geofence_radius = geofence_rows[0].radius;
    geofence_shape = geofence_rows[0].shape;

    return { lat: geofence_lat, lon: geofence_lon, radius: geofence_radius, shape: geofence_shape };
  } catch (err) {
    console.error("Database error:", err);
    return null;
  }
}


//haversine formula
function haversine(lat1, lon1, lat2, lon2) {
  
  //readability
  const {sin, cos, sqrt, atan2, PI} = Math;

  //radius of the earth in metres
  const R = 6371000;

  //radian conversion function for readability
  function toRad(value) {

    return value * PI /180;

  }

  //distance between lat and lon points converted to radians
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  
  //haversine calculation, represents proportional distance on the surface of a sphere
  const a = sin(dLat / 2) ** 2 +
    
    cos(toRad(lat1)) *
    cos(toRad(lat2)) *
    sin(dLon / 2) ** 2;

  //apply constant a to the surface of the earth spefically
  return 2 * R * atan2(sqrt(a), sqrt(1 - a));

}

//checks whether the supplied coordinates are inside the geofence
function checkGeofence(lat, lon) {
  
  //no circle present
  if (!circle) return false;

  //haversine distance from the centre of the circle
  const d = haversine(lat, lon, circle.center.lat, circle.center.lon);
  
  //bounds check
  if (d <= circle.radius) {

    console.log("Inside geofence");

    return true

  } else if (d > circle.radius) {

    console.log("Outside geofence");

    return false

  }

}

//parses CGNSINF sentences
async function parseCGNSINF(sentence, deviceid) {

  /* if (!await doesDeviceExist(deviceid)) {

    console.error("Device does not exist, skipping CGNSINF parsing");
    return; 
  } */

  sentence = sentence.replace('+CGNSINF:', '');

  const p = sentence.split(',');

  if (p[3] === '') return;

  let lat = parseFloat(p[3]);
  let lon = parseFloat(p[4]);

  if (isNaN(lat) || isNaN(lon)) return;

  const privacy = checkGeofence(lat, lon);

  if (privacy === true) {

    lat = circle.center.lat
    lon = circle.center.lon

  }

  //server sent events handling
  /* const data = `data:${lat},${lon}\n\n`;
  clients.forEach(res => res.write(data)); */

  await isInsideGeofence(deviceid, lat, lon);

}


//TCP server
net.createServer(socket => {

  console.log('Client connected from', socket.remoteAddress);

  socket.on('data', d => {

    console.log('RAW BUFFER:', d);

    const text = d.toString('ascii');

    console.log('ASCII:', JSON.stringify(text));

    text.split(/\r?\n/).forEach(line => {

      line = line.trim();
      if (!line) return;

      console.log('LINE:', line);

      if (line.startsWith('+DEVICEID:')) {
        currentDeviceId = line.replace('+DEVICEID:', '').trim();
    }

      if (line.startsWith('+CGNSINF:')) {
      
        parseCGNSINF(line, currentDeviceId);
      
      }

    });

  });

  socket.on('close', () => {
  
    console.log('Client disconnected');
  
  });

  socket.on('error', err => {
  
    console.error('Socket error:', err);
  
  });

//listen
}).listen(TCP_PORT, () =>
  
  console.log(`TCP listening on ${TCP_PORT}`)

);

//HTTP server
http.createServer((req, res) => {

  if (req.url === '/') {
    
    fs.createReadStream('index.html').pipe(res);
    return;
  
  }

  //SSE
  if (req.url === '/events') {

    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    });

    clients.push(res);

    req.on('close', () => {
    
      clients = clients.filter(c => c !== res);
    
    });

    return;
  }

  //circle handling
  if(req.url==='/circle' && req.method==='POST'){

    let body=''; 

    req.on('data',chunk=>body+=chunk);

    req.on('end',()=>{

      //parse circle data to JSON
      try {
      
        circle = JSON.parse(body);
      
      } catch (e) {
        
        console.error("Invalid JSON");
        res.writeHead(400);
        return res.end();
      
      }
      
      if (!circle.center || typeof circle.radius !== 'number') {
      
        console.error("Bad circle format");
        res.writeHead(400);
        return res.end();
      
      }

      //debugging
      console.log("Updated circle:", circle.radius, circle.center.lat, circle.center.lon);

      res.writeHead(200); res.end();

    });

    return;

  }
  
  res.writeHead(404);
  res.end();

//listen
}).listen(HTTP_PORT, () =>
  
  console.log(`HTTP server on ${HTTP_PORT}`)

);

module.exports = haversine