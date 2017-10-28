Docker
------

Steps required to run it locally in Docker:

```bash
cp .env-sample .env
# Replace QUANDL_KEY with actual value in .env
docker build --rm -t rostsber/yapo:latest .
docker run --env-file=.env -it -p 8888:8888 -v "$(pwd)":/opt/yapo/ --name jupyter-yapo rostsber/yapo:latest
```
