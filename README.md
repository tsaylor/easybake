# Easybake

Easybake is a tool for making static websites that lets you focus on your content and not on software. It generates your website based on simple yaml configuration files and jinja templates.

## The Site File

The basic component of a website is a site file, which is a json or yaml file specifying the pages of your site. This example yaml file defines a single content object that generates a single page at the root of the website:

```
content:
- url: /
  template: home.html
  assets:
  - picture-of-me.jpg
```

The `template` key references a template file called `home.html`. This is a jinja template that might look like this:

```
<html>
    <head>
        <title>My Website</title>
    </head>
    <body>
        <h1>Hello World!</h1>
        <img src="/assets/picture-of-me.jpg" />
    </body>
</html>
```

When you generate this site, you'll end up with the following files in your `build` directory:

```
/build/
    index.html
    /assets/
        picture-of-me.jpg
```

This can be published to any web host (Amazon S3, Github Pages, Azure Storage, or Google Cloud Storage all offer popular ways to do this).

## Generating your site

Generating the site from the example above is simple. Using the example above, you might have the following files:

```
site.yaml
/templates/
    home.html
/assets/
    picture-of-me.jpg
```

From this directory, run `python -m easybake build --site=site.yaml` and your site will be generated in a new subdirectory called `build`:

```
site.yaml
/templates/
    home.html
/assets/
    picture-of-me.jpg
/build/
    index.html
    /assets/
        picture-of-me.jpg
```

To see your site, you can run `python -m easybake serve` and your site will be viewable at http://127.0.0.1:8000.

## More complex content

Content objects can do more than just specify a template and related assets. Variables can be defined and used in your templates, and the rendered page itself can be stored in a variable instead of in a file. Here's a full list of usable keys in a content object:

- `template` - Render the data in this content object into this template
- `assets` - A list of extra files to make available to the website
- `url` - If given, the content will be saved in a file available at this url
- `name` - If given, the context variable name where this rendered content will be available. If a name is repeated, both values will be kept in a list.
- `data` - An object of data to add to the template's rendering context
- `datafile` - A file of data to add to the template's rendering context

Content objects are rendered in order, so content stored in a variable will be available to use in subsequently rendered content.

Any keys defined in a datafile that aren't used in a template are ignored, so a single datafile can be used in multiple content objects to render one piece of content in multiple ways (for example, to render a article preview with a short summary that links to the full article).

In a datafile, variables can be defined in markdown for richer content.

```
title: My Article
summary: >
  This is a summary of the content in my article.
  I've split it across multiple lines for readability.
body:
  _language: markdown
  content: |
    ## An H2 in markdown

    This is the full content of my article, fully written
    in markdown. It will be in the 'body' variable as html.

    - a list
    - of items
    - in markdown
```

Here's an example of a site using more of these features:

**site.yaml**
```
content:
- url: /contact/
  template: page.html
  data:
    title: Contact Me
    body:
      _language:
      content: |
        Drop me a line at [me@exmaple.com](mailto://me@exmaple.com)!
- name: articles
  template: card.html
  datafile: my-first-article.yaml
- url: /my-first-article/
  template: page.html
  datafile: my-first-article.yaml
- name: articles
  template: card.html
  datafile: my-second-article.yaml
- url: /my-second-article/
  template: page.html
  datafile: my-second-article.yaml
- url: /
  template: home.html
  assets:
  - picture-of-me.jpg
```

**home.html**
```
<html>
    <head>
        <title>My Website</title>
    </head>
    <body>
        <h1>This is my website</h1>
        <img src="/assets/picture-of-me.jpg" />
        <p>Articles:</p>
        {% for article in articles %}
            {{article}}  <!-- injects a rendered card.html for this article -->
        {% endfor %}
    </body>
</html>
```

**card.html**
```
<div class="card">
    <h2>{{title}}</h2>
    <p>{{summary}}</p>
</div>
```

**page.html**
```
<html>
    <head>
        <title>My Website</title>
    </head>
    <body>
        <h1>{{title}}</h1>
        {{body}}  <!-- no containing tag since this variable is markdown rendered to html -->
    </body>
</html>
```
