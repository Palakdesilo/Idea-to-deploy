import asyncio
import subprocess
import sys
import os
import signal
from pathlib import Path
from typing import Dict, Optional, Tuple
import aiofiles

class ProjectRunner:
    def __init__(self, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir
        self.processes: Dict[str, subprocess.Popen] = {}
        self.ports: Dict[str, int] = {}

    async def install_dependencies(self, project_id: str, type: str = "backend") -> Tuple[bool, str]:
        """Install dependencies for the specified project component"""
        # Map internal types to generated folder names
        comp_folder = "apps/api" if type == "backend" else "apps/web"
        project_path = (self.artifacts_dir / project_id / "code" / comp_folder).resolve()
        log_dir = (self.artifacts_dir / project_id).resolve()
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"{type}_install.log"
        
        if not project_path.exists():
            # Try to report this to log file so UI sees it
            msg = f"Project path does not exist: {project_path}\nDid you 'Generate Code' successfully?"
            try:
                with open(log_file, "w") as f:
                    f.write(msg)
            except: 
                pass
            return False, msg

        # sanity check for config files
        if type == "backend":
             if not (project_path / "requirements.txt").exists():
                  msg = "requirements.txt not found. Code generation might be incomplete."
                  with open(log_file, "w") as f: f.write(msg)
                  return False, msg
        if type == "frontend":
             if not (project_path / "package.json").exists():
                  msg = "package.json not found. Code generation might be incomplete."
                  with open(log_file, "w") as f: f.write(msg)
                  return False, msg

        cmd = []
        if type == "backend":
            # Use the current python interpreter to avoid venv issues for now, or assume pip is in path
            cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        elif type == "frontend":
            if os.name == 'nt':
                cmd = ["npm.cmd", "install"]
            else:
                cmd = ["npm", "install"]

        try:
            # Run install command synchronously in a separate thread to avoid blocking event loop
            # and avoid asyncio subprocess issues on Windows SelectorEventLoop
            def run_install():
                return subprocess.run(
                    cmd,
                    cwd=str(project_path),
                    capture_output=True,
                    text=True,
                    shell=(True if type == "frontend" and os.name == 'nt' else False) # Use shell for npm on windows to be safe
                )
            
            # Using partial to pass args if needed, or just closure
            result = await asyncio.to_thread(run_install)
            
            output = result.stdout + "\n" + result.stderr
            
            # Use standard open for safety
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(output)
                
            if result.returncode != 0:
                return False, f"Installation failed. Check logs."
                
            return True, "Dependencies installed successfully"
            
        except Exception as e:
            import traceback
            err_details = traceback.format_exc()
            with open(log_file, 'w') as f:
                f.write(f"Exception during install:\n{err_details}")
            return False, f"Install Error: {repr(e)}"

    async def start_server(self, project_id: str, type: str, port: int, env: Optional[Dict[str, str]] = None) -> Tuple[bool, str]:
        """Start a dev server for the component"""
        # Stop existing if any
        await self.stop_server(project_id, type)
        
        # Map internal types to generated folder names
        comp_folder = "apps/api" if type == "backend" else "apps/web"
        project_path = self.artifacts_dir / project_id / "code" / comp_folder
        log_file = self.artifacts_dir / project_id / f"{type}_run.log"
        
        cmd = []
        if type == "backend":
            # Use hypercorn instead of uvicorn for Python 3.13 compatibility
            # hypercorn is a stable ASGI server that works with FastAPI
            cmd = [sys.executable, "-m", "hypercorn", "main:app", "--bind", f"0.0.0.0:{port}", "--reload"]
        elif type == "frontend":
            # Run next dev
            # On Windows, we must use npm.cmd explicitly if shell=False, or just use shell=True carefully
            if os.name == 'nt':
                cmd = ["npm.cmd", "run", "dev", "--", "-p", str(port)]
            else:
                cmd = ["npm", "run", "dev", "--", "-p", str(port)]

        try:
            # Open logs in append mode to capture history
            out_f = open(log_file, "a")
            # Write start marker
            out_f.write(f"\n--- STARTING SERVER ON PORT {port} ---\n")
            if env:
                out_f.write(f"Environment variables injected: {list(env.keys())}\n")
            out_f.flush()

            if os.name == 'nt':
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                creationflags = 0

            # Merge current environment with custom environment
            full_env = os.environ.copy()
            if env:
                full_env.update(env)

            # Start process without shell=True for better control, using npm.cmd above helps
            process = subprocess.Popen(
                cmd,
                cwd=str(project_path),
                stdout=out_f,
                stderr=subprocess.STDOUT, # Merge stderr into stdout
                creationflags=creationflags,
                shell=False, # Better for PID tracking
                env=full_env
            )
            
            self.processes[f"{project_id}_{type}"] = process
            self.ports[f"{project_id}_{type}"] = port
            
            return True, f"Server started on port {port}"

        except Exception as e:
            return False, str(e)

    async def stop_server(self, project_id: str, type: str):
        """Stop a running server"""
        key = f"{project_id}_{type}"
        process = self.processes.get(key)
        
        if process:
            # On Windows, we need to kill the process tree for shell=True commands (npm)
            if os.name == 'nt':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
            else:
                process.terminate()
            
            process.poll()
            del self.processes[key]
            
    async def get_logs(self, project_id: str, type: str, lines: int = 50) -> str:
        """Read the last N lines of the log file"""
        log_file = self.artifacts_dir / project_id / f"{type}_run.log"
        if not log_file.exists():
            # Try install log if run log missing
            log_file = self.artifacts_dir / project_id / f"{type}_install.log"
            
        if not log_file.exists():
            return "No logs found."
            
        if not log_file.exists():
            return "No logs found."
            
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                return "\n".join(content.splitlines()[-lines:])
        except Exception as e:
            return f"Error reading logs: {e}"

    async def check_health(self, project_id: str, type: str) -> str:
        """Check if process is still running"""
        key = f"{project_id}_{type}"
        process = self.processes.get(key)
        if process and process.poll() is None:
            return "running"
        return "stopped"
