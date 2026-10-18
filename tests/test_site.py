"""Validate published command coverage, links, private-file isolation and search data."""
import importlib.util
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
import threading
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer

ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if 'id' in values:self.ids.append(values['id'])
        if tag=='a' and 'href' in values:self.links.append(values['href'])

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable,str(ROOT/'build.py')],check=True,capture_output=True)
        cls.commands=json.loads((ROOT/'content/commands.json').read_text(encoding='utf-8'))
    def test_every_implemented_command_and_alias_is_documented(self):
        source=ROOT.parent/'backend/src'
        names=set()
        # The standalone public docs repository has no private backend checkout.
        # In DaveBot's workspace, additionally check actual parser coverage.
        if source.is_dir():
            host=(source/'modules/accounts/commands.rs').read_text(encoding='utf-8')
            account_names=host.split('pub const NAMES:',1)[1].split('];',1)[0]
            names={'/d'+value for value in re.findall(r'"([^"\n]+)"',account_names)}
            bot=(source/'modules/mysekai/commands.rs').read_text(encoding='utf-8')
            recognized=bot.split('if !matches!(',1)[1].split(') {',1)[0]
            names|={'/d'+value for value in re.findall(r'"([^"\n]*)"',recognized)}
        documented=set()
        for command in self.commands:
            documented.add(command['usage'].split()[0]);documented.update(command['aliases'])
        self.assertFalse(names-documented, names-documented)
        self.assertTrue(all(name.startswith('/d') for name in documented))
        for alias in ['/dcp','/d自定义个人信息','/d自定义资料卡']:
            self.assertIn(alias,documented)
        # Region parsing support must not be advertised as an active region.
        profile=(ROOT/'dist/personal-info/index.html').read_text(encoding='utf-8')
        self.assertIn('除 cn 外的区服尚未接通',profile)
        self.assertIn('15 秒是检测上限，不是动画周期',profile)
    def test_links_fragments_and_search_results_resolve(self):
        out=ROOT/'dist';parsers={}
        for file in out.rglob('*.html'):
            parser=Links();parser.feed(file.read_text(encoding='utf-8'));parsers[file.resolve()]=parser
            self.assertEqual(len(parser.ids),len(set(parser.ids)),str(file))
        links=[link for parser in parsers.values() for link in parser.links if link.startswith('/')]
        search=json.loads((out/'search-index.json').read_text(encoding='utf-8'));links.extend(row['url'] for row in search)
        for url in links:
            path,_,fragment=url.partition('#');target=out/path.lstrip('/')/'index.html'
            self.assertTrue(target.is_file(),url)
            if fragment:self.assertIn(fragment,parsers[target.resolve()].ids,url)
        self.assertEqual(len(self.commands),21)
        self.assertTrue(any('/dcp' in row['description'] and row['type']=='指令' for row in search))
    def test_server_never_exposes_source_and_disallows_writes(self):
        spec=importlib.util.spec_from_file_location('docs_server',ROOT/'server.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        server=ThreadingHTTPServer(('127.0.0.1',0),module.handler(ROOT/'dist'))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        origin='http://127.0.0.1:'+str(server.server_port)
        try:
            with urllib.request.urlopen(origin+'/personal-info/') as response:
                self.assertIn("frame-ancestors 'none'",response.headers['Content-Security-Policy'])
                self.assertIn('名片',response.read().decode())
            for path in ['/../content/commands.json','/%2e%2e/server.py','/server.py','/api/admin/game-client']:
                with self.assertRaises(urllib.error.HTTPError) as caught:urllib.request.urlopen(origin+path)
                self.assertEqual(caught.exception.code,404)
            with self.assertRaises(urllib.error.HTTPError) as caught:urllib.request.urlopen(urllib.request.Request(origin+'/',data=b'x'))
            self.assertEqual(caught.exception.code,405)
        finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
