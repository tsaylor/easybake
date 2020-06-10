import copy
import http.server
import json
import os
import shutil
import socketserver
import sys
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader


class SiteBuilder:
    def __init__(
        self,
        sitefile_path,
        template_dir="templates",
        content_dir="content",
        asset_dir="assets",
        base_dir=os.getcwd(),
    ):
        self.BASE_DIR = base_dir
        self.sitefile_path = sitefile_path
        self.template_dir = template_dir
        self.content_dir = content_dir
        self.asset_dir = asset_dir
        self.env = Environment(loader=FileSystemLoader(self.BASE_DIR))

    def load_datafile(self, datafile):
        return self.load_json_or_yaml(os.path.join(self.content_dir, datafile))

    def load_json_or_yaml(self, path):
        with open(path) as f:
            if path.endswith("json"):
                data = json.load(f)
            elif path.endswith("yaml"):
                # I can't catch exceptions well in yaml so this at least lets yaml report it better
                txt = f.read()
                data = yaml.safe_load(txt)
            else:
                data = {}
        data = self.process_data(data)
        return data

    def process_data(self, data):
        if isinstance(data, list):
            data = [self.process_data(i) for i in data]
        elif isinstance(data, dict):
            if set(data.keys()) == set(("_language", "content")):
                if data["_language"] == "markdown":
                    data = markdown.markdown(data["content"])
            else:
                data = {key: self.process_data(value) for key, value in data.items()}
        return data

    def load_sitefile(self, sitefile):
        try:
            data = self.load_json_or_yaml(self.sitefile_path)
        except (TypeError, FileNotFoundError):
            print(
                "Can't load sitefile '{}'".format(self.sitefile_path), file=sys.stdout
            )
            sys.exit(1)
        except json.decoder.JSONDecodeError:
            print(
                "Provided sitefile '{}' is not valid JSON".format(self.sitefile_path),
                file=sys.stdout,
            )
            sys.exit(1)
        if data == {}:
            print("Site file is empty!", file=sys.stdout)
            sys.exit(1)
        return data

    def load_template(self, template):
        return self.env.get_template(os.path.join(self.template_dir, template))

    def render(self, obj):
        template = self.load_template(obj["template"])
        data = copy.deepcopy(self.context)
        if "datafile" in obj:
            data.update(self.load_datafile(obj["datafile"]))
        if "data" in obj:
            data.update(obj["data"])
        content = template.render(**data)
        for a in obj.get("assets", []):
            shutil.copy(
                os.path.join(self.asset_dir, a), os.path.join("build", "assets", a)
            )
        return content

    def write_page(self, content):
        url = content["url"]
        if url.endswith("/"):
            url += "index.html"
        if url.startswith("/"):
            url = url[1:]
        urlparts = url.split("/")
        dirpath = os.path.join("build", *urlparts[:-1])
        filename = urlparts[-1]
        os.makedirs(dirpath, exist_ok=True)
        with open(os.path.join(dirpath, filename), "w") as f:
            f.write(content["rendered"])

    def build(self):
        clean()
        os.makedirs(os.path.join("build", "assets"))
        site = self.load_sitefile(self.sitefile_path)
        self.context = {}
        for content in site["content"]:
            content["rendered"] = self.render(content)
            if "name" in content:
                cname = content["name"]
                if cname in self.context:
                    if isinstance(self.context[cname], list):
                        self.context[cname].append(content["rendered"])
                    else:
                        self.context[cname] = [self.context[cname], content["rendered"]]
                else:
                    self.context[cname] = content["rendered"]
            if "url" in content:
                self.write_page(content)


def clean():
    if os.path.exists("build"):
        shutil.rmtree("build")


def get_handler(directory):
    def handler(*args, **kwargs):
        kwargs["directory"] = directory
        return http.server.SimpleHTTPRequestHandler(*args, **kwargs)

    return handler


def serve():
    try:
        PORT = 8000
        Handler = get_handler("build")
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("serving at http://0.0.0.0:{}/".format(PORT))
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping...")
