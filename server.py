#!/usr/bin/env python2.7

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


DATABASEURI = "postgresql://kc3051:2329@35.185.80.252/w4111"
engine = create_engine(DATABASEURI)



@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None



@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass



@app.route('/')
def index():
  print request.args
  return render_template("homepage.html")



@app.route('/movie_award')
def movie_award():
  a = []
  context = dict(data = a)
  return render_template("award_year.html", **context)


@app.route('/do_movie_award', methods=['POST'])
def do_movie_award():
  year = request.form['year']
  
  command = "select * from oscar_award where year = "+year
  cursor = g.conn.execute(command)
  a = []
  m = True
  a.append(year)
  for index in cursor : 
    if m : 
      a.append(index['mname'])
      m = False
    a.append(index['type'])
  cursor.close()
  context = dict(data = a)
  return render_template("award_year.html", **context)


@app.route('/company_revenue')
def company_revenue():
  a = []
  context = dict(data = a)
  return render_template("company_revenue.html", **context)



@app.route('/do_company_revenue', methods=['POST'])
def do_company_revenue():
  company = request.form['company']
  
  command = "select * from (select fname, sum(gross) from release natural join movie group by release.fname) t where t.fname = '"+str(company)+"';"
  cursor = g.conn.execute(command)
  a = []
  a.append(company)
  a.append('Revenues earned from Oscar movies : ')
  a.append(0)
  for index in cursor :
    a.append(str(index['sum'])+" US dollars")
  
  if a[len(a)-1] != 0:
    del a[len(a)-2]
  
  command = "select revenue from firm where fname = '"+str(company)+"'"
  cursor = g.conn.execute(command)
  a.append("And the total revenue of "+str(company)+" from 2003 to 2012 is ")
  for index in cursor : 
    a.append(str(index['revenue'])+" US dollars")
  context = dict(data = a)
  return render_template("company_revenue.html", **context)


@app.route('/become_audience')
def become_audience():
  
  command = "select * from audience"
  cursor = g.conn.execute(command)
  a = []
  for i in cursor:
    b =[]
    b.append(i['ssn'])
    if i['gender'] == 0:
      b.append('Male')
    elif i['gender'] == 1:
      b.append('Female')
    elif i['gender'] == 2:
      b.append('Refuse to answer')
    else :
      b.append('Unidentified')
    if i['pname'] == None:
      b.append(' ')
    else :
      b.append(i['pname'])
    a.append(b)
  context = dict(data = a)
  return render_template("become_audience.html", **context)


@app.route('/do_become_audience', methods = ['POST'])
def do_become_audience():
  a = []
  name = request.form['name']
  ssn = request.form['ssn']
  gender = request.form['gender']
  gender_index = 0
  country = request.form['country']
  if gender == 'Male' : 
    gender_index = 0
  elif gender == 'Female':
    gender_index = 1
  elif gender =='Refuse to ansert' : 
    gender_index = 2  
  elif gender =='Unidentified': 
    gneder_index = 3
  else :
    gender_index = 6
 
  try:
    command = "insert into audience (ssn,gender,pname) values ("+str(ssn)+","+str(gender_index)+","+"'"+str(name)+"'"+")"
    cursor = g.conn.execute(command)
    command = "insert into at (cname,ssn) values ('"+str(country)+"'"+","+ssn+")"
    cursor = g.conn.execute(command)
  except :
    command = "select * from audience"
    cursor = g.conn.execute(command)
    a = []
    for i in cursor:
      b =[]
      b.append(i['ssn'])
      if i['gender'] == 0:
        b.append('Male')
      elif i['gender'] == 1:
        b.append('Female')
      elif i['gender'] == 2:
        b.append('Refuse to answer')
      else :
        b.append('Unidentified')
      if i['pname'] == None:
        b.append(' ')
      else :
        b.append(i['pname'])
      a.append(b)
    context = dict(data = a)
    return render_template("become_audience.html", **context)   #Key exist return to origin page
  
  command = "select * from audience"
  cursor = g.conn.execute(command)
  a = []
  for i in cursor:
    b =[]
    b.append(i['ssn'])
    if i['gender'] == 0:
      b.append('male')
    elif i['gender'] == 1:
      b.append('Female')
    elif i['gender'] == 2:
      b.append('Refuse to answer')
    else : 
      b.append('Unidentified')
    if i['pname'] == None:
      b.append(' ')
    else :
      b.append(i['pname'])
    a.append(b)
  
    
  context = dict(data = a)
  return render_template("become_audience.html", **context)


