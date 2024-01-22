(function(){
  /// store our references
  var table = document.getElementById('target'),
      rows = table.getElementsByTagName('tr'),
      scroller = document.getElementById('scroller'),
      shown = [];
  /// core function, updates which rows are visible at what scroller offset
  var reveal = function(){
    var i, tr,
        s = scroller.step,
        p = +scroller.value,
        c = Math.floor(rows.length * s),
        l = rows.length,
        o = Math.floor(p * (l - c)) + 1;
      while ( (tr = shown.pop()) ) { tr.style.display = 'none'; }
      for ( i=0; i<c; i++ ) {
      if ( (tr = rows[o+i]) ) {
        shown.push(tr);
        tr.style.display = 'table-row';
      }
    }
  };
  /// update when the scroller is changed
  scroller.addEventListener('input', reveal);
  scroller.focus();
  /// transfer right and left arrow keys to the scroller (optional)
  window.addEventListener('keypress', function(e){
    if ( document.activeElement !== scroller ) {
      switch ( e.keyCode ) {
        case 37:
          scroller.value = parseFloat(scroller.value) - parseFloat(scroller.step);
          reveal();
        break;
        case 39:
          scroller.value = parseFloat(scroller.value) + parseFloat(scroller.step);
          reveal();
        break;
      }
    }
  });
  /// set the ball rolling
  reveal();
})();