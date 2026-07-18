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

// copy buttons on code blocks
(function(){
  document.querySelectorAll('.content pre').forEach(function(pre){
    // wrap the scrollable <pre> so the button stays pinned while the code scrolls
    var wrap=document.createElement('div');
    wrap.className='codewrap';
    pre.parentNode.insertBefore(wrap,pre);
    wrap.appendChild(pre);
    var btn=document.createElement('button');
    btn.type='button';btn.className='copy-btn';btn.textContent='Copy';
    btn.addEventListener('click',function(){
      var text=(pre.querySelector('code')||pre).textContent;
      function done(){btn.textContent='Copied';setTimeout(function(){btn.textContent='Copy';},1500);}
      function fallback(){
        var ta=document.createElement('textarea');
        ta.value=text;ta.style.position='fixed';ta.style.opacity='0';
        document.body.appendChild(ta);ta.select();
        try{document.execCommand('copy');done();}catch(e){}
        document.body.removeChild(ta);
      }
      if(navigator.clipboard&&navigator.clipboard.writeText){
        navigator.clipboard.writeText(text).then(done,fallback);
      }else{fallback();}
    });
    wrap.appendChild(btn);
  });
})();

// client-side search over the build-time index (assets/search-index.js)
(function(){
  var input=document.getElementById('search-input');
  var box=document.getElementById('search-results');
  if(!input||!box)return;
  var hits=[],active=-1;
  function close(){box.hidden=true;box.innerHTML='';hits=[];active=-1;}
  function mark(i){
    var links=box.querySelectorAll('.search-hit');
    if(links[active])links[active].classList.remove('active');
    active=i;
    if(links[active]){links[active].classList.add('active');links[active].scrollIntoView({block:'nearest'});}
  }
  function esc(s){return s.replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function run(){
    var idx=window.RCT_SEARCH_INDEX||[];
    var q=input.value.trim().toLowerCase();
    close();
    if(q.length<2)return;
    var terms=q.split(/\s+/);
    for(var p=0;p<idx.length&&hits.length<12;p++){
      var pg=idx[p];
      for(var h=0;h<pg.h.length&&hits.length<12;h++){
        var sec=pg.h[h];
        var hay=(pg.t+' '+sec.t+' '+sec.s).toLowerCase();
        var ok=terms.every(function(t){return hay.indexOf(t)>=0;});
        if(ok)hits.push({href:pg.p+'#'+sec.id,page:pg.t,head:sec.t,snip:sec.s});
      }
    }
    if(!hits.length){box.innerHTML='<div class="search-empty">No matches.</div>';box.hidden=false;return;}
    box.innerHTML=hits.map(function(x){
      return '<a class="search-hit" href="'+esc(x.href)+'">'
        +'<span class="hit-page">'+esc(x.page)+'</span> &rsaquo; '
        +'<span class="hit-head">'+esc(x.head)+'</span>'
        +'<span class="hit-snip">'+esc(x.snip)+'</span></a>';
    }).join('');
    box.hidden=false;
  }
  input.addEventListener('input',run);
  input.addEventListener('keydown',function(e){
    if(box.hidden)return;
    var n=box.querySelectorAll('.search-hit').length;
    if(e.key==='ArrowDown'&&n){e.preventDefault();mark((active+1)%n);}
    else if(e.key==='ArrowUp'&&n){e.preventDefault();mark((active-1+n)%n);}
    else if(e.key==='Enter'&&n){
      e.preventDefault();
      var pick=box.querySelectorAll('.search-hit')[active>=0?active:0];
      if(pick)window.location.href=pick.getAttribute('href');
    }
    else if(e.key==='Escape'){close();input.blur();}
  });
  box.addEventListener('click',function(e){
    if(e.target.closest&&e.target.closest('.search-hit'))setTimeout(close,0);
  });
  document.addEventListener('click',function(e){
    if(!e.target.closest||!e.target.closest('.search'))close();
  });
})();
