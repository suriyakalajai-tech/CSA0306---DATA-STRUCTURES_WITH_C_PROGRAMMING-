import json, math, csv, io
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import check_password_hash
from database import connect, init_db
from config import Config
from algorithms.graph import dijkstra, alternative_path, kruskal, components, edmonds_karp

app=Flask(__name__)
app.config.from_object(Config)
init_db()

def login_required(fn):
    @wraps(fn)
    def wrapped(*a,**kw):
        if "user" not in session: return redirect(url_for("login"))
        return fn(*a,**kw)
    return wrapped

def rows(sql,args=()):
    with connect() as db: return [dict(r) for r in db.execute(sql,args).fetchall()]

def save_analysis(module, locality, title, result):
    with connect() as db:
        db.execute("INSERT INTO analyses(module,locality,title,result_json,created_by) VALUES(?,?,?,?,?)",
                   (module,locality,title,json.dumps(result),session.get("user","demo")))

@app.route("/")
def home(): return redirect(url_for("dashboard") if "user" in session else url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username","").strip()
        with connect() as db: user=db.execute("SELECT * FROM users WHERE username=?",(username,)).fetchone()
        if user and check_password_hash(user["password_hash"],request.form.get("password","")):
            session["user"]=user["username"]; session["role"]=user["role"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password","error")
    return render_template("login.html")

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", facilities=rows("SELECT * FROM facilities"),
        locations=rows("SELECT * FROM locations"), analyses=rows("SELECT * FROM analyses ORDER BY id DESC LIMIT 8"),
        counts={"facilities":len(rows("SELECT id FROM facilities")),"localities":len(rows("SELECT id FROM locations")),
                "analyses":len(rows("SELECT id FROM analyses")),"versions":len(rows("SELECT id FROM network_versions"))})

@app.route("/map")
@login_required
def city_map(): return render_template("map.html", facilities=rows("SELECT * FROM facilities"), locations=rows("SELECT * FROM locations"))

@app.route("/accessibility",methods=["GET","POST"])
@login_required
def accessibility():
    result=None
    if request.method=="POST":
        loc=request.form.get("locality","Adyar")
        facilities=rows("SELECT * FROM facilities WHERE locality=? OR locality='Adyar'",(loc,))
        # A demonstrative road graph; weights are estimated minutes and are labelled as such.
        graph={"Residential Hub":[("Main Junction",4),("Lake Road",7)],"Main Junction":[("Residential Hub",4),("Hospital",6),("Metro",5)],
               "Lake Road":[("Residential Hub",7),("Hospital",4),("School",5)],"Hospital":[("Main Junction",6),("Lake Road",4),("Metro",3)],
               "School":[("Lake Road",5),("Metro",6)],"Metro":[("Main Junction",5),("Hospital",3),("School",6)]}
        shortest=dijkstra(graph,"Residential Hub","Hospital")
        alternative=alternative_path(graph,"Residential Hub","Hospital")
        degree={n:len(v) for n,v in graph.items()}
        result={"locality":loc,"shortest":shortest,"alternative":alternative,"connected_components":len(components(graph)),
                "critical_nodes":sorted(degree,key=degree.get,reverse=True)[:2],"facilities":facilities,
                "coverage":"Illustrative threshold coverage: 5 of 6 model nodes within the configured service threshold"}
        save_analysis("Accessibility",loc,"Urban accessibility analysis",result)
    return render_template("accessibility.html",locations=rows("SELECT * FROM locations"),result=result)

@app.route("/optimizer",methods=["GET","POST"])
@login_required
def optimizer():
    result=None
    if request.method=="POST":
        utility=request.form.get("utility","Water")
        nodes=["A","B","C","D","E","F"]
        edges=[("A","B",12),("B","C",8),("A","D",18),("D","C",7),("C","E",10),("B","E",20),("D","F",9),("F","E",11)]
        chosen,cost=kruskal(nodes,edges)
        baseline=sum(e[2] for e in edges)
        shared=round(cost*.12,2)
        result={"utility":utility,"edges":chosen,"optimized_cost":cost-shared,"baseline_cost":baseline,
                "savings":round(baseline-(cost-shared),2),"nodes":nodes,
                "note":"Illustrative cost units; shared-corridor discount is a configurable planning assumption."}
        with connect() as db:
            cur=db.execute("INSERT INTO network_versions(name,utility,locality,status) VALUES(?,?,?,?)",
                           ("Optimized "+utility+" network",utility,"Adyar","optimized"))
            vid=cur.lastrowid
            db.executemany("INSERT INTO utility_edges(version_id,source,target,cost,capacity,utility) VALUES(?,?,?,?,?,?)",
                           [(vid,u,v,w,100,utility) for u,v,w in chosen])
        save_analysis("Utility Optimization","Adyar","Kruskal network optimization",result)
    return render_template("optimizer.html",result=result)

@app.route("/conflicts",methods=["GET","POST"])
@login_required
def conflicts():
    result=None
    if request.method=="POST":
        # Candidate pairs are checked geometrically; sample coordinates are projected-scale approximations.
        from shapely.geometry import LineString
        lines={"Water main":LineString([(0,0),(10,10)]),"Power cable":LineString([(0,10),(10,0)]),
               "Drainage":LineString([(0,2),(10,2)])}
        found=[]
        names=list(lines)
        for i,a in enumerate(names):
            for b in names[i+1:]:
                if lines[a].intersects(lines[b]):
                    found.append({"a":a,"b":b,"type":"Intersection / overlap","severity":"High"})
                elif lines[a].distance(lines[b])<1.5:
                    found.append({"a":a,"b":b,"type":"Insufficient clearance","severity":"Medium"})
        result={"conflicts":found,"candidate_pairs":3,"index":"R-tree concept represented by bounding-box candidate filtering in this compact demo",
                "status":"Review required; no route is automatically approved."}
        save_analysis("Conflict Detection","Adyar","Infrastructure conflict scan",result)
    return render_template("conflicts.html",result=result)

@app.route("/resilience",methods=["GET","POST"])
@login_required
def resilience():
    result=None
    if request.method=="POST":
        capacity={"Source":{"A":12,"B":8},"A":{"B":5,"C":7},"B":{"C":10,"Sink":6},"C":{"Sink":12},"Sink":{}}
        flow,residual=edmonds_karp(capacity,"Source","Sink")
        failed=request.form.get("failure","Road closure")
        g={"A":[("B",1)],"B":[("A",1),("C",1)],"C":[("B",1)],"D":[]}
        result={"failure":failed,"max_flow":flow,"components_after_failure":components(g),
                "affected":"Illustrative downstream service zone C","priority":"Restore link B–C, then verify downstream connectivity",
                "note":"Capacity units and restoration priority are simulated, not live municipal telemetry."}
        save_analysis("Resilience Simulation","Adyar","Network failure simulation",result)
    return render_template("resilience.html",result=result)

@app.route("/reports")
@login_required
def reports(): return render_template("reports.html",analyses=rows("SELECT * FROM analyses ORDER BY id DESC"))

@app.route("/data")
@login_required
def data(): return render_template("data.html",locations=rows("SELECT * FROM locations"),facilities=rows("SELECT * FROM facilities"),versions=rows("SELECT * FROM network_versions ORDER BY id DESC"))

@app.route("/settings",methods=["GET","POST"])
@login_required
def settings():
    if request.method=="POST":
        with connect() as db:
            db.execute("INSERT INTO notifications(message) VALUES(?)",("Settings updated by "+session["user"],))
        flash("Settings saved.","success")
    return render_template("settings.html")

@app.route("/api/map")
@login_required
def api_map():
    return jsonify({"locations":rows("SELECT * FROM locations"),"facilities":rows("SELECT * FROM facilities")})

@app.route("/export.csv")
@login_required
def export_csv():
    data=rows("SELECT id,module,locality,title,result_json,created_by,created_at FROM analyses ORDER BY id DESC")
    output=io.StringIO(); writer=csv.DictWriter(output,fieldnames=list(data[0].keys()) if data else ["id","module","locality","title","result_json","created_by","created_at"])
    writer.writeheader(); writer.writerows(data)
    return send_file(io.BytesIO(output.getvalue().encode()),mimetype="text/csv",as_attachment=True,download_name="smart_city_analysis_history.csv")

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=False)
