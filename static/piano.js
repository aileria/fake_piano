var canvas = null;

window.onload = function() {
  canvas = document.getElementById("canvas");
  update();
  requestAnimationFrame(update);
};

function receiveActiveKeys(response) {
  var obj = JSON.parse(response);
  DrawKeyboard(canvas, obj);
}

function httpGetAsync(url, callback) {
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() { 
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
        callback(xmlHttp.responseText);
      }else {
        DrawKeyboard(canvas, []);
      }
  }
  xmlHttp.open("GET", url, true); // true for asynchronous 
  xmlHttp.send(null);
}

function update() {
  httpGetAsync('/active_keys', receiveActiveKeys);
}

function DrawKeyboard(canvas, activeKeys) {
  var NUM_KEYS = 88;
  var NUM_WHITE_KEYS = 52;
  var X_BORDER = 0;
  var Y_BORDER = 0;

  var width = canvas.width - (X_BORDER * 2);
  var height = canvas.height - (Y_BORDER * 2);
  var ctx = canvas.getContext("2d");

  var WHITE_KEY_WIDTH = (width / NUM_WHITE_KEYS);
  var BLACK_KEY_WIDTH = WHITE_KEY_WIDTH * .75
  var BLACK_KEY_HEIGHT = height * .66

  function DrawRectWithBorder(X, Y, Width, Height, Color1, Color2) {
    //draw border
    ctx.fillStyle = Color1;
    ctx.fillRect(X, Y, Width, Height);
    //draw inside
    ctx.fillStyle = Color2;
    ctx.fillRect(X + 1, Y + 1, Width - 2, Height - 2);
  }

  // draws a back key, based on whiteKeyIndex, where 0 <= WhiteKeyIndex < 52 
  function drawBlackKey(whiteKeyIndex, shouldBeRed = false) {
    if (!shouldBeRed) {
      C1 = "rgb(0,0,0)";      // black
      C2 = "rgb(50,50,50)";    // ??

      DrawRectWithBorder(X_BORDER + ((whiteKeyIndex + 1) * WHITE_KEY_WIDTH) - (BLACK_KEY_WIDTH / 2), Y_BORDER, BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT, C1, C2);
    }
    else {
      C1 = "rgb(0,0,0)";      // black
      C2 = "rgb(255,0,0)";    // red
      DrawRectWithBorder(X_BORDER + ((whiteKeyIndex + 1) * WHITE_KEY_WIDTH) - (BLACK_KEY_WIDTH / 2), Y_BORDER, BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT, C1, C2);
    }

  }

  function drawWhiteKey(WhiteKeyIndex, shouldBeRed = false) {

    if (!shouldBeRed) {
      C1 = "rgb(0,0,0)";      // black
      C2 = "rgb(255,255,255)";  // white
      DrawRectWithBorder(X_BORDER + (WhiteKeyIndex * WHITE_KEY_WIDTH), Y_BORDER, WHITE_KEY_WIDTH, height, C1, C2);
    } else {
      C1 = "rgb(0,0,0)";      // black
      C2 = "rgb(255,0,0)";    // red
      DrawRectWithBorder(X_BORDER + (WhiteKeyIndex * WHITE_KEY_WIDTH), Y_BORDER, WHITE_KEY_WIDTH, height, C1, C2);

    }
  }

  function keyType(isBlack, White_Index) {
    this.isBlack = isBlack;
    this.White_Index = White_Index
  }

  function AbsoluteToKeyInfo(AbsoluteNoteNum) {

    var keys = new Array(NUM_KEYS);

    keys[0] = new keyType(false, 0);      // a
    keys[1] = new keyType(true, 0);      // a#
    keys[2] = new keyType(false, 1);      // b
    base = 3;

    NumOctaves = 8
    for (counter = 0; counter < NumOctaves; counter++) {
      octave_offset = 7 * counter;

      keys[base + 0] = new keyType(false, octave_offset + 2); // c
      keys[base + 1] = new keyType(true, octave_offset + 2); // c#
      keys[base + 2] = new keyType(false, octave_offset + 3); // d
      keys[base + 3] = new keyType(true, octave_offset + 3); // d#
      keys[base + 4] = new keyType(false, octave_offset + 4); // e
      keys[base + 5] = new keyType(false, octave_offset + 5); // f
      keys[base + 6] = new keyType(true, octave_offset + 5); // f#
      keys[base + 7] = new keyType(false, octave_offset + 6); // g
      keys[base + 8] = new keyType(true, octave_offset + 6); // g#
      keys[base + 9] = new keyType(false, octave_offset + 7); // a
      keys[base + 10] = new keyType(true, octave_offset + 7)  // a#
      keys[base + 11] = new keyType(false, octave_offset + 8); // b

      base += 12;
    }

    return keys[AbsoluteNoteNum];
  }

  // Draw all white keys
  for (i = 0; i < NUM_WHITE_KEYS; i++) {
    drawWhiteKey(i, false);
  }

  // Draw active white keys
  for (index = 0; index < NUM_KEYS; index++) {
    if (activeKeys.includes(index)) {
      KeyLookup = AbsoluteToKeyInfo(index);
      if (!KeyLookup.isBlack)
        drawWhiteKey(KeyLookup.White_Index, true);
    }
  }

  // Draw lowest a# manually (active or not)
  drawBlackKey(0, activeKeys.includes(1));

  // Draw all black keys
  numOctaves = 7;
  curWhiteNoteIndex = 2;

  for (octave = 0; octave < numOctaves; octave++) {
    for (i = 0; i < 5; i++) {
      drawBlackKey(curWhiteNoteIndex, false);
      if (i == 1 || i == 4)
        curWhiteNoteIndex += 2;
      else
        curWhiteNoteIndex += 1;
    }
  }

  // Draw active black keys
  for (index = 0; index < NUM_KEYS; index++) {
    // and if we find any black keys that are supposed to be red, then draw them in red...
    if (activeKeys.includes(index)) {
      KeyLookup = AbsoluteToKeyInfo(index);
      if (KeyLookup.isBlack)
        drawBlackKey(KeyLookup.White_Index, true);
    }
  }

}