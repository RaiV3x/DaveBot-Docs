"""Build the public DaveBot command guide. Python standard library only."""
import html
import json
from pathlib import Path
import shutil
import hashlib
import os
from datetime import date

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist'
E=lambda value:html.escape(str(value),quote=True)
commands=json.loads((ROOT/'content/commands.json').read_text(encoding='utf-8'))
pages=json.loads((ROOT/'content/pages.json').read_text(encoding='utf-8'))
page_map={p['id']:p for p in pages}
CSS_VERSION=hashlib.sha256((ROOT/'assets/style.css').read_bytes()).hexdigest()[:10]
JS_VERSION=hashlib.sha256((ROOT/'assets/app.js').read_bytes()).hexdigest()[:10]
order=['guide','commands','accounts','mysekai','personal-info','tracking','faq','admin']
titles={p['id']:p['title'] for p in pages}|{'commands':'全部指令','home':'使用指南'}
ICONS={
 'search':'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
 'menu':'<path d="M4 6h16M4 12h16M4 18h16"/>',
 'theme':'<path d="M20.8 13.2A9 9 0 0 1 10.8 3.2 9 9 0 1 0 20.8 13.2Z"/>',
 'arrow':'<path d="M5 12h14m-5-5 5 5-5 5"/>',
 'copy':'<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V4H4v12h4"/>',
 'close':'<path d="m6 6 12 12M18 6 6 18"/>'}
def icon(name):return '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'+ICONS[name]+'</svg>'
def link(page):return '/'+page+'/' if page!='home' else '/'
def code(value):return '<pre><code>'+E(value)+'</code></pre>'
def heading(identity,title):return '<h2 id="'+E(identity)+'">'+E(title)+'<a class="anchor" href="#'+E(identity)+'" aria-label="链接到'+E(title)+'">#</a></h2>'
def command_block(c):
    identity='cmd-'+c['id']
    result='<section class="command-section">'+heading(identity,c['title'])
    result+='<p>'+E(c['description'])+'</p>'+code(c['usage'])
    if c.get('access'):result+='<p class="access-label">'+E(c['access'])+'</p>'
    if c.get('aliases'):result+='<p class="aliases">别名 '+' '.join('<code>'+E(a)+'</code>' for a in c['aliases'])+'</p>'
    if c.get('arguments'):
        result+='<div class="table-wrap"><table><thead><tr><th>参数</th><th>类型</th><th>说明</th></tr></thead><tbody>'
        result+=''.join('<tr><td><code>'+E(a)+'</code></td><td class="nowrap">'+E(b)+'</td><td>'+E(d)+'</td></tr>' for a,b,d in c['arguments'])+'</tbody></table></div>'
    if c.get('examples'):result+='<h3>示例</h3><div class="example-list">'+''.join(code(example) for example in c['examples'])+'</div>'
    if c.get('notes'):result+='<ul class="command-notes">'+''.join('<li>'+E(n)+'</li>' for n in c['notes'])+'</ul>'
    return result+'</section>'
def sidebar(current):
    groups=[('开始',['guide','commands']),('功能',['accounts','mysekai','personal-info','tracking']),('支持',['faq','admin'])]
    return ''.join('<div class="nav-group"><p>'+label+'</p>'+''.join('<a '+('class="active" aria-current="page" ' if current==p else '')+'href="'+link(p)+'">'+E(titles[p])+'</a>' for p in ids)+'</div>' for label,ids in groups)
def table_of_commands():
    result=''
    for category in ['accounts','mysekai','personal-info','tracking','admin']:
        result+=heading(category,titles[category])+'<div class="table-wrap"><table class="command-index"><thead><tr><th>指令</th><th>用途</th></tr></thead><tbody>'
        for c in commands:
            if c['category']!=category:continue
            result+='<tr><td><a href="'+link(category)+'#cmd-'+c['id']+'"><code>'+E(c['usage'])+'</code></a></td><td>'+E(c['title'])+(' <span class="small-label">管理员</span>' if c.get('access') else '')+'</td></tr>'
        result+='</tbody></table></div>'
    return result
