(()=>{
const root=document.documentElement,walk=document.getElementById('walk'),scene=document.getElementById('scene');
const rooms=[...document.querySelectorAll('.room')],label=document.getElementById('hudLabel'),bar=document.getElementById('hudBar');
const names=['Your Finances','New Launches','Market Reports','Upgrade Plans'],D=1400,N=rooms.length-1;
const mqR=matchMedia('(prefers-reduced-motion: reduce)'),mqM=matchMedia('(max-width:768px), (pointer:coarse)');
rooms.forEach(r=>r.style.setProperty('--i',r.dataset.i));
const clamp=(v,a,b)=>Math.min(Math.max(v,a),b),ss=t=>t*t*(3-2*t);
// mobile: each panel rests in a hold zone, then eases to the next
function hold(p){const t=p*N,k=Math.min(Math.floor(t),N-1),f=t-k,h=.28;return (k+ss(clamp((f-h)/(1-2*h),0,1)))/N}
let cur=0,target=0,raf=0,lastIdx=-1;
function measure(){const r=walk.getBoundingClientRect(),len=walk.offsetHeight-innerHeight;return clamp(-r.top/Math.max(len,1),0,1)}
function render(p){const mob=mqM.matches,q=mob?hold(p):p,z=q*N*D;
 scene.style.transform=`translateZ(${z}px) rotateY(${innerWidth<820?0:Math.sin(q*Math.PI*3)*4}deg)`;
 let best=0,bi=0;rooms.forEach((el,i)=>{const d=z-i*D;const o=mob?clamp(1-Math.abs(d)/D*1.6,0,1):Math.max(0,Math.min(1,1-Math.abs(d)/D*1.1,(d+D*1.6)/D));el.style.opacity=o;if(o>best){best=o;bi=i}});
 if(bi!==lastIdx){label.textContent=`0${bi+1} / ${names[bi]}`;lastIdx=bi}bar.style.width=(p*100)+'%';}
function loop(){raf=0;const k=mqM.matches?.1:.25;cur+=(target-cur)*k;if(Math.abs(target-cur)<.0005)cur=target;render(cur);if(cur!==target)raf=requestAnimationFrame(loop)}
function onScroll(){root.style.setProperty('--s',Math.min(scrollY,1200));
 if(mqR.matches){const i=0;return}target=measure();if(!raf)raf=requestAnimationFrame(loop)}
function setMode(){root.classList.toggle('walk-static',mqR.matches);if(mqR.matches){scene.style.transform='none';rooms.forEach(el=>el.style.opacity=1)}else{cur=target=measure();render(cur)}}
addEventListener('scroll',onScroll,{passive:true});addEventListener('resize',onScroll,{passive:true});
mqR.addEventListener?.('change',setMode);mqM.addEventListener?.('change',onScroll);setMode();onScroll();
document.getElementById('enq').addEventListener('submit',e=>{e.preventDefault();const f=new FormData(e.target);
 const body=`Name: ${f.get('name')}\nMobile: ${f.get('mobile')}\nInterest: ${f.get('interest')}\n\n${f.get('message')||''}\n\nPDPA consent: yes`;
 location.href='mailto:solidhomesbyemmeline@gmail.com?subject='+encodeURIComponent('Website enquiry: '+f.get('interest'))+'&body='+encodeURIComponent(body);});
})();
