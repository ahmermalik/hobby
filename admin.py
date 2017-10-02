import os         ##this is wused when you're deploying server. it is ok to add it in the beginning of your project.
import boto3

import tornado.ioloop
import tornado.web
import tornado.log

from dotenv import load_dotenv



from jinja2 import \
  Environment, PackageLoader, select_autoescape                     #This is setting up jinja to know where the python module is located.




load_dotenv('.env')

PORT = int(os.environ.get('PORT','1337'))


                                                                    #AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")



SES_CLIENT = boto3.client(
  'ses',
  aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
  aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
  region_name="us-east-1"
)









ENV = Environment(                                                  #the module and which directory within the module has your templates
  loader=PackageLoader('myapp', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)




class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))


class MainHandler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("admin.html", {})




class RickHandler(TemplateHandler):
  def get(self, page):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template(page + '.html', {})

class MainHandlerOld(tornado.web.RequestHandler):              ##
  def get(self):
    self.set_header("Content-Type", 'text/plain')
    self.write("Hello World.")


class YouTooHandler(tornado.web.RequestHandler):            #this is a handler
  def get(self):
    self.set_header("Content-Type", 'text/plain')
    name = self.get_query_argument('name', 'Nobody')
    self.write("Hello World{}".format(name))

class SubmissionHandler(tornado.web.RequestHandler):            #this is a handler
  def post(self):
    name = self.get_body_argument('name', 'Nobody')
    email = self.get_body_argument('email')

    self.write("Hello World " + name)

    img = self.request.files['image'][0]
    with open("temp.jpg", 'wb') as fh:
        fh.write(img['body'])


    response = SES_CLIENT.send_email(
      Destination={
        'ToAddresses': ['ahmerm92@gmail.com'],
      },
      Message={
        'Body': {
          'Text': {
            'Charset': 'UTF-8',
            'Data': 'Name: {}\nE-mail: {}\n'.format(name, email),               # learn how to attach the file submitted and e-mail it to yourself
          },                                                                    #"SES Amazon Python BOTO" Keywords
        },
        'Subject': {'Charset': 'UTF-8', 'Data': 'Password Sniffer'},
      },
      Source='ahmerm92@gmail.com',
    )








def make_app():                                 ##make_app will return the application and all the routing logic within it.
  return tornado.web.Application([              ##the r/hello2 will call the YouTooHandler hanlder
    (r"/", MainHandler),
    (r"/hello2", YouTooHandler),
    (r"/form-submission", SubmissionHandler),
    (r"/page/(.*)", RickHandler),
    (
     r"/static/(.*)",                           ##this helps the server find the static folder which goes with all the main files.
     tornado.web.StaticFileHandler,
     {'path': 'static'}
    ),
  ], autoreload=True)


if __name__ == "__main__":
  tornado.log.enable_pretty_logging()

  app = make_app()
  app.listen(PORT, print('Server started on localhost: ' + str(PORT)))
  tornado.ioloop.IOLoop.current().start()