@app.route('/watch_movie')
def watch_movie():
  a = []
  context = dict(data = a)
  return render_template("watch_movie.html", **context)

@app.route('/do_watch_movie', methods=['POST'])
def do_watch_movie():
  movie = request.form['movie']
  command = "select a1.pname, a1.ssn, c.cname from movie m, show s, country c, at a2, audience a1 where a1.ssn = a2.ssn and a2.cname = c.cname and c.cname = s.cname and s.mname = m.mname and m.mname ="+"'"+str(movie)+"'"
  cursor = g.conn.execute(command)
  a = []
  for i in cursor : 
    a.append(i)
  context = dict(data = a)
  return render_template("watch_movie.html", **context)



@app.route('/company_award')
def company_award():
  a = []
  context = dict(data = a)
  return render_template("company_award.html", **context)

@app.route('/do_company_award', methods=['POST'])
def do_company_award():
  company = request.form['company']

  command = 'select o.type, o.year from oscar_award o, release r where r.mname = o.mname and r.fname='+"'"+str(company)+"'"
  cursor = g.conn.execute(command)
  a = []
  for i in cursor :
    a.append(i)
  context = dict(data = a)
  return render_template("company_award.html", **context)


@app.route('/actor_country')
def actor_country():
  a = []
  context = dict(data = a)
  return render_template("actor_country.html", **context)

@app.route('/do_actor_country', methods=['POST'])
def do_actor_country():
  actor = request.form['actor']
  command = 'select c.cname, m.mname from actor a1, act a2, movie m, show s, country c where a1.ssn = a2.ssn and a2.mname = m.mname and m.mname = s.mname and s.cname = c.cname and a1.name = '+"'"+str(actor)+"'"
  cursor = g.conn.execute(command)
  a = []
  for i in cursor :
    a.append(i)
  context = dict(data = a)
  return render_template("actor_country.html", **context)



@app.route('/country_award')
def country_award():
  a = []
  context = dict(data = a)
  return render_template("country_award.html", **context)

@app.route('/do_country_award', methods=['POST'])
def do_country_award():
  country = request.form['country']
  command = 'select o.year, count(o.year) from oscar_award o, movie m, show s, country c where c.cname = s.cname and s.mname = m.mname and o.mname = m.mname and c.cname = '+"'"+str(country)+"'"+' group by year'
  cursor = g.conn.execute(command)
  a = []
  for i in cursor :
    a.append(i)
  context = dict(data = a)
  return render_template("country_award.html", **context)



@app.route('/company_actor')
def company_actor():
  a = []
  context = dict(data = a)
  return render_template("company_actor.html", **context)


@app.route('/do_company_actor', methods=['POST'])
def do_company_actor():
  company = request.form['company']
  command = 'select a1.name from firm f, release r, movie m, act a2, actor a1 where f.fname = r.fname and r.mname = m.mname and a2.mname = m.mname and a2.ssn = a1.ssn and f.fname = '+"'"+str(company) +"'"
  cursor = g.conn.execute(command)
  a = []
  a.append('Cash cowes for '+str(company)+' are : ')
  for i in cursor :
    a.append(i['name'])
  context = dict(data = a)
  return render_template("company_actor.html", **context)




@app.route('/actor_audience')
def actor_audience():
  a = []
  context = dict(data = a)
  return render_template("actor_audience.html", **context)

@app.route('/do_actor_audience', methods=['POST'])
def do_actor_audience():
  actor = request.form['actor']
  command = "Select a.ssn, a.pname from audience a, at a1, country c, show s, movie m, act a2, actor a3 where a3.ssn  = a2.ssn and a2.mname = m.mname and m.mname = s.mname and s.cname = c.cname and c.cname = a1.cname and a1.ssn = a.ssn and a3.name ='"+str(actor)+"' group by a.ssn, a.pname"
  cursor = g.conn.execute(command)
  a = []
  for i in cursor :
    b = []
    b.append(i['ssn'])
    b.append(i['pname'])
    a.append(b)
  context = dict(data = a)
  return render_template("actor_audience.html", **context)




@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=True, threaded=threaded)

  run()

