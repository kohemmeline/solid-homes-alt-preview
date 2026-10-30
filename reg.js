// Early-registration forms: posts to FormSubmit (email to solidhomesbyemmeline@gmail.com); optional Google Apps Script endpoint; mailto fallback.
(()=>{const TO='solidhomesbyemmeline@gmail.com',SHEET=window.REG_SHEET_URL||'';
document.querySelectorAll('form[data-reg]').forEach(fm=>fm.addEventListener('submit',async e=>{e.preventDefault();if(!fm.reportValidity())return;
const fd=new FormData(fm);if(fd.get('_honey'))return;const msg=fm.querySelector('.reg-msg'),btn=fm.querySelector('button');
const proj=fd.getAll('project').join(', '),units=fd.getAll('unit_type').join(', ');
if(!proj){msg.textContent='Please choose at least one project.';return}
const d={name:fd.get('name'),mobile:fd.get('mobile'),email:fd.get('email'),projects:proj,unit_types:units||'Not sure yet',pdpa_consent:'yes',consent_text:fm.querySelector('[name=pdpa_consent]').closest('label').textContent.trim(),consent_timestamp:new Date(Date.now()+288e5).toISOString().slice(0,19)+'+08:00',page:location.href,_subject:'Early registration: '+proj,_template:'table',_captcha:'false'};
btn.disabled=true;msg.removeAttribute('data-ok');msg.textContent='Sending…';let ok=false;
if(SHEET){try{await fetch(SHEET,{method:'POST',mode:'no-cors',body:JSON.stringify(d)});ok=true}catch(_){}}
try{const r=await fetch('https://formsubmit.co/ajax/'+TO,{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(d)});const j=await r.json().catch(()=>({}));if(r.ok&&String(j.success)==='true')ok=true}catch(_){}
btn.disabled=false;
if(ok){fm.reset();msg.setAttribute('data-ok','');msg.textContent='Thank you, you are registered. Emmeline will send you the brochure and preview details when they are released.';return}
let b='';for(const k of['name','mobile','email','projects','unit_types','pdpa_consent','consent_timestamp','page'])b+=k+': '+d[k]+'\n';
msg.textContent='Opening your email app to send the registration. If nothing opens, WhatsApp 8275 4135.';
location.href='mailto:'+TO+'?subject='+encodeURIComponent(d._subject)+'&body='+encodeURIComponent(b)}))})();
