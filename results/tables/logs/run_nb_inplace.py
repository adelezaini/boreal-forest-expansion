"""Execute a notebook in a Jupyter kernel and save the outputs (text, tables, figures) into the .ipynb.

Usage: python run_nb_inplace.py path/to/nb.ipynb [--kernel lcc-env] [--timeout 3600]
Same idea as `jupyter nbconvert --execute --inplace`, which is not installed (no nbformat/nbclient).
Stops at the first error; the error is saved in that cell's output.
"""
import argparse, json, os, queue, time
from jupyter_client.manager import start_new_kernel

p = argparse.ArgumentParser()
p.add_argument('notebook')
p.add_argument('--kernel', default='lcc-env')
p.add_argument('--timeout', type=float, default=3600, help='seconds per cell')
args = p.parse_args()

path = os.path.abspath(args.notebook)
nb = json.load(open(path))
km, kc = start_new_kernel(kernel_name=args.kernel, cwd=os.path.dirname(path))
kc.execute_interactive('%matplotlib inline', timeout=60)

def save():
    json.dump(nb, open(path, 'w'), indent=1, ensure_ascii=False)

count, failed = 0, False
try:
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code':
            continue
        count += 1
        outputs, t0 = [], time.time()
        msg_id = kc.execute(''.join(cell['source']))
        while True:
            try:
                msg = kc.get_iopub_msg(timeout=args.timeout)
            except queue.Empty:
                raise TimeoutError(f'cell {i} exceeded {args.timeout} s')
            if msg['parent_header'].get('msg_id') != msg_id:
                continue
            kind, content = msg['msg_type'], msg['content']
            if kind == 'status' and content['execution_state'] == 'idle':
                break
            if kind == 'stream':
                if outputs and outputs[-1]['output_type'] == 'stream' and outputs[-1]['name'] == content['name']:
                    outputs[-1]['text'] += content['text']
                else:
                    outputs.append(dict(output_type='stream', name=content['name'], text=content['text']))
            elif kind in ('display_data', 'execute_result'):
                out = dict(output_type=kind, data=content['data'], metadata=content.get('metadata', {}))
                if kind == 'execute_result':
                    out['execution_count'] = count
                outputs.append(out)
            elif kind == 'error':
                outputs.append(dict(output_type='error', ename=content['ename'], evalue=content['evalue'],
                                    traceback=content['traceback']))
                failed = True
        cell['outputs'], cell['execution_count'] = outputs, count
        save()  # keep partial results if a later cell fails
        print(f'--- cell {i} {"FAILED" if failed else "ok"} ({time.time() - t0:.0f}s)', flush=True)
        if failed:
            break
finally:
    kc.stop_channels()
    km.shutdown_kernel(now=True)
raise SystemExit(1 if failed else 0)
