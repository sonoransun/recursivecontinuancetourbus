(function(){
  'use strict';
  var root=document.documentElement;

  // ---- theme: auto -> light -> dark ----
  var order=['auto','light','dark'];
  var labels={auto:'Auto',light:'Light',dark:'Dark'};
  var btn=document.getElementById('theme-toggle');
  function cur(){try{return localStorage.getItem('rct-theme')||'auto';}catch(e){return 'auto';}}
  function apply(m){
    root.setAttribute('data-theme',m);
    if(!btn)return;
    btn.setAttribute('data-mode',m);
    var t=btn.querySelector('.tt-label'); if(t)t.textContent=labels[m];
    btn.setAttribute('aria-label','Color theme: '+labels[m]+'. Click to change.');
  }
  apply(cur());
  if(btn)btn.addEventListener('click',function(){
    var m=order[(order.indexOf(cur())+1)%3];
    try{localStorage.setItem('rct-theme',m);}catch(e){}
    apply(m);
  });

  // ---- mobile navigation ----
  var menu=document.querySelector('.menu-btn');
  function setNav(open){
    document.body.classList.toggle('nav-open',open);
    if(menu)menu.setAttribute('aria-expanded',open?'true':'false');
  }
  if(menu)menu.addEventListener('click',function(){setNav(!document.body.classList.contains('nav-open'));});
  document.querySelectorAll('.sidebar a').forEach(function(a){
    a.addEventListener('click',function(){setNav(false);});
  });
  document.addEventListener('keydown',function(e){if(e.key==='Escape')setNav(false);});
  // keep the current station in view inside a long sidebar
  var on=document.querySelector('.sidebar .on');
  if(on&&on.scrollIntoView){try{on.scrollIntoView({block:'nearest'});}catch(e){}}
})();

// ---- copy buttons (terminals copy their commands, without prompts) ----
(function(){
  document.querySelectorAll('.content pre').forEach(function(pre){
    var wrap=document.createElement('div');
    wrap.className='codewrap';
    pre.parentNode.insertBefore(wrap,pre);
    wrap.appendChild(pre);
    var btn=document.createElement('button');
    btn.type='button';btn.className='copy-btn';btn.textContent='Copy';
    btn.addEventListener('click',function(){
      var text;
      var cmds=pre.querySelectorAll('.tc');
      if(cmds.length){text=Array.prototype.map.call(cmds,function(c){return c.textContent;}).join('\n');}
      else{text=(pre.querySelector('code')||pre).textContent;}
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

// ---- reading progress + "on this page" scrollspy ----
(function(){
  var bar=document.querySelector('.progress i');
  var links=document.querySelectorAll('.toc-rail a[href^="#"]');
  var byId={};
  Array.prototype.forEach.call(links,function(a){byId[decodeURIComponent(a.getAttribute('href').slice(1))]=a;});
  var heads=Array.prototype.filter.call(document.querySelectorAll('.content h2[id], .content h3[id]'),function(h){return byId[h.id];});
  var active=null, ticking=false;
  function update(){
    ticking=false;
    var doc=document.documentElement;
    var max=doc.scrollHeight-window.innerHeight;
    if(bar)bar.style.width=(max>0?Math.min(100,Math.max(0,window.scrollY/max*100)):0)+'%';
    if(!heads.length)return;
    var y=window.scrollY+110, cur=null;
    for(var i=0;i<heads.length;i++){ if(heads[i].getBoundingClientRect().top+window.scrollY<=y)cur=heads[i]; else break; }
    var link=cur?byId[cur.id]:null;
    if(link!==active){
      if(active)active.classList.remove('active');
      active=link;
      if(active){active.classList.add('active');
        var rail=document.querySelector('.toc-rail');
        if(rail){var r=active.getBoundingClientRect(),rr=rail.getBoundingClientRect();
          if(r.top<rr.top||r.bottom>rr.bottom)rail.scrollTop+=r.top-rr.top-rr.height/3;}}
    }
  }
  window.addEventListener('scroll',function(){if(!ticking){ticking=true;window.requestAnimationFrame(update);}},{passive:true});
  window.addEventListener('resize',update);
  update();
})();

// ---- client-side search over the build-time index (assets/search-index.js) ----
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
    var scored=[];
    for(var p=0;p<idx.length;p++){
      var pg=idx[p];
      for(var h=0;h<pg.h.length;h++){
        var sec=pg.h[h];
        var head=sec.t.toLowerCase();
        var hay=(pg.t+' '+sec.t+' '+sec.s).toLowerCase();
        if(!terms.every(function(t){return hay.indexOf(t)>=0;}))continue;
        var score=terms.reduce(function(s,t){return s+(head.indexOf(t)>=0?2:0);},0);
        scored.push({score:score,order:scored.length,href:pg.p+'#'+sec.id,page:pg.t,head:sec.t,snip:sec.s});
      }
    }
    scored.sort(function(a,b){return b.score-a.score||a.order-b.order;});
    hits=scored.slice(0,14);
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
  // "/" (or Ctrl/Cmd-K) jumps to search from anywhere that is not a text field
  document.addEventListener('keydown',function(e){
    var t=e.target, typing=t&&(t.tagName==='INPUT'||t.tagName==='TEXTAREA'||t.isContentEditable);
    if((e.key==='/'&&!typing)||((e.ctrlKey||e.metaKey)&&(e.key==='k'||e.key==='K'))){
      e.preventDefault();input.focus();input.select();
    }
  });
})();
