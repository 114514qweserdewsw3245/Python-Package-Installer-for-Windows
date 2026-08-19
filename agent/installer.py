"""Windows-only localhost Agent for Python-Package-Installer-for-Windows V0.7.5."""
from __future__ import annotations
import json, os, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from .environment import ALLOWED_COMMANDS, detect_python
from .pip_manager import pip_available, validate_mirror, validate_requirement, install
from .mirror_manager import benchmark_mirrors
from .task_manager import TASKS
from .venv_manager import UnsafePathError, create_venv, safe_workspace, validate_venv
HOST='127.0.0.1'; PORT=int(os.environ.get('PYTHON_PACKAGE_INSTALLER_PORT',os.environ.get('CLICK_INSTALL_PORT','8765')))
ROOT=Path(__file__).resolve().parent.parent; FRONTEND_ROOT=ROOT/'frontend'; WORKSPACE_ROOT=ROOT/'workspace'
STATIC_TYPES={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8'}

def run_task(task_id, request):
    try:
        workspace=safe_workspace(request.get('workspace','default'),WORKSPACE_ROOT); workspace.mkdir(parents=True,exist_ok=True)
        mode=request['environment_mode']; env=detect_python(request.get('python_command'))
        if not env.available or not env.executable: raise RuntimeError(env.error or 'Python is unavailable.')
        TASKS.update(task_id,status='preparing')
        TASKS.emit(task_id,'info','Preparing the selected Python environment.')
        if mode=='new_venv':
            TASKS.emit(task_id,'info','Creating or reusing the workspace virtual environment.')
            python=str(create_venv(env.executable,workspace))
        elif mode=='current_python':
            TASKS.emit(task_id,'info','Using the current Python environment.')
            python=env.executable
        else:
            TASKS.emit(task_id,'info','Using the existing workspace virtual environment.')
            python=str(validate_venv(workspace/'.venv'))
        if not pip_available(python): raise RuntimeError('pip is unavailable in the selected Python environment.')
        TASKS.update(task_id,status='installing',python_executable=python)
        TASKS.emit(task_id,'info',f'Using Python: {python}')
        for i, requirement in enumerate(request['packages']):
            TASKS.update(task_id,current_package=requirement)
            TASKS.package(task_id,i,status='installing')
            TASKS.emit(task_id,'info',f'Installing {requirement}.',requirement)
            code, stderr=install(
                python, requirement, request['mirror'], workspace,
                on_output=lambda level, line: TASKS.emit(task_id,level,line,requirement),
            )
            status='success' if code==0 else 'failed'
            TASKS.package(task_id,i,status=status,return_code=code,stderr='' if code==0 else stderr)
            TASKS.emit(task_id,'success' if code==0 else 'error',f'{requirement}: {status} (exit code {code}).',requirement)
        task=TASKS.get(task_id)
        final_status='completed_with_errors' if task['failed_count'] else 'completed'
        TASKS.update(task_id,status=final_status,current_package=None)
        TASKS.emit(task_id,'info',f'Installation finished: {task["success_count"]} succeeded, {task["failed_count"]} failed.')
    except Exception as exc:
        task=TASKS.get(task_id)
        if task:
            for i,item in enumerate(task['packages']):
                if item['status'] in ('waiting','installing'): TASKS.package(task_id,i,status='failed',return_code=None,stderr=str(exc)[:4000])
        TASKS.update(task_id,status='failed',error=str(exc)[:4000],current_package=None)
        TASKS.emit(task_id,'error',f'Installation task failed: {exc}')

class AgentHandler(BaseHTTPRequestHandler):
    server_version='Python-Package-Installer-for-Windows/0.7.5'
    def log_message(self, fmt,*args): print('[agent] '+fmt%args)
    def send_json(self,status,payload):
        body=json.dumps(payload,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.send_header('Access-Control-Allow-Origin','*'); self.end_headers(); self.wfile.write(body)
    def do_OPTIONS(self):
        self.send_response(204); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.end_headers()
    def read_body(self):
        size=int(self.headers.get('Content-Length','0'))
        if size<=0 or size>200000: raise ValueError('Invalid request body size.')
        return json.loads(self.rfile.read(size).decode('utf-8'))
    def serve_file(self,path):
        relative='index.html' if path in ('','/') else unquote(path.lstrip('/')); file=(FRONTEND_ROOT/relative).resolve()
        if FRONTEND_ROOT not in file.parents or not file.is_file() or file.suffix not in STATIC_TYPES: return self.send_json(404,{'ok':False,'error':'Not found'})
        body=file.read_bytes(); self.send_response(200); self.send_header('Content-Type',STATIC_TYPES[file.suffix]); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
    def stream_events(self, task_id, after_id):
        if TASKS.get(task_id) is None:
            return self.send_json(404,{'ok':False,'error':'Task not found.'})
        self.send_response(200)
        self.send_header('Content-Type','text/event-stream; charset=utf-8')
        self.send_header('Cache-Control','no-cache, no-store')
        self.send_header('Connection','keep-alive')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        last_id=after_id
        try:
            while True:
                events=TASKS.events_after(task_id,last_id,timeout=12)
                if events is None:
                    break
                if not events:
                    self.wfile.write(b': keepalive\n\n')
                    self.wfile.flush()
                    continue
                for event in events:
                    payload=json.dumps(event,ensure_ascii=False).encode('utf-8')
                    self.wfile.write(b'id: '+str(event['id']).encode()+b'\n')
                    self.wfile.write(b'event: log\n')
                    self.wfile.write(b'data: '+payload+b'\n\n')
                    last_id=event['id']
                task=TASKS.get(task_id)
                snapshot=json.dumps(task,ensure_ascii=False).encode('utf-8')
                self.wfile.write(b'event: task\n')
                self.wfile.write(b'data: '+snapshot+b'\n\n')
                self.wfile.flush()
                if task and task['status'] in ('completed','completed_with_errors','failed'):
                    break
        except (BrokenPipeError,ConnectionResetError):
            pass

    def do_GET(self):
        parsed=urlparse(self.path)
        if parsed.path=='/api/health': return self.send_json(200,{'ok':True,'agent':'Python-Package-Installer-for-Windows','version':'0.7.5','windows_only':True})
        if parsed.path=='/api/environment':
            requested=parse_qs(parsed.query).get('python',[None])[0]
            if requested not in (None,)+ALLOWED_COMMANDS: return self.send_json(400,{'ok':False,'error':'Unsupported Python command.'})
            env=detect_python(requested); return self.send_json(200,{'ok':env.available and env.pip_available,'environment':env.to_dict()})
        if parsed.path=='/api/tasks': return self.send_json(200,{'ok':True,'tasks':TASKS.all()})
        if parsed.path=='/api/mirrors/benchmark':
            return self.send_json(200, {'ok': True, **benchmark_mirrors()})
        if parsed.path.startswith('/api/tasks/') and parsed.path.endswith('/events'):
            task_id=parsed.path.split('/')[3]
            raw_after=parse_qs(parsed.query).get('after',['0'])[0]
            try: after_id=max(0,int(raw_after))
            except ValueError: return self.send_json(400,{'ok':False,'error':'Invalid event cursor.'})
            return self.stream_events(task_id,after_id)
        if parsed.path.startswith('/api/tasks/'):
            task=TASKS.get(parsed.path.rsplit('/',1)[1]); return self.send_json(200 if task else 404,{'ok':bool(task),'task':task} if task else {'ok':False,'error':'Task not found.'})
        if parsed.path=='/api/catalog':
            catalog=json.loads((FRONTEND_ROOT/'packages.json').read_text(encoding='utf-8')); return self.send_json(200,{'ok':True,'categories':len(catalog),'packages':sum(len(x) for x in catalog.values())})
        self.serve_file(parsed.path)
    def do_POST(self):
        if urlparse(self.path).path != '/api/install': return self.send_json(404,{'ok':False,'error':'Not found'})
        try:
            payload=self.read_body(); packages=payload.get('packages'); mode=payload.get('environment_mode'); mirror=payload.get('mirror',''); workspace=payload.get('workspace','default'); command=payload.get('python_command')
            if not isinstance(packages,list) or not packages or len(packages)>100 or len(set(packages))!=len(packages): raise ValueError('Choose 1–100 unique packages.')
            if not all(validate_requirement(x) for x in packages): raise ValueError('One or more package requirements are invalid.')
            if mode not in ('new_venv','current_python','existing_venv'): raise ValueError('Invalid environment mode.')
            if not validate_mirror(mirror): raise ValueError('Unsupported package index.')
            if command not in (None,)+ALLOWED_COMMANDS: raise ValueError('Unsupported Python command.')
            safe_workspace(workspace,WORKSPACE_ROOT)
            task=TASKS.create(packages,mode,workspace); payload={'packages':packages,'environment_mode':mode,'mirror':mirror,'workspace':workspace,'python_command':command}
            threading.Thread(target=run_task,args=(task['id'],payload),daemon=True).start(); self.send_json(202,{'ok':True,'task_id':task['id'],'status':'queued'})
        except (ValueError,UnsafePathError,json.JSONDecodeError) as exc: self.send_json(400,{'ok':False,'error':str(exc)})

def main():
    if os.name!='nt': raise SystemExit('This agent is Windows-only.')
    WORKSPACE_ROOT.mkdir(exist_ok=True); server=ThreadingHTTPServer((HOST,PORT),AgentHandler); print(f'Python-Package-Installer-for-Windows Agent V0.7.5 listening on http://{HOST}:{PORT}')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
