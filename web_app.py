import os
from json import JSONEncoder

import httpagentparser  # for getting the user agent as json
from flask import Flask, render_template, session
from flask import request

import time

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine
from myapp.generation.rag import RAGGenerator
from myapp.generation.rag_improved import ImprovedRAGGenerator, parse_constraints
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env


# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)
_default.default = JSONEncoder().default
JSONEncoder.default = _default
# end lines ***for using method to_json in objects ***


# instantiate the Flask application
app = Flask(__name__)

# random 'secret_key' is used for persisting data in secure cookie
app.secret_key = os.getenv("SECRET_KEY")
# open browser dev tool to see the cookies
app.session_cookie_name = os.getenv("SESSION_COOKIE_NAME")
# load documents corpus into memory.
full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
file_path = path + "/" + os.getenv("DATA_FILE_PATH")
corpus = load_corpus(file_path)
# Log first element of corpus to verify it loaded correctly:
print("\nCorpus is loaded... \n First element:\n", list(corpus.values())[0])
# instantiate our search engine
search_engine = SearchEngine(file_path)
# instantiate our in memory persistence
analytics_data = AnalyticsData()
# instantiate RAG generator: the improved one by default, RAG_MODE=baseline in .env for the original
if os.getenv("RAG_MODE", "improved") == "baseline":
    rag_generator = RAGGenerator()
else:
    rag_generator = ImprovedRAGGenerator(corpus=corpus)

@app.before_request
def track_request_and_session():
    if request.endpoint == "static" or request.path.startswith("/static") or request.path == "/favicon.ico":
        return

    now = time.time()

    # Close dwell time if user was viewing a product details page
    active_click_id = session.pop("active_click_id", None)
    click_start_ts = session.pop("click_start_ts", None)
    if active_click_id is not None and click_start_ts is not None:
        analytics_data.record_dwell_time(active_click_id, max(0.0, now - click_start_ts))

    # Validate or create session (30-min timeout)
    agent_info = httpagentparser.detect(request.headers.get("User-Agent", ""))
    user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    valid_sid = analytics_data.get_or_create_session(
        session_id=session.get("analytics_session_id"),
        ip_address=user_ip,
        agent_info=agent_info,
    )
    session["analytics_session_id"] = valid_sid

    # Log request (ignore chart iframes)
    chart_endpoints = {
        "plot_number_of_views",
        "plot_clicks_by_rank",
        "plot_top_terms",
        "plot_dwell_by_rank",
        "plot_requests_by_page",
    }
    if request.endpoint not in chart_endpoints:
        analytics_data.log_request(valid_sid, request.endpoint or "unknown", request.method, request.path)

# Home URL "/"
@app.route('/')
def index():
    print("starting home url /...")

    # flask server creates a session by persisting a cookie in the user's browser.
    # the 'session' object keeps data between multiple requests. Example:
    session['some_var'] = "Some value that is kept in session"

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent)

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))
    print(session)
    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['POST'])
def search_form_post():
    
    search_query = request.form['search-query']
    algorithm = request.values.get('algorithm', 'custom') #tune to use other algorithms

    session['last_search_query'] = search_query

    sid = session.get('analytics_session_id') 
    search_id = analytics_data.save_query_terms(search_query, session_id=sid)
    session['last_search_id'] = search_id

    # price and rating phrases ("under 800", "4+ stars") are removed before retrieval: they never appear in
    # product text, so with AND semantics they would make every search return nothing
    # the limits themselves are applied inside the search, to all matches before the top 20 are cut
    constraints = parse_constraints(search_query)
    limits = {k: constraints[k] for k in ("max_price", "min_price", "min_rating")}
    results = search_engine.search(constraints["clean_query"], search_id, corpus, algorithm=algorithm, **limits)

    # if no product respects the limits, the RAG gets the unfiltered matches so it can say why (e.g. cheapest is 499)
    rag_input = results
    if not results and any(v is not None for v in limits.values()):
        rag_input = search_engine.search(constraints["clean_query"], search_id, corpus, algorithm=algorithm)

    # generate RAG response based on user query and retrieved results
    rag_response = rag_generator.generate_response(search_query, rag_input)
    print("RAG response:", rag_response)

    found_count = len(results)
    analytics_data.update_query_result_count(search_id, found_count) 
    session['last_found_count'] = found_count

    print(session)

    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count, rag_response=rag_response, search_id=search_id)

