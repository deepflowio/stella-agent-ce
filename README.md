# stella-agent-ce
gpt agent

# 运行服务
进入deploy/templates 目录下，执行命令

```
kubectl create -f ./configmap.yaml
kubectl create -f ./deployment.yaml
kubectl create -f ./service.yaml
```

# 本地测试

python3 -m pip install virtualenv

/usr/local/bin/virtualenv --clear ./venv

./venv/bin/pip3 install -r ./requirements3.txt

./venv/bin/python3 ./app.py
