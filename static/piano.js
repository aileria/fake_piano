var KEY_COUNT = 88

var c
var ctx

window.onload = function load() {
    c = document.getElementById("canvas")
    const h = (c.height = 60);
    const w = (c.width = 500);
    const padding = 10;
    const key_count = 20;
    ctx = c.getContext("2d");
    const sz = (w - padding * 2) / key_count;
    ctx.fillStyle = "#FF0000";
    ctx.fillRect(0, 0, w, 75);
}

function render ( keyNote, keyBlackNote ) {
  // set width and height of piano canvas (also clear canvas after re-render)
  c.width = 1470;
  c.height = 400;	

  // draw piano notes
  for( i = 0; i < 21; i++ ) {
    // white notes
    ctx.strokeRect( noteWidth * i, 0, noteWidth, 400 - ( keyNote == i ? 20 : 0 ) );
    // middle notes
    notesMiddle[ i ] && ctx.fillRect( noteWidth * i - 20, 0, 40, middleCFrequency - ( keyBlackNote == i ? 20 : 0 ) );
  }
}
requestAnimationFrame(render([2,8],[5]))