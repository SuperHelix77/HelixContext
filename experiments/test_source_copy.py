import hashlib,json
import pytest
from source_copy import render

def cat(tmp_path,value):
 p=tmp_path/'catalog.json';p.write_text(json.dumps(value,ensure_ascii=False));return p,hashlib.sha256(p.read_bytes()).hexdigest()

def test_exact_unicode_and_types_text(tmp_path):
 s='req-1: 119 ms; false; not authorized; −0; 9007199254740993; null ≠ "null"'
 p,h=cat(tmp_path,{'r1':s});assert render('Answer: {{r1}}',p,h)=='Answer: '+s

def test_unknown_reference_fails(tmp_path):
 p,h=cat(tmp_path,{'r1':'x'})
 with pytest.raises(ValueError,match='unknown'):render('{{r2}}',p,h)

def test_changed_catalog_fails(tmp_path):
 p,h=cat(tmp_path,{'r1':'x'});p.write_text('{}')
 with pytest.raises(ValueError,match='hash'):render('{{r1}}',p,h)

def test_no_recursive_expansion(tmp_path):
 p,h=cat(tmp_path,{'r1':'{{r2}}','r2':'DO NOT EXECUTE'})
 assert render('{{r1}}',p,h)=='{{r2}}'

def test_duplicate_keys_fail(tmp_path):
 p=tmp_path/'cat';p.write_text('{"a":"x","a":"y"}');h=hashlib.sha256(p.read_bytes()).hexdigest()
 with pytest.raises(ValueError,match='duplicate'):render('{{a}}',p,h)

def test_invalid_value_fails(tmp_path):
 p,h=cat(tmp_path,{'a':None})
 with pytest.raises(ValueError,match='strings'):render('{{a}}',p,h)

def test_ordinary_text_unchanged(tmp_path):
 p,h=cat(tmp_path,{})
 s='def f(): return {"a": 2}\n1.25 × 0.8 = 1.';assert render(s,p,h)==s

def test_lists_and_ranges(tmp_path):
 p,h=cat(tmp_path,{'r1':'a','r2':'b','r3':'c'})
 assert render('{{r3,1}}',p,h)=='c\na'
 assert render('{{r1:3}}',p,h)=='a\nb\nc'

@pytest.mark.parametrize('marker',['{{r3:1}}','{{r1:999999999}}','{{r1:3,2}}','{{r1,9}}'])
def test_invalid_selectors(tmp_path,marker):
 p,h=cat(tmp_path,{'r1':'a','r2':'b','r3':'c'})
 with pytest.raises(ValueError):render(marker,p,h)