def shell(current,title,description,body,toc,eyebrow='使用文档'):
    previous=next_page=None
    if current in order:
        n=order.index(current)
        previous=order[n-1] if n else 'home'
        next_page=order[n+1] if n<len(order)-1 else None
    pager='<nav class="pager" aria-label="相邻文档">'
    for direction,target in [('上一篇',previous),('下一篇',next_page)]:
        pager+=('<a href="'+link(target)+'"><span>'+direction+'</span><strong>'+titles[target]+'</strong></a>') if target else '<span></span>'
    pager+='</nav>' if previous or next_page else '</nav>'
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · DaveBot 文档</title><meta name="description" content="{E(description)}">
<meta name="theme-color" content="#ffffff"><meta name="davebot-hosting" content="{'github-pages' if os.environ.get('GITHUB_ACTIONS')=='true' else 'preview'}"><link rel="canonical" href="https://docs.raivex.xyz{link(current)}">
<meta property="og:title" content="{E(title)} · DaveBot 文档"><meta property="og:description" content="{E(description)}">
<link rel="icon" href="/assets/mark.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/style.css?v={CSS_VERSION}">
<script src="/assets/app.js?v={JS_VERSION}" defer></script></head><body data-page="{E(current)}">
<a class="skip" href="#content">跳到正文</a>
<header class="topbar"><div class="topbar-inner"><a class="brand" href="/" aria-label="DaveBot 文档首页"><img src="/assets/mark.svg" width="30" height="30" alt=""><b>DaveBot</b><span class="brand-divider">/</span><span class="brand-sub">文档</span></a>
<nav class="top-links" aria-label="顶部导航"><a href="/guide/">开始使用</a><a href="/commands/">全部指令</a></nav>
<div class="header-tools"><button class="search-trigger" data-search aria-label="搜索文档">{icon('search')}<span>搜索文档</span><kbd>Ctrl K</kbd></button><button class="icon-button" id="theme" aria-label="切换深色模式" aria-pressed="false">{icon('theme')}</button><button class="icon-button menu-trigger" id="menu" aria-label="打开导航" aria-controls="sidebar" aria-expanded="false">{icon('menu')}</button></div></div></header>
<div class="layout"><aside class="sidebar" id="sidebar" aria-label="文档导航"><div class="sidebar-top"><span class="eyebrow">使用指南</span><a href="/commands/" class="index-link">指令速查 {icon('arrow')}</a></div>{sidebar(current)}<div class="sidebar-foot"><span class="status-dot"></span>当前可用 · 国服 CN</div></aside>
<button id="nav-backdrop" class="nav-backdrop" tabindex="-1" aria-label="关闭导航" hidden></button>
<main id="content" class="article" tabindex="-1"><div class="article-header"><p class="eyebrow">{E(eyebrow)}</p><h1>{E(title)}</h1><p class="lead">{E(description)}</p></div>{body}{pager}<footer class="article-footer"><span>DaveBot · 功能与指令指南</span><a href="https://github.com/RaiV3x/DaveBot-Docs" target="_blank" rel="noopener">GitHub ↗</a></footer></main>
<aside class="toc" aria-label="本页目录"><p>本页内容</p><nav>{''.join('<a href="#'+E(i)+'">'+E(t)+'</a>' for i,t in toc)}</nav><a class="back-to-top" href="#content">回到顶部 ↑</a></aside></div>
<dialog id="search-dialog" aria-labelledby="search-label"><div class="search-head">{icon('search')}<label class="sr-only" id="search-label" for="search-input">搜索文档和指令</label><input id="search-input" placeholder="搜索指令、别名或功能…" autocomplete="off" type="search" aria-controls="search-results"><button class="icon-button" id="search-close" aria-label="关闭搜索">{icon('close')}</button></div><p class="search-hint" id="search-hint" role="status">输入功能名，例如“名片”或“绑定”。</p><div id="search-results"></div><div class="search-footer"><span><kbd>↑</kbd> <kbd>↓</kbd> 选择 <kbd>Enter</kbd> 打开</span><span><kbd>Esc</kbd> 关闭</span></div></dialog>
<div id="toast" role="status" class="toast" hidden></div></body></html>'''

def main():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    search=[]
    def write(identity,title,desc,body,toc,eyebrow='使用文档'):
        path=OUT/identity/'index.html' if identity!='home' else OUT/'index.html'
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(shell(identity,title,desc,body,toc,eyebrow),encoding='utf-8')
        search.append({'title':title,'url':link(identity),'description':desc,'type':'文档','keywords':title+' '+desc})
    tiles=[('accounts','01','账号绑定','统一选择，所有功能共用。'),('mysekai','02','MySekai','查看资源卡片与地图。'),('personal-info','03','个人信息','静态名片与动态预览。')]
    body='<div class="hero-actions"><a class="button primary" href="/guide/">开始使用 '+icon('arrow')+'</a><a class="button secondary" href="/commands/">全部指令</a></div><div class="feature-grid">'+''.join('<a class="feature" href="'+link(p)+'"><span class="feature-number">'+n+'</span><h2>'+t+'</h2><p>'+d+'</p><span class="feature-arrow">'+icon('arrow')+'</span></a>' for p,n,t,d in tiles)+'</div>'
    body+=heading('first','从一条指令开始')+'<p>已完成绑定，直接查询；第一次使用，先阅读<a href="/guide/">快速开始</a>。</p><div class="home-commands"><a href="/accounts/#cmd-list"><code>/d账号列表</code><span>查看自己的绑定账号</span>'+icon('arrow')+'</a><a href="/mysekai/#cmd-resources"><code>/dmsa</code><span>查看 MySekai 资源</span>'+icon('arrow')+'</a><a href="/personal-info/#cmd-custom-profile"><code>/dcp 1</code><span>查看第 1 页名片</span>'+icon('arrow')+'</a></div>'
    body+='<div class="home-note"><span class="status-dot"></span><p>当前开放国服 CN。名片部分组件仍在移植，详见<a href="/personal-info/#coverage">支持范围</a>。</p></div>'
    write('home','DaveBot 使用指南','绑定一次账号，查询 MySekai 与个人名片。',body,[('first','从一条指令开始')],'DOCUMENTATION')
    write('commands','全部指令',f'{len(commands)} 项主要指令，按功能查阅；别名与参数见详情。',table_of_commands(),[(c,titles[c]) for c in ['accounts','mysekai','personal-info','tracking','admin']],'指令速查')
    for page in pages:
        identity=page['id'];body='';toc=[]
        for section in page['sections']:
            body+='<section>'+heading(section['id'],section['title'])+section['html']+'</section>'
            toc.append((section['id'],section['title']))
            search.append({'title':section['title'],'url':link(identity)+'#'+section['id'],'description':page['title'],'type':'章节','keywords':section['title']+' '+page['title']})
        for c in [c for c in commands if c['category']==identity]:
            body+=command_block(c);toc.append(('cmd-'+c['id'],c['title']))
            search.append({'title':c['title'],'url':link(identity)+'#cmd-'+c['id'],'description':c['usage'],'type':'指令','keywords':' '.join([c['title'],c['usage'],c['description'],*c['aliases']])})
        write(identity,page['title'],page['description'],body,toc,page['group'])
    (OUT/'search-index.json').write_text(json.dumps(search,ensure_ascii=False),encoding='utf-8')
    (OUT/'commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'CNAME').write_text('docs.raivex.xyz\n',encoding='utf-8')
    (OUT/'hosting.json').write_text(json.dumps({'platform':'github-pages' if os.environ.get('GITHUB_ACTIONS')=='true' else 'preview','revision':os.environ.get('GITHUB_SHA')}),encoding='utf-8')
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://docs.raivex.xyz/sitemap.xml\n',encoding='utf-8')
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://docs.raivex.xyz'+link(p)+'</loc></url>' for p in ['home',*order])+'</urlset>',encoding='utf-8')
    (OUT/'404.html').write_text(shell('home','找不到这页','可以搜索指令，或回到使用指南。','<a class="button primary" href="/">回到首页</a>',[]),encoding='utf-8')
    print(json.dumps({'pages':len(pages)+2,'commands':len(commands),'searchEntries':len(search),'output':str(OUT)}))

if __name__=='__main__':main()
