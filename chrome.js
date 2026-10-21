(()=>{const b=document.getElementById('kBurger'),m=document.getElementById('kMenu');if(!b)return;
const set=o=>{b.setAttribute('aria-expanded',o);m.hidden=!o;document.body.style.overflow=o?'hidden':'';b.setAttribute('aria-label',o?'Close menu':'Open menu')};
b.addEventListener('click',()=>set(m.hidden));m.addEventListener('click',e=>{if(e.target.tagName==='A')set(false)});
addEventListener('keydown',e=>{if(e.key==='Escape')set(false)});})();
