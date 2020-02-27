const div_select_box = document.querySelector(".select-box");
const svg_stride = document.querySelectorAll(".cms-cascade-svg-viewer");
const input_fullscreen = document.querySelectorAll(".clipboard-fullscreen");
const xs = document.getElementById("js-cascade-btn-xs");
const sm = document.getElementById("js-cascade-btn-sm");
const md = document.getElementById("js-cascade-btn-md");
const lg = document.getElementById("js-cascade-btn-lg");
const xl = document.getElementById("js-cascade-btn-xl");
const max = document.getElementById("js-cascade-btn-max");

input_fullscreen.forEach(element => {
   element.addEventListener('click', function(event) {
      if ( div_select_box.classList.contains('clipboard-base')){
        div_select_box.classList.remove('clipboard-base');
      }
      else {
        div_select_box.classList.add('clipboard-base');
      }
    });
});

function parser_clipboards(elements, viewbox){
  elements.forEach(element => {
    element.setAttribute("viewBox",  viewbox);
  });
}

xs.addEventListener('click', function(event) {
  parser_clipboards(svg_stride ,'0 0 475 500');
  });
sm.addEventListener('click', function(event) {
  parser_clipboards(svg_stride ,'0 0 767 800');
  });
md.addEventListener('click', function(event) {
  parser_clipboards(svg_stride ,'0 0 991 900');
  });
lg.addEventListener('click', function(event) {
  parser_clipboards(svg_stride ,'0 0 1199 1400');
  });
xl.addEventListener('click', function(event) {
  parser_clipboards(svg_stride ,'0 0 2000 4000');
  });
max.addEventListener('click', function(event) {
  parser_clipboards(svg_stride ,'0 0 5000 10000');
  });
