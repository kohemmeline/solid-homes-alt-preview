(()=>{const btn=document.getElementById('snd');if(!btn)return;
const zone=[document.querySelector('.film'),document.getElementById('walk')].filter(Boolean);
const SRC='/solid-homes-alt-preview/assets/ambient-pad.m4a',VOL=0.32;let ctx,gain,src,on=false,loading=false,inZone=true;
function ramp(v,s){if(!gain)return;const t=ctx.currentTime;gain.gain.cancelScheduledValues(t);gain.gain.setValueAtTime(gain.gain.value,t);gain.gain.linearRampToValueAtTime(v,t+s)}
function target(){return on&&inZone?VOL:(on?0.0001:0)}
async function start(){if(loading)return;loading=true;ctx=new (window.AudioContext||window.webkitAudioContext)();gain=ctx.createGain();gain.gain.value=0;gain.connect(ctx.destination);
const buf=await ctx.decodeAudioData(await (await fetch(SRC)).arrayBuffer());src=ctx.createBufferSource();src.buffer=buf;src.loop=true;src.connect(gain);src.start();loading=false}
function label(){btn.setAttribute('aria-pressed',on);btn.querySelector('.snd-t').textContent=on?'Sound off':'Sound on';btn.setAttribute('aria-label',on?'Sound off: mute ambient music':'Sound on: play ambient music')}
btn.addEventListener('click',async()=>{on=!on;label();if(on){if(!ctx)await start();await ctx.resume();ramp(target(),2.5)}else{ramp(0,0.8)}});
function check(){const vh=innerHeight;inZone=zone.some(z=>{const r=z.getBoundingClientRect();return r.bottom>vh*0.25&&r.top<vh*0.75})||scrollY<innerHeight*0.6;if(ctx&&on)ramp(target(),inZone?2:2.5)}
let tk;addEventListener('scroll',()=>{clearTimeout(tk);tk=setTimeout(check,120)},{passive:true});
document.addEventListener('visibilitychange',()=>{if(ctx&&on){document.hidden?ctx.suspend():ctx.resume()}});
})();
