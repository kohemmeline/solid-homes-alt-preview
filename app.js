(()=>{
const root=document.documentElement,walk=document.getElementById('walk'),scene=document.getElementById('scene');
const rooms=[...document.querySelectorAll('.room')],label=document.getElementById('hudLabel'),bar=document.getElementById('hudBar');
const names=['Arrival','Living','Study','Balcony'],D=1400,reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
rooms.forEach(r=>r.style.setProperty('--i',r.dataset.i));
let tick=false;
function frame(){tick=false;const y=scrollY;root.style.setProperty('--s',Math.min(y,1200));
 const r=walk.getBoundingClientRect(),len=walk.offsetHeight-innerHeight;
 const p=Math.min(Math.max(-r.top/len,0),1),z=p*(rooms.length-1)*D;
 scene.style.transform=reduce?'none':`translateZ(${z}px) rotateY(${innerWidth<820?0:Math.sin(p*Math.PI*3)*4}deg)`;
 rooms.forEach((el,i)=>{const d=z-i*D;el.style.opacity=reduce?(Math.round(p*3)===i?1:0):Math.max(0,Math.min(1,1-Math.abs(d)/D*1.1,(d+D*1.6)/D))});
 const ops=rooms.map(el=>+el.style.opacity||0);const idx=reduce?Math.round(p*3):ops.indexOf(Math.max(...ops));
 label.textContent=`0${idx+1} / ${names[idx]}`;bar.style.width=(p*100)+'%';}
addEventListener('scroll',()=>{if(!tick){tick=true;requestAnimationFrame(frame)}},{passive:true});
addEventListener('resize',frame);frame();
document.getElementById('enq').addEventListener('submit',e=>{e.preventDefault();const f=new FormData(e.target);
 const body=`Name: ${f.get('name')}\nMobile: ${f.get('mobile')}\nInterest: ${f.get('interest')}\n\n${f.get('message')||''}\n\nPDPA consent: yes`;
 location.href='mailto:solidhomesbyemmeline@gmail.com?subject='+encodeURIComponent('Website enquiry: '+f.get('interest'))+'&body='+encodeURIComponent(body);});
})();
