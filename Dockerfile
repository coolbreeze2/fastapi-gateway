FROM python:3.9.16-bullseye

ADD . /opt/fastapi_gateway
WORKDIR /opt/fastapi_gateway

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
&& pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn \
&& pip install -r requirements.txt

CMD ["sh", "entrypoint.sh"]