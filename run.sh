#运行前要安装pm2,守护node进程，安装命令：npm install -g pm2
#运行命令：pm2 start web/package.json --name "web"
#查看进程：pm2 ls
#停止进程：pm2 stop web
#重启进程：pm2 restart web
#删除进程：pm2 delete web

export PYTHONPATH=src
nohup uvicorn ana_flow.server.app:app --host 0.0.0.0 --port 8000 >>info.log &
cd web/.next/standalone
pm2 start server.js --name "ana_flow_web"

