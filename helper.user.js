// ==UserScript==
// @name         Chess Helper Bridge
// @match        https://www.chess.com/*
// @grant        none
// ==/UserScript==
(function(){
  'use strict';
  let lastFen='';
  let lastColor=null;
  let pending=null;
  const KEY='ch_helper_color';

  function boardEl(){ return document.querySelector('chess-board, wc-chess-board'); }

  function getFEN(){
    try{
      const b=boardEl();
      if(b && b.game && typeof b.game.getFEN==='function') return b.game.getFEN();
      if(b && b.controller && typeof b.controller.getFEN==='function') return b.controller.getFEN();
      if(window.chesscom && window.chesscom.game && typeof window.chesscom.game.getFEN==='function') return window.chesscom.game.getFEN();
    }catch(e){}
    return null;
  }

  function detectColor(){
    const b=boardEl();
    if(!b) return null;
    // board must have pieces rendered
    if(!b.querySelector('.piece, [class*="piece"]')) return null;
    const flipped=b.classList.contains('flipped');
    return flipped?'b':'w';
  }

  function getColor(){
    const c=detectColor();
    if(c){
      // require stable reading for 1.5s before trusting (board may flip on load)
      if(pending && pending.c===c && Date.now()-pending.t>1500){
        lastColor=c;
        localStorage.setItem(KEY,c);
        pending=null;
        return c;
      }
      if(!pending || pending.c!==c) pending={c:c, t:Date.now()};
    }
    return lastColor || localStorage.getItem(KEY);
  }

  function isMyTurn(fen){
    if(!fen) return false;
    const turn=fen.split(' ')[1];
    const my=getColor();
    if(!my) return false;
    return turn===my;
  }

  async function tick(){
    const fen=getFEN();
    if(!fen || fen===lastFen) return;
    if(!isMyTurn(fen)) return;
    lastFen=fen;
    try{
      const r=await fetch('http://127.0.0.1:8765/fen',{method:'POST',body:fen});
      const j=await r.json();
      if(j.move){
        highlight(j.move);
        const flip = boardEl() ? boardEl().classList.contains('flipped') : false;
        fetch('http://127.0.0.1:8765/click',{method:'POST',body:JSON.stringify({move:j.move,flip:flip}),headers:{'Content-Type':'application/json'}});
      }
    }catch(e){}
  }

  function highlight(uci){
    document.querySelectorAll('.ch-helper').forEach(e=>e.remove());
    const b=boardEl();
    if(!b) return;
    const sq=12.5;
    function center(s){
      const f=s.charCodeAt(0)-97, rk=parseInt(s[1])-1;
      const flip=b.classList.contains('flipped');
      return {x:(flip?7-f:f)*sq+sq/2, y:(flip?rk:7-rk)*sq+sq/2};
    }
    const from=center(uci.slice(0,2)), to=center(uci.slice(2,4));
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('class','ch-helper');
    svg.style.cssText=`position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none;z-index:9999;`;
    const defs=document.createElementNS('http://www.w3.org/2000/svg','defs');
    const marker=document.createElementNS('http://www.w3.org/2000/svg','marker');
    marker.setAttribute('id','arrow'); marker.setAttribute('markerWidth','10'); marker.setAttribute('markerHeight','10');
    marker.setAttribute('refX','5'); marker.setAttribute('refY','5'); marker.setAttribute('orient','auto');
    const path=document.createElementNS('http://www.w3.org/2000/svg','path');
    path.setAttribute('d','M0,0 L10,5 L0,10 z'); path.setAttribute('fill','red');
    marker.appendChild(path); defs.appendChild(marker); svg.appendChild(defs);
    const line=document.createElementNS('http://www.w3.org/2000/svg','line');
    line.setAttribute('x1',from.x+'%'); line.setAttribute('y1',from.y+'%');
    line.setAttribute('x2',to.x+'%'); line.setAttribute('y2',to.y+'%');
    line.setAttribute('stroke','red'); line.setAttribute('stroke-width','0.8%');
    line.setAttribute('marker-end','url(#arrow)');
    svg.appendChild(line);
    b.appendChild(svg);
  }

  setInterval(tick,300);
})();