(()=>{const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{rootMargin:'0px 0px -8% 0px',threshold:.06});
document.querySelectorAll('.rv,.room').forEach(el=>RM?el.classList.add('in'):io.observe(el));
const par=[...document.querySelectorAll('.phero-bg,.band img')],prog=document.querySelector('.prog i');let tk=false;
function f(){tk=false;const vh=innerHeight;if(!RM)par.forEach(el=>{const r=el.parentElement.getBoundingClientRect();if(r.bottom<0||r.top>vh)return;const c=(r.top+r.height/2-vh/2)/vh;el.style.setProperty('--py',(c*-60).toFixed(1)+'px')});
if(prog){const h=document.documentElement.scrollHeight-vh;prog.style.width=(h>0?scrollY/h*100:0)+'%'}}
addEventListener('scroll',()=>{if(!tk){tk=true;requestAnimationFrame(f)}},{passive:true});f();
const q=document.querySelector('[data-filter]');if(q){const cards=[...document.querySelectorAll('.pg .card')],cnt=document.querySelector('.hub-count');
const up=()=>{const v=q.value.trim().toLowerCase();let n=0;cards.forEach(c=>{const ok=!v||c.textContent.toLowerCase().includes(v);c.hidden=!ok;if(ok)n++});cnt.textContent=n+' of '+cards.length+' shown'};q.addEventListener('input',up);up();}
document.querySelectorAll('form[data-mailto]').forEach(fm=>fm.addEventListener('submit',e=>{e.preventDefault();if(!fm.reportValidity())return;const fd=new FormData(fm);let body='';for(const [k,v] of fd.entries())body+=k+': '+v+'\n';
location.href='mailto:solidhomesbyemmeline@gmail.com?subject='+encodeURIComponent('Website enquiry: '+document.title.split('|')[0].trim())+'&body='+encodeURIComponent(body)}));
})();
