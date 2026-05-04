const net = require('net');
const http = require('http');
const fs = require('fs');
const { spawn } = require('child_process'); //python process

const TCP_PORT = 5000;
const HTTP_PORT = 3000;

let clients = [];
let circle = null; //only one circle can exist

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
function parseCGNSINF(sentence) {

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
  const data = `data:${lat},${lon}\n\n`;
  clients.forEach(res => res.write(data));

}

net.createServer(socket => {
  
  console.log('Client connected from', socket.remoteAddress);

  //spawn python process
  const proc = spawn('python3', ['crypto_ecdh_ascon.py'], { cwd: __dirname });

  proc.stderr.on('data', d => {
    
    console.error('crypto stderr:', d.toString());
  
  });

  //accumulate python returns
  let pyBuffer = '';
  let gotPub = false;

  //receive key
  proc.stdout.on('data', d => {
    
    //stringify data
    pyBuffer += d.toString('utf8');

    //split lines by headers
    let lines = pyBuffer.split(/\r?\n/);
    pyBuffer = lines.pop();

    lines.forEach(line => {
      
      line = line.trim();
      if (!line) return;
      
      //no public key acquired yet
      if (!gotPub) {

        //first line is server pubkey JSON
        gotPub = true;
        console.log('Server pubkey JSON:', line);
        socket.write(line + '\n');
        return;
      
      }

      //subsequent lines are decrypted plaintext
      console.log('DECRYPTED:', line);
      if (line.startsWith('+CGNSINF:')) {

        parseCGNSINF(line);

      }
    });
  });

  //accumulate incoming data
  let devBuffer = '';

  socket.on('data', d => {
    
    devBuffer += d.toString('utf8');

    //split by headers
    let lines = devBuffer.split(/\r?\n/);
    devBuffer = lines.pop();

    lines.forEach(line => {
      
      line = line.trim();
      if (!line) return;

      //validate JSON
      try {
        
        JSON.parse(line);
      
      } catch {
      
        console.error('Invalid JSON', line);
        return;
      
      }

      proc.stdin.write(line + '\n');

    });
  });

  socket.on('close', () => {
    
    console.log('Client disconnected');
    proc.stdin.end();
  
  });

  socket.on('error', err => {
    
    console.error('Socket error:', err);
    proc.stdin.end();
  
  });

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