(function(){
  var order=['auto','light','dark'];
  var labels={auto:'Theme: Auto',light:'Theme: Light',dark:'Theme: Dark'};
  var btn=document.getElementById('theme-toggle');
  function cur(){try{return localStorage.getItem('rct-theme')||'auto';}catch(e){return 'auto';}}
  function apply(m){document.documentElement.setAttribute('data-theme',m);if(btn)btn.textContent=labels[m];}
  apply(cur());
  if(btn)btn.addEventListener('click',function(){
    var m=order[(order.indexOf(cur())+1)%3];
    try{localStorage.setItem('rct-theme',m);}catch(e){}
    apply(m);
  });
  // close mobile nav after following a link
  document.querySelectorAll('.sidebar a').forEach(function(a){
    a.addEventListener('click',function(){document.body.classList.remove('nav-open');});
  });
})();
