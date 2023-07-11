# liteapi
A native python server implementation with support for routes.
## Usage
Liteapi is intended to be used as a submodule in other python projects.  
References: https://git-scm.com/book/en/v2/Git-Tools-Submodules
## Getting started
- Create your new project and cd into it
- `git init`
- `git commit -am "initial commit"`
- `git submodule add https://github.com/shifqu/liteapi.git`
- Modify pyproject.toml to include liteapi package:
```toml
packages = [
    { "include"= "exampleapi" },
    { "include"= "liteapi" }
]
```
- Add the following to your main python file:
```python
# main.py
import liteapi

app = liteapi.Application()

@app.route("/query")
def query(request: liteapi.Request) -> liteapi.JSONResponse:
    if "q" not in request.query_params:
        body = dict(ok=False, message="`q` is a required query parameter.")
        raise liteapi.ApiException(body=body, status_code=400)
    
    body = dict(ok=True, message="success", data=request.query_params["q"])
    return liteapi.JSONResponse(body=body)

if __name__ == "__main__":
    app.serve("localhost", 7878)
```
- Run the application: `python path/to/main.py`
- Visit http://localhost:7878/query?q=hello
- Behold the response