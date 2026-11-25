import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import altair as alt
import pandas as pd


class AnalyticsData:
    """
    In-memory Star Schema persistence for Web Analytics.
    
    Dimension Table:
      - dim_sessions: Visitor context, physical sit-downs, and logical missions.
    Fact Tables:
      - fact_requests: Every HTTP request hit.
      - fact_queries: Every search query executed, term counts, order, and mission ID.
      - fact_clicks: Every result document click, rank, related query, and dwell time.
    """

    SESSION_TIMEOUT_SECONDS = 30 * 60  #when 30 minutes pass, new session

    def __init__(self):
        #save info for each session_id: {session_id: {session_data}}
        self.dim_sessions: Dict[str, dict] = {}

        #save info for request
        self.fact_requests: List[dict] = []
        #save info for search queries
        self.fact_queries: List[dict] = []
        #save info for clicks on documents
        self.fact_clicks: List[dict] = []

        #helper lookup for fast click counts per doc_id: {doc_id: int}
        self.doc_click_counts: Dict[str, int] = {}

        #counters for sequential ID generation
        self._request_counter = 0
        self._search_counter = 0
        self._click_counter = 0

    ##########################################################################
    #Session and user management (dim_sessions)
    ##########################################################################
    def get_or_create_session(
        self,
        session_id: Optional[str],
        ip_address: str,
        agent_info: dict,
        country: str = "Unknown",
        city: str = "Unknown",
    ) -> str:
        """
        Validates an existing physical session or creates a new one if none exists
        or if the user has been inactive for > SESSION_TIMEOUT_SECONDS.
        """
        now = time.time()
        dt_now = datetime.fromtimestamp(now)

        if session_id and session_id in self.dim_sessions:
            sess = self.dim_sessions[session_id]
            #check session timeout
            if (now - sess["last_active_ts"]) <= self.SESSION_TIMEOUT_SECONDS:
                sess["last_active_ts"] = now
                sess["last_active"] = dt_now.strftime("%Y-%m-%d %H:%M:%S")
                return session_id

        #create a new session
        new_session_id = str(uuid.uuid4()) #id generated for a new session
        browser_name = agent_info.get("browser", {}).get("name", "Unknown")
        os_name = agent_info.get("os", {}).get("name", "Unknown")
        platform_name = agent_info.get("platform", {}).get("name", "")

        #determine device type based on keywords
        mobile_keywords = ("android", "iphone", "ipad", "mobile", "ios")
        raw_check = f"{os_name} {platform_name}".lower()
        device_type = "Mobile" if any(k in raw_check for k in mobile_keywords) else "Desktop"

        self.dim_sessions[new_session_id] = {
            "session_id": new_session_id,
            "ip_address": ip_address or "127.0.0.1",
            "browser": browser_name,
            "os": os_name,
            "device_type": device_type,
            "country": country,
            "city": city,
            "start_ts": now,
            "last_active_ts": now,
            "start_time": dt_now.strftime("%Y-%m-%d %H:%M:%S"),
            "last_active": dt_now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": dt_now.strftime("%Y-%m-%d"),
            "hour_of_day": dt_now.hour,
            "mission_count": 0,
            "last_query_terms": set(),
            "current_mission_id": None,
        }
        return new_session_id

    ##########################################################################
    #HTTP request tracking (fact_requests)
    ##########################################################################
    def log_request(self, session_id: str, endpoint: str, method: str, path: str) -> int:
        """Logs every HTTP request hitting the web application."""
        self._request_counter += 1
        now = time.time()
        dt_now = datetime.fromtimestamp(now)

        record = {
            "request_id": self._request_counter,
            "session_id": session_id,
            "endpoint": endpoint,
            "method": method,
            "path": path,
            "timestamp": now,
            "datetime": dt_now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": dt_now.strftime("%Y-%m-%d"),
            "hour_of_day": dt_now.hour,
        }
        self.fact_requests.append(record)
        return self._request_counter

    ##########################################################################
    #search queries and missions (fact_queries)
    ##########################################################################
    def save_query_terms(
        self,
        terms: str,
        session_id: Optional[str] = None,
        num_results: int = 0,
    ) -> int:
        """
        Records a search query, extracts term count & order, and assigns
        a logical mission_id based on term overlap with the previous query.
        """
        self._search_counter += 1
        search_id = self._search_counter
        now = time.time()
        dt_now = datetime.fromtimestamp(now)

        clean_terms = [t.strip().lower() for t in terms.split() if t.strip()]
        term_set = set(clean_terms)

        #mission detection in the same session (multiple queries with same goal)
        mission_id = f"{session_id}_m1" if session_id else f"anon_m{search_id}"
        if session_id and session_id in self.dim_sessions:
            sess = self.dim_sessions[session_id]
            prev_terms = sess["last_query_terms"]
            #if the current query has no overlapping terms with the previous query, start a new mission
            if not prev_terms or len(term_set.intersection(prev_terms)) == 0:
                sess["mission_count"] += 1
                sess["current_mission_id"] = f"{session_id}_m{sess['mission_count']}"
            sess["last_query_terms"] = term_set
            mission_id = sess["current_mission_id"]

        record = {
            "search_id": search_id,
            "session_id": session_id,
            "mission_id": mission_id,
            "raw_query": terms,
            "terms": clean_terms, #preserves exact term order
            "num_terms": len(clean_terms),
            "num_results": num_results,
            "timestamp": now,
            "datetime": dt_now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": dt_now.strftime("%Y-%m-%d"),
            "hour_of_day": dt_now.hour,
        }
        self.fact_queries.append(record)
        return search_id

    def update_query_result_count(self, search_id: int, num_results: int) -> None:
        """Updates num_results once search_engine.search() finishes."""
        for q in reversed(self.fact_queries):
            if q["search_id"] == search_id:
                q["num_results"] = num_results
                break

    ##########################################################################
    #Document clicks, ranks and dwell time (fact_clicks)
    ##########################################################################
    def log_click(
        self,
        doc_id: str,
        session_id: Optional[str] = None,
        search_id: Optional[int] = None,
        rank: Optional[int] = None,
    ) -> int:
        """
        Records a click on a document result, its ranking position,
        and the search_id that produced it. Initializes dwell_time_seconds as None.
        """
        self._click_counter += 1
        click_id = self._click_counter
        now = time.time()
        dt_now = datetime.fromtimestamp(now)

        record = {
            "click_id": click_id,
            "session_id": session_id,
            "search_id": search_id,
            "doc_id": doc_id,
            "rank": rank,
            "click_timestamp": now,
            "datetime": dt_now.strftime("%Y-%m-%d %H:%M:%S"),
            "dwell_time_seconds": None,  #update when user goes back to search results
        }
        self.fact_clicks.append(record)

        #update the click count for the document
        self.doc_click_counts[doc_id] = self.doc_click_counts.get(doc_id, 0) + 1
        return click_id

    def record_dwell_time(self, click_id: int, dwell_seconds: float) -> None:
        """Updates dwell time for a click when the user navigates back."""
        for c in reversed(self.fact_clicks):
            if c["click_id"] == click_id:
                c["dwell_time_seconds"] = round(dwell_seconds, 2)
                break

    ##########################################################################
    #Metrics
    ##########################################################################
    def get_summary_metrics(self) -> dict:
        """Computes high-level KPIs for the analytics dashboard."""
        total_sessions = len(self.dim_sessions)
        total_requests = len(self.fact_requests)
        total_searches = len(self.fact_queries)
        total_clicks = len(self.fact_clicks)

        #search success rate (how many searches resulted in at least one click)
        searches_with_clicks = {
            c["search_id"] for c in self.fact_clicks if c["search_id"] is not None
        }
        ssr = round((len(searches_with_clicks) / total_searches) * 100, 2) if total_searches > 0 else 0.0

        #average click rank
        ranks = [c["rank"] for c in self.fact_clicks if c["rank"] is not None]
        avg_rank = round(sum(ranks) / len(ranks), 2) if ranks else 0.0

        #average dwell time (excluding unclosed clicks)
        dwells = [c["dwell_time_seconds"] for c in self.fact_clicks if c["dwell_time_seconds"] is not None]
        avg_dwell = round(sum(dwells) / len(dwells), 2) if dwells else 0.0

        #average queries per logical mission (how many queries until users looks for somethings else)
        missions = {q["mission_id"] for q in self.fact_queries if q["mission_id"]}
        avg_queries_per_mission = round(total_searches / len(missions), 2) if missions else 0.0

        return {
            "total_sessions": total_sessions,
            "total_requests": total_requests,
            "total_searches": total_searches,
            "total_clicks": total_clicks,
            "ssr": ssr,
            "avg_rank": avg_rank,
            "avg_dwell": avg_dwell,
            "total_missions": len(missions),
            "avg_queries_per_mission": avg_queries_per_mission,
        }

    ##########################################################################
    #Charts
    ##########################################################################
    def plot_number_of_views(self) -> str:
        if not self.doc_click_counts:
            return "<p style='font-family:sans-serif;color:#666;'>No document clicks recorded yet.</p>"
        data = [
            {"Document ID": doc_id, "Number of Views": count}
            for doc_id, count in self.doc_click_counts.items()
        ]
        df = pd.DataFrame(data).sort_values(by="Number of Views", ascending=False).head(15)
        chart = (
            alt.Chart(df)
            .mark_bar(color="#4c78a8")
            .encode(
                x=alt.X("Document ID:N", sort="-y", title="Product ID"),
                y=alt.Y("Number of Views:Q", title="Clicks"),
                tooltip=["Document ID", "Number of Views"],
            )
            .properties(title="Top Clicked Documents", width=500, height=300)
        )
        return chart.to_html()


class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter

    def to_json(self):
        return self.__dict__

    def __str__(self):
        return json.dumps(self)