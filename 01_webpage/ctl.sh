#!/bin/sh
# webui 服务启停（走 ctl.sh 壳服务，幂等；重启先按监听端口清场，避免 bind 冲突）
# 用法: sh webui/ctl.sh restart|start|stop|status
. /data/ctl.sh
# 解释器写死到 xuseek venv：技能/非壳环境调用时 PATH 可能没有 venv
XUSEEK_HOME=${XUSEEK_HOME:-/data/xuseek}
VENV=/data/xuseek/.venv
PATH="$VENV/bin:$PATH"; export PATH
CMD="$VENV/bin/python3 -u /data/workspace/webui/server.py"

holder() {   # 打印占用 8600 的 pid（无则空）
  python3 - <<'PY'
import re, subprocess
try:
    out = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=5).stdout
except Exception:
    out = ''
for line in out.splitlines():
    if ':8600' in line:
        m = re.search(r'pid=(\d+)', line)
        if m:
            print(m.group(1))
            break
PY
}

# freeport: 0=端口空闲，1=仍被占用（勿加 || 兜底，否则占用态被误判为空闲）
freeport() { python3 -c "import socket,sys;s=socket.socket();s.settimeout(0.5);sys.exit(1 if s.connect_ex(('127.0.0.1',8600))==0 else 0)" 2>/dev/null; }

case "$1" in
  stop)
    # 先杀壳看门狗（它退出时会清 pidfile；必须早于新实例写 pidfile，否则竞态删掉新 pid），
    # 再杀实际监听进程，等端口真正释放。
    p=$(cat "$XUSEEK_HOME/data/webui.pid" 2>/dev/null)
    rm -f "$XUSEEK_HOME/data/webui.pid"   # 先摘 pidfile：主动重启不该触发看门狗铃（免自醒）
    if [ -n "$p" ]; then kill "$p" 2>/dev/null; i=0; while [ $i -lt 20 ] && kill -0 "$p" 2>/dev/null; do sleep 0.25; i=$((i+1)); done; fi
    h=$(holder); [ -n "$h" ] && kill "$h" 2>/dev/null
    i=0; while [ $i -lt 40 ] && ! freeport; do sleep 0.5; i=$((i+1)); done
    ;;
  start)   start_wrapped webui "$CMD" ;;
  restart) sh "$0" stop; start_wrapped webui "$CMD" ;;
  status)  if freeport; then echo "webui: down"; else echo -n "webui: up (pid $(holder)) "; curl -s http://127.0.0.1:8600/healthz; echo; fi ;;
  *) echo "usage: $0 restart|start|stop|status"; exit 1 ;;
esac
