#!/usr/bin/env python3
"""Launch the local Helix release console without changing Codex configuration."""
import argparse
import json
from pathlib import Path
import runpy
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', type=int, default=8769)
    p.add_argument('--config', type=Path, help='Existing live observer registration JSON')
    p.add_argument('--data-dir', type=Path, default=Path.home()/'.helix/hud')
    args = p.parse_args()
    if not 1 <= args.port <= 65535: p.error('Port must be1..65535')
    args.data_dir.mkdir(parents=True, exist_ok=True)
    config = args.config
    if config is None:
        config = args.data_dir/'config.json'
        if not config.exists():
            with config.open('x') as f: json.dump({'experiments': [], 'cohorts': [], 'audit_reports': []}, f)
    if not config.is_file(): p.error('Config file does not exist')
    root = Path(__file__).resolve().parent/'engine/hud'
    sys.path.insert(0, str(root))
    sys.argv = ['server.py', '--config', str(config.resolve()), '--journal', str((args.data_dir/'observations.jsonl').resolve()), '--port', str(args.port)]
    try: runpy.run_path(str(root/'server.py'), run_name='__main__')
    except KeyboardInterrupt: pass
    except OSError as exc:
        print(f'Cannot start Helix HUD: {exc}. Choose another --port if needed.', file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__': main()
