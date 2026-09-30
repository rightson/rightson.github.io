"""Author reference experiment: configuration integrity, no EDA or PDK inputs.
Run: python3 scripts/experiments/ic_config_release_demo.py
"""
import hashlib
import json
import sqlite3

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

db=sqlite3.connect(':memory:')
db.executescript('''
CREATE TABLE head (project TEXT PRIMARY KEY, config TEXT);
CREATE TABLE requests (request_key TEXT PRIMARY KEY, config TEXT);
INSERT INTO head VALUES ('toy-soc', 'cfg42');
''')
cfg={'rtl':'r12','sdc':'s8','recipe':'flow-r6'}
cfg_hash=digest(cfg)

def validate(evidence):
    if evidence['configuration_digest']!=cfg_hash:
        return 'STALE_INPUT'
    if set(evidence['reports'])!={'synthesis_check','lec'}:
        return 'INCOMPLETE'
    if not all(evidence['reports'].values()):
        return 'FAILED_GATE'
    return 'VALID'

def publish(request,config,parent):
    # One database transaction binds request identity and the expected head.
    db.execute('BEGIN IMMEDIATE')
    prior=db.execute('SELECT config FROM requests WHERE request_key=?',(request,)).fetchone()
    if prior:
        db.rollback()
        return 'REPLAY' if prior[0]==config else 'REQUEST_CONFLICT'
    n=db.execute('UPDATE head SET config=? WHERE project=? AND config=?',
                 (config,'toy-soc',parent)).rowcount
    if n!=1:
        db.rollback()
        return 'HEAD_CONFLICT'
    db.execute('INSERT INTO requests VALUES (?,?)',(request,config))
    db.commit()
    return 'PUBLISHED'

def check(label,actual,expected):
    assert actual==expected,(label,actual,expected)
    print(f'{label}: {actual}')

check('mixed configuration',validate({'configuration_digest':digest({'rtl':'r12','sdc':'s7','recipe':'flow-r6'}),'reports':{'synthesis_check':True,'lec':True}}),'STALE_INPUT')
check('interrupted artifact set',validate({'configuration_digest':cfg_hash,'reports':{'synthesis_check':True}}),'INCOMPLETE')
check('complete matching evidence',validate({'configuration_digest':cfg_hash,'reports':{'synthesis_check':True,'lec':True}}),'VALID')
check('first integrator',publish('request-A','cfg43','cfg42'),'PUBLISHED')
check('timeout retry',publish('request-A','cfg43','cfg42'),'REPLAY')
check('competing stale integrator',publish('request-B','cfg44','cfg42'),'HEAD_CONFLICT')
check('request identity misuse',publish('request-A','cfg44','cfg43'),'REQUEST_CONFLICT')
assert db.execute('SELECT config FROM head').fetchone()[0]=='cfg43'
print('7 checks passed; head=cfg43; synthetic metadata only.')
