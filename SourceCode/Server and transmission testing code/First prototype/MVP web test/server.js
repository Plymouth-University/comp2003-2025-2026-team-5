const net = require('net');
const http = require('http');
const fs = require('fs');

const TCP_PORT = 5000;
const HTTP_PORT = 3000;

let clients = [];

//converts NMEA string to decimal
function nmeaToDecimal(coord, dir) {

  if (!coord || !dir) return null;

  const degLen = (dir === 'N' || dir === 'S') ? 2 : 3;

  const deg = parseInt(coord.slice(0, degLen), 10);

  const min = parseFloat(coord.slice(degLen));

  let val = deg + min / 60;

  if (dir === 'S' || dir === 'W') val *= -1;

  return val;

}

//parses GNGGA sentences
function parseGNGGA(sentence) {

  const p = sentence.split(',');

  if (p[6] === '0') return; //no data

  const lat = nmeaToDecimal(p[2], p[3]);

  const lon = nmeaToDecimal(p[4], p[5]);

  if (lat == null || lon == null) return;

  //push to connected clients
  const data = `data:${lat},${lon}\n\n`;
  clients.forEach(res => res.write(data));

}

//function to parse CGNSINF
function parseCGNSINF(sentence) {

  //remove irrelevant header
  sentence = sentence.replace('+CGNSINF:', '');

  //split sentence by commas
  const p = sentence.split(',');
  
  //no data
  if (p[3] === '') return;

  //set latitude and longitude
  const lat = p[3];
  const lon = p[4];

  //no data
  if (lat == null || lon == null) return;

  //push to connected clients
  const data = `data:${lat},${lon}\n\n`;
  clients.forEach(res => res.write(data));
}

//---------------------------------

//TCP
net.createServer(socket => {
  console.log('Pico connected from', socket.remoteAddress);

  socket.on('data', d => {

    //logs raw data
    console.log('RAW BUFFER:', d);

    //converts data to ascii
    const text = d.toString('ascii');

    //converts lines to JSON to make them usable
    console.log('ASCII:', JSON.stringify(text));

    //splits lines up
    text.split(/\r?\n/).forEach(line => {

      //removes whitespace
      line = line.trim();

      //no lines present
      if (!line) return;

      //debug
      console.log('LINE:', line);

      //for Grove Air530 GPS unit
      if (line.startsWith('$GNGGA')) {
  
        parseGNGGA(line);
  
      }

      //for waveshare combined module
      if (line.startsWith('+CGNSINF:')) {
  
        parseCGNSINF(line);
  
      }

    });
  
  });

  socket.on('close', () => {
    
    //debug
    console.log('Pico disconnected');
  
  });

  socket.on('error', err => {
    console.error('Socket error:', err);
  });
}).listen(TCP_PORT, () =>

  //debug
  console.log(`TCP listening on ${TCP_PORT}`)
);

//---------------------------------

//HTTP
http.createServer((req, res) => {

  if (req.url === '/') {
    fs.createReadStream('index.html').pipe(res);
    return;
  }

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

  res.writeHead(404);
  res.end();

}).listen(HTTP_PORT, () =>
  console.log(`HTTP server on ${HTTP_PORT}`)
);