@app.route('/doc_details', methods=['GET'])
def doc_details():
    """
    Show document details page
    ### Replace with your custom logic ###
    """
    print("doc details session: ")
    print(session)

    res = session.get("some_var") 
    print("recovered var from session:", res)

    # get the query string parameters from request
    clicked_doc_id = request.args.get("pid")

    rank_param = request.args.get("rank", type=int) 
    search_id_param = request.args.get("search_id", type=int) or session.get("last_search_id") 
    sid = session.get("analytics_session_id") 

    print("click in id={} (rank={}, search_id={})".format(clicked_doc_id, rank_param, search_id_param))

    #store click in fact_clicks and start dwell timer
    if clicked_doc_id:
        click_id = analytics_data.log_click(
            doc_id=clicked_doc_id,
            session_id=sid,
            search_id=search_id_param,
            rank=rank_param,
        )
        session["active_click_id"] = click_id 
        session["click_start_ts"] = time.time() 

    print("doc_click_counts for id={} is {}".format(clicked_doc_id, analytics_data.doc_click_counts.get(clicked_doc_id, 0)))
    print(analytics_data.fact_clicks)
    doc = corpus.get(clicked_doc_id)
    return render_template('doc_details.html', doc=doc)


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with yourdashboard ###
    :return:
    """

    docs = []
    for doc_id, count in analytics_data.doc_click_counts.items(): 
        if doc_id in corpus:
            row: Document = corpus[doc_id]
            doc = StatsDocument(pid=row.pid, title=row.title, description=row.description, url=row.url, count=count)
            docs.append(doc)
    
    #simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)
    return render_template('stats.html', clicks_data=docs, page_title="Stats")


@app.route('/dashboard', methods=['GET'])
def dashboard():
    visited_docs = []
    for doc_id, count in analytics_data.doc_click_counts.items(): 
        if doc_id in corpus:
            d: Document = corpus[doc_id]
            doc = ClickedDoc(doc_id, d.title, count)
            visited_docs.append(doc)

    #simulate sort by ranking
    visited_docs.sort(key=lambda doc: doc.counter, reverse=True)

    for doc in visited_docs: print(doc)

    metrics = analytics_data.get_summary_metrics()
    chart_data = analytics_data.get_chart_data() 

    return render_template(
        'dashboard.html',
        page_title="Analytics Dashboard",
        visited_docs=visited_docs,
        metrics=metrics,
        chart_data=chart_data,
        sessions=list(analytics_data.dim_sessions.values()),
        recent_queries=list(reversed(analytics_data.fact_queries[-15:])),
    )


# New route added for generating an examples of basic Altair plot (used for dashboard)
@app.route('/plot_number_of_views', methods=['GET'])
def plot_number_of_views():
    return analytics_data.plot_number_of_views()

@app.route('/plot_clicks_by_rank', methods=['GET'])
def plot_clicks_by_rank():
    return analytics_data.plot_clicks_by_rank()

@app.route('/plot_top_terms', methods=['GET'])
def plot_top_terms():
    return analytics_data.plot_top_terms()

@app.route('/plot_dwell_by_rank', methods=['GET'])
def plot_dwell_by_rank():
    return analytics_data.plot_dwell_by_rank()

@app.route('/plot_requests_by_page', methods=['GET'])
def plot_requests_by_page():
    return analytics_data.plot_requests_by_page()



if __name__ == "__main__":
    #indexes are not build twice like this
    debug_mode = str(os.getenv("DEBUG", "False")).lower() == "true"
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=debug_mode, use_reloader=False)
