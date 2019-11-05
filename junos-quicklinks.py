from flask import Flask, render_template, redirect, url_for, request, make_response
import sqlite3
from ezdb import DatabaseDef, TableDef
import os
import sys

def GetQuickLinks(db):
  return [a for a in db.Select("quicklinks")]

def GetJunosFQDN(db):
  try:
    returnval = [a for a in db.Select("settings",["propname"],["fqdn"])][0]['propval']
  except:
    returnval = ""

  return returnval

def ExistsJunosFQDN(db):
  return [a["propval"] for a in db.Select("settings") if a["propname"] == "fqdn"]

def ExistQuickLink(db,linkurl):
  return [a["url"] for a in db.Select("quicklinks") if a["url"] == linkurl]

# Database Def
linktab = TableDef("quicklinks")
linktab.AddField("url","text")
settab = TableDef("settings")
settab.AddField("propname","text")
settab.AddField("propval","text")
linkdb = DatabaseDef("./quicklinks.db")
linkdb.AddTable(linktab)
linkdb.AddTable(settab)

if not linkdb.Initialize():
  print "Error Initializing Database"
  sys.exit()

app = Flask(__name__)

@app.route("/")
def GetRoot():
  if not ExistsJunosFQDN(linkdb):
    return render_template("fqdn.html")
  else:
    linklist = GetQuickLinks(linkdb)
    domainname = GetJunosFQDN(linkdb)

    return render_template("root.html", domainname = domainname, linklist = linklist)

@app.route("/moddomain/", methods = ["POST"])
def ModFqdn():
  domainname = str(request.form["fqdn"])

  if len(domainname) < 1:
    return redirect("/?error=invalid-fqdn")
  else:
    linkdb.Insert("settings",["fqdn",domainname])
    return redirect("/")

@app.route("/resetdomain/", methods = ["POST"])
def ResetDomain():
  fqdn = str(request.form["fqdn"])
  if len(fqdn) > 0:
    linkdb.Delete("settings",["propname"],["fqdn"])
    return redirect("/")
  else:
    return redirect("/?error=reset-fqdn-fail")
 
@app.route("/addlink/", methods = ["POST"])
def AddLink():
  linkurl = str(request.form["linkurl"])

  if len(linkurl) < 1:
    return redirect("/?error=invalid-url")
  else:
    if not ExistQuickLink(linkdb,linkurl):
      linkdb.Insert("quicklinks",[linkurl])
      return redirect("/")
    else:
      return redirect("/?error=link-exists")

@app.route("/dellink/", methods = ["POST"])
def DelLink():
  linkurl = str(request.form["linkurl"])

  if len(linkurl) > 0:
    if ExistQuickLink(linkdb,linkurl):
      linkdb.Delete("quicklinks",["url"],[linkurl])
      return redirect("/")
    else:
      return redirect("/?error=delete-link-fail")
  else:
    return redirect("/?error=invalid-url")

app.run("0.0.0.0",8080)
