'use strict';
(() => {
  const $=selector=>document.querySelector(selector);
  const root=document.documentElement;
  let theme='light';try{theme=localStorage.getItem('dave-docs-theme')==='dark'?'dark':'light';}catch{}
  const themeButton=$('#theme');
  function applyTheme(){root.dataset.theme=theme;themeButton.setAttribute('aria-pressed',String(theme==='dark'));themeButton.setAttribute('aria-label',theme==='dark'?'切换浅色模式':'切换深色模式');}
  applyTheme();themeButton.addEventListener('click',()=>{theme=theme==='dark'?'light':'dark';applyTheme();try{localStorage.setItem('dave-docs-theme',theme);}catch{}});
  const sidebar=$('#sidebar'),menu=$('#menu'),backdrop=$('#nav-backdrop'),mobile=matchMedia('(max-width:840px)');
  function setMenu(open){document.body.classList.toggle('nav-open',open);menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'关闭导航':'打开导航');backdrop.hidden=!open;sidebar.inert=mobile.matches&&!open;if(open)sidebar.querySelector('a').focus();}
  menu.addEventListener('click',()=>setMenu(!document.body.classList.contains('nav-open')));
  backdrop.addEventListener('click',()=>{setMenu(false);menu.focus();});mobile.addEventListener('change',()=>setMenu(false));setMenu(false);
  let toastTimer;
  function toast(message){const target=$('#toast');target.textContent=message;target.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>{target.hidden=true;},2200);}
  for(const pre of document.querySelectorAll('pre')){
    const code=pre.querySelector('code');if(!code)continue;
    const button=document.createElement('button');button.className='copy-button';button.type='button';button.setAttribute('aria-label','复制指令');button.innerHTML='<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V4H4v12h4"/></svg>';
    button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(code.textContent);toast('已复制');}catch{toast('请选中指令手动复制');}});pre.append(button);
  }
  const dialog=$('#search-dialog'),input=$('#search-input'),results=$('#search-results'),hint=$('#search-hint');
  let index=null,indexPromise=null,selected=-1,returnFocus=null,searchVersion=0;
  async function loadIndex(){if(index)return index;if(!indexPromise)indexPromise=fetch('/search-index.json').then(r=>{if(!r.ok)throw new Error();return r.json();}).then(data=>{index=data;return data;}).catch(error=>{indexPromise=null;throw error;});return indexPromise;}
  function select(n){const rows=[...results.querySelectorAll('a')];if(!rows.length)return;selected=(n+rows.length)%rows.length;rows.forEach((a,i)=>a.classList.toggle('selected',i===selected));rows[selected].scrollIntoView({block:'nearest'});}
  function normalize(value){return value.toLowerCase().replace(/\s+/g,' ').trim();}
  async function search(){const version=++searchVersion;selected=-1;results.replaceChildren();const query=normalize(input.value);if(!query){hint.textContent='输入功能名，例如“名片”或“绑定”。';return;}
    hint.textContent='搜索中…';
    try{
      const data=await loadIndex();if(version!==searchVersion||!dialog.open)return;
      const tokens=query.split(' ');const found=data.map(item=>({item,score:tokens.reduce((n,t)=>n+(normalize(item.title).includes(t)?4:0)+(normalize(item.description).includes(t)?3:0),0)})).filter(({item})=>tokens.every(t=>normalize(item.keywords+' '+item.description).includes(t))).sort((a,b)=>b.score-a.score).slice(0,18);
      hint.textContent=found.length?`${found.length} 个结果`:'没有找到结果，试试指令别名或功能名。';
      for(const {item} of found){if(!item.url.startsWith('/')||item.url.startsWith('//'))continue;const a=document.createElement('a');a.className='search-result';a.href=item.url;const content=document.createElement('div'),title=document.createElement('strong'),description=document.createElement('p'),type=document.createElement('span');title.textContent=item.title;description.textContent=item.description;type.textContent=item.type;content.append(title,description);a.append(content,type);a.addEventListener('click',()=>dialog.close());results.append(a);}
      if(found.length)select(0);
    }catch{if(version===searchVersion)hint.textContent='搜索暂不可用，请使用左侧导航。';}
  }
  function openSearch(){returnFocus=document.activeElement;if(document.body.classList.contains('nav-open'))setMenu(false);dialog.showModal();input.focus();search();}
  document.querySelectorAll('[data-search]').forEach(b=>b.addEventListener('click',openSearch));$('#search-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>{searchVersion++;returnFocus?.focus();});dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
  input.addEventListener('input',search);input.addEventListener('keydown',e=>{if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();select(selected+(e.key==='ArrowDown'?1:-1));}if(e.key==='Enter'){const a=results.querySelectorAll('a')[selected];if(a){e.preventDefault();a.click();}}});
  document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();if(!dialog.open)openSearch();}if(e.key==='Escape'&&document.body.classList.contains('nav-open')){setMenu(false);menu.focus();}});
  if('IntersectionObserver' in window){const links=[...document.querySelectorAll('.toc nav a')];const observer=new IntersectionObserver(entries=>{for(const entry of entries){if(!entry.isIntersecting)continue;links.forEach(a=>a.setAttribute('aria-current',String(a.hash==='#'+entry.target.id)));}},{rootMargin:'-80px 0px -65% 0px'});document.querySelectorAll('.article h2[id]').forEach(h=>observer.observe(h));}
})();
