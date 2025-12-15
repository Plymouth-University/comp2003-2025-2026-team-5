const ROUNDS = 20;

const SBOX = [
    99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118,
    202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192,
    183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21,
    4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117,
    9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132,
    83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207,
    208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168,
    81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210,
    205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115,
    96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219,
    224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121,
    231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8,
    186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138,
    112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158,
    225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223,
    140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22
];

var INV_SBOX = [];
for (var idx = 0; idx < 256; idx++) {
    INV_SBOX[SBOX[idx]] = idx;
}

// intiger to Bytes premade code:
function intToBytes(n) {
    var arr = [];
    arr[0] = (n >> 24) & 0xFF;
    arr[1] = (n >> 16) & 0xFF;
    arr[2] = (n >> 8) & 0xFF;
    arr[3] = n & 0xFF;
    return arr;
}
function bytesToInt(bytes) {
    if (!bytes || bytes.length < 4) return 0;
    return ((bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]) >>> 0;
}
// random IV
function generateIV() {
    var iv = [];
    if (typeof crypto !== "undefined" && crypto.getRandomValues) {
        var tmp = new Uint8Array(16);
        crypto.getRandomValues(tmp);
        for (var i = 0; i < 16; i++) iv[i] = tmp[i];
    } else {
        // fallback for environments without crypto
        for (var i = 0; i < 16; i++) iv[i] = Math.floor(Math.random() * 256);
    }
    return iv;
}

//difuse function

const PERMUTATION = [
    0,5,10,15,
    4,9,14,3,
    8,13,2,7,
    12,1,6,11
];

var INV_PERMUTATION = [];
for (var i = 0; i < 16; i++) {
    INV_PERMUTATION[PERMUTATION[i]] = i;
}

//encrypt 4 coordinates (NSEW)
function encryptBounds(bounds, key) {
    const SCALE = 1e6;
    var state = [];
    for (var i = 0; i < bounds.length; i++) {
        var val = Math.round(bounds[i] * SCALE);
        var bytes = intToBytes(val);
        for (var j = 0; j < 4; j++) {
            state.push(bytes[j]);
        }
    }

    //Iv
    var iv = generateIV();
    for (var k = 0; k < 16; k++) {
        state[k] = state[k] ^ iv[k];
    }

    for (var round = 0; round < ROUNDS; round++) {
        // subsituting 
        for (var m = 0; m < 16; m++) {
            var kbyte = key[(m + round) % key.length];
            state[m] = SBOX[state[m] ^ kbyte];
        }

        // diffusion
        var temp = [];
        for (var n = 0; n < 16; n++) {
            temp[n] = state[PERMUTATION[n]];
        }
        for (var n2 = 0; n2 < 16; n2++) {
            state[n2] = temp[n2];
        }
    }

    //iv + cipher text:
    return iv.concat(state);
}


//decrypt 4 coordinates (NSEW)

function decryptBounds(encrypted, key) {
    const SCALE = 1e6;

    // remove iv
    var iv = [];
    for (var i = 0; i < 16; i++) iv[i] = encrypted[i];
    var state = [];
    for (var i = 16; i < 32; i++) state.push(encrypted[i]);
    
    for (var round = ROUNDS - 1; round >= 0; round--) {
        // Reverse diffusion
        var temp = [];
        for (var n = 0; n < 16; n++) {
            temp[n] = state[INV_PERMUTATION[n]];
        }
        for (var n2 = 0; n2 < 16; n2++) {
            state[n2] = temp[n2];
        }

        for (var m = 0; m < 16; m++) {
            var kbyte = key[(m + round) % key.length];
            state[m] = INV_SBOX[state[m]] ^ kbyte;
        }
    }

    // Remove IV
    for (var k = 0; k < 16; k++) {
        state[k] = state[k] ^ iv[k];
    }

    var coords = [];
    for (var i = 0; i < 16; i += 4) {
        coords.push(bytesToInt([state[i], state[i+1], state[i+2], state[i+3]]) / SCALE);
    }

    return {
        north: coords[0],
        east: coords[1],
        south: coords[2],
        west: coords[3]
    };
}

// interface (can be removed when we inplement , only for testing)
var KEY = [0x13, 0x37, 0x42, 0x99];

var action = prompt("Type 'e' to encrypt or 'd' to decrypt:");

if (action === "e") {
    var north = parseFloat(prompt("Enter North:"));
    var east = parseFloat(prompt("Enter East:"));
    var south = parseFloat(prompt("Enter South:"));
    var west = parseFloat(prompt("Enter West:"));

    var encrypted = encryptBounds([north, east, south, west], KEY);
    alert("Encrypted bytes:\n" + JSON.stringify(encrypted));

} else if (action === "d") {
    var input = prompt(
        "Enter encrypted byte array ( remove [] otherwise innacuracy):"
    );

    var encrypted = input.split(",").map(function(n) { return parseInt(n.trim(), 10); });
    var decrypted = decryptBounds(encrypted, KEY);

    alert(
        " North: " + decrypted.north + "\n" +
        " East: " + decrypted.east + "\n" +
        " South: " + decrypted.south + "\n" +
        " West: " + decrypted.west
    );
} else {
    alert("Invalid option selected.");
}

