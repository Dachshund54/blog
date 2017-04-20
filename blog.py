import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog_Post(db.Model):
    subject = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        blogs = db.GqlQuery( "SELECT * FROM Blog_Post "
                            "ORDER BY created DESC ")
        self.render("front.html", blogs = blogs)

class NewPostHandler(Handler):
    def render_newpost(self, subject="", blog="", error=""):
        self.render("newpost.html", subject = subject, blog = blog, error = error)

    def get(self):
        self.render_newpost()

    def post(self):
        subject = self.request.get('subject')
        blog = self.request.get('blog')

        if subject and blog:
            a = Blog_Post(subject = subject, blog = blog)
            a_key = a.put()
            self.redirect("/%d" % a_key.id())

        else:
            error = "subject and content, please!"
            self.render_newpost(subject, blog, error)

class PermaLink(Handler):
    def get(self, post_id):
        c = db.GqlQuery( "SELECT * FROM Blog_Post ")
        blogs = c.get()
        result = blogs.get_by_id(int(post_id))
        subject = result.subject
        blog = result.blog
        created = result.created
        self.render("permalink.html", subject = subject, blog = blog, created = created)

app = webapp2.WSGIApplication([ ('/', MainPage),
                                ('/newpost', NewPostHandler),
                                ('/(\d+)', PermaLink)
                                ], debug=True)
