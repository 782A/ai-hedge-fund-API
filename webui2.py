import os
import sys
# 確保 Python 可以找到 `src/` 內的模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
import json
from src.utils.db_utils import execute_query # Added import
from werkzeug.security import generate_password_hash, check_password_hash # Add this import
import threading
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sock import Sock
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from src.main import run_hedge_fund

# 加載 .env 環境變數
load_dotenv()

# 設置 Flask 伺服器
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 允許跨域請求
sock = Sock(app)

# WebSocket 客戶端列表
websocket_clients = []

# Function to log to database
def log_to_db(level, event_type, message, details_dict=None):
    details_json_str = json.dumps(details_dict) if details_dict else None
    query = "INSERT INTO system_logs (level, event_type, message, details_json) VALUES (%s, %s, %s, %s)"
    params = (level, event_type, message, details_json_str)
    try:
        execute_query(query, params=params, commit=True)
    except Exception as e:
        print(f"Failed to log to DB: {e}") # Fallback to console logging if DB log fails

def broadcast_log(message, level="info", event_type="GENERAL_EVENT", details_dict=None): # Added event_type and details_dict
    log_data = {"level": level, "message": message}
    if details_dict: # Optionally include details in WebSocket broadcast if needed
        log_data["details"] = details_dict

    # Log to database
    log_to_db(level, event_type, message, details_dict)

    # Broadcast to WebSocket clients
    for client in websocket_clients[:]:
        try:
            client.send(json.dumps(log_data))
        except Exception:
            websocket_clients.remove(client)

@app.route('/api/analysis', methods=['POST'])
def run_analysis():
    """執行對股票的分析"""
    request_id = None # Initialize request_id here so it's in scope for the main try/except
    try:
        data = request.get_json()
        user_id_req = data.get('user_id') # Get user_id from request if provided
        
        # Extract data for analysis_requests table
        ticker_list_req = data.get('tickers', '').split(',') # Use a different var name to avoid conflict if needed later
        selected_analysts_req = data.get('selectedAnalysts', [])
        model_name_req = data.get('modelName')
        end_date_req = data.get('endDate') or datetime.now().strftime('%Y-%m-%d')
        start_date_req = data.get('startDate') or (datetime.strptime(end_date_req, '%Y-%m-%d') - relativedelta(months=3)).strftime('%Y-%m-%d')

        try:
            tickers_str = ",".join(ticker_list_req)
            selected_analysts_json = json.dumps(selected_analysts_req)
            
            request_query = """
                INSERT INTO analysis_requests 
                (user_id, tickers, selected_analysts, model_name, start_date, end_date, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            request_params = (user_id_req, tickers_str, selected_analysts_json, model_name_req, start_date_req, end_date_req, 'processing')
            
            request_id = execute_query(request_query, params=request_params, commit=True) 
            
            if request_id:
                broadcast_log(f"Analysis request {request_id} logged and processing.", level="info", event_type="ANALYSIS_REQUEST_LOGGED", details_dict={"request_id": request_id, "tickers": tickers_str})
            else:
                broadcast_log("Failed to get request_id after insert.", level="warning", event_type="DB_INSERT_WARNING", details_dict={"query": request_query, "params": request_params})
                
        except Exception as db_e:
            broadcast_log(f"Failed to log analysis request to DB: {str(db_e)}", level="error", event_type="DB_INSERT_ERROR", details_dict={"error": str(db_e), "traceback": traceback.format_exc()})
            # request_id will remain None

        # Original variable names for run_hedge_fund
        ticker_list = data.get('tickers', '').split(',')
        selected_analysts = data.get('selectedAnalysts', [])
        model_name = data.get('modelName')
        end_date = data.get('endDate') or datetime.now().strftime('%Y-%m-%d')
        start_date = data.get('startDate') or (datetime.strptime(end_date, '%Y-%m-%d') - relativedelta(months=3)).strftime('%Y-%m-%d')
        
        # 初始投資組合
        broadcast_log(f"Received analysis request for tickers: {ticker_list} (Request ID: {request_id})", level="info", event_type="API_REQUEST_START", details_dict=data)
        portfolio = {
            "cash": data.get('initialCash', 100000),
            "positions": {},
            "cost_basis": {},
            "realized_gains": {ticker: {"long": 0.0, "short": 0.0} for ticker in ticker_list}
        }

        # 執行完整分析
        broadcast_log(f"Starting analysis for {ticker_list}", "info")
        result = run_hedge_fund(
            tickers=ticker_list,
            start_date=start_date,
            end_date=end_date,
            portfolio=portfolio,
            show_reasoning=True,
            selected_analysts=selected_analysts,
            model_name=model_name,
            model_provider="OpenAI",
            is_crypto=False
        )

        if request_id:
            try:
                raw_response_json_str = json.dumps(result)
                decisions_json_str = json.dumps(result.get("decisions"))
                analyst_signals_json_str = json.dumps(result.get("analyst_signals"))

                results_query = """
                    INSERT INTO analysis_results 
                    (request_id, raw_response_json, decisions_json, analyst_signals_json) 
                    VALUES (%s, %s, %s, %s)
                """
                results_params = (request_id, raw_response_json_str, decisions_json_str, analyst_signals_json_str)
                execute_query(results_query, params=results_params, commit=True)
                
                update_request_query = "UPDATE analysis_requests SET status = %s WHERE id = %s"
                execute_query(update_request_query, params=('completed', request_id), commit=True)
                
                broadcast_log(f"Analysis results for request {request_id} saved.", level="info", event_type="ANALYSIS_RESULT_SAVED", details_dict={"request_id": request_id})

                if result.get("decisions"):
                    log_to_db(level="info", event_type="AI_DECISION", 
                              message=f"AI decisions made for request {request_id}", 
                              details_dict={"request_id": request_id, "decisions": result.get("decisions")})
                if result.get("analyst_signals"):
                     log_to_db(level="info", event_type="AI_SIGNALS",
                               message=f"AI signals generated for request {request_id}",
                               details_dict={"request_id": request_id, "analyst_signals": result.get("analyst_signals")})

            except Exception as db_e:
                broadcast_log(f"Failed to save analysis results for request {request_id}: {str(db_e)}", level="error", event_type="DB_SAVE_RESULT_ERROR", details_dict={"request_id": request_id, "error": str(db_e), "traceback": traceback.format_exc()})
                try:
                    update_request_query = "UPDATE analysis_requests SET status = %s WHERE id = %s"
                    execute_query(update_request_query, params=('completed_save_failed', request_id), commit=True)
                except Exception as status_update_e:
                     broadcast_log(f"Failed to update status for request {request_id} after result save error: {str(status_update_e)}", level="error", event_type="DB_STATUS_UPDATE_ERROR")

        broadcast_log("Analysis completed successfully", level="success", event_type="API_REQUEST_SUCCESS", details_dict={"request_id": request_id, "tickers": ticker_list, "num_results": len(result.get("decisions", {}))})
        return jsonify(result)

    except Exception as e:
        if request_id:
            try:
                update_request_query = "UPDATE analysis_requests SET status = %s WHERE id = %s"
                execute_query(update_request_query, params=('failed', request_id), commit=True)
            except Exception as db_update_e:
                broadcast_log(f"Additionally, failed to update analysis request {request_id} status to 'failed' in DB: {str(db_update_e)}", level="error", event_type="DB_STATUS_UPDATE_ERROR_ON_FAIL")
        
        error_message = f"API Error in run_analysis (Request ID: {request_id}): {str(e)}"
        tb_str = traceback.format_exc()
        broadcast_log(error_message, level="error", event_type="API_ERROR", details_dict={"request_id": request_id, "error": str(e), "traceback": tb_str})
        return jsonify({"error": str(e), "traceback": tb_str}), 500

@sock.route('/ws/logs')
def logs(ws):
    """WebSocket 端點來監控日誌"""
    websocket_clients.append(ws)
    log_to_db("info", "WEBSOCKET_CONNECT", "New client connected") # Added DB log
    try:
        while True:
            ws.receive()  # 只是保持連線，前端不會傳送訊息
    except Exception:
        # It's good to log client disconnection, but be careful about logging errors from ws.receive() if they are frequent on client close
        log_to_db("info", "WEBSOCKET_DISCONNECT", "Client disconnected or error on receive") # Added DB log
        if ws in websocket_clients: # Check if client is still in the list before removing
            websocket_clients.remove(ws)

@app.route('/api/users/<int:user_id>/analyses', methods=['GET'])
def get_user_analyses(user_id):
    try:
        query = "SELECT id, tickers, selected_analysts, model_name, request_timestamp, status FROM analysis_requests WHERE user_id = %s ORDER BY request_timestamp DESC"
        analyses_tuples = execute_query(query, params=(user_id,), fetchall=True)
        if analyses_tuples is None:
            # Handle DB error
            log_to_db("error", "DB_QUERY_ERROR", "Failed to fetch user analyses.")
            return jsonify({"error": "Database query failed"}), 500
        analyses_list = []
        for row in analyses_tuples:
            s_analysts = None
            try:
                s_analysts = json.loads(row[2]) if row[2] else None
            except: pass # Keep as string if error
            analyses_list.append({
                "id": row[0], "tickers": row[1], "selected_analysts": s_analysts,
                "model_name": row[3], 
                "request_timestamp": row[4].isoformat() if row[4] else None, "status": row[5]
            })
        log_to_db("info", "API_ACCESS", f"User analyses retrieved for user: {user_id}")
        return jsonify(analyses_list), 200
    except Exception as e:
        log_to_db("error", "API_ERROR", f"Error in get_user_analyses: {str(e)}", {"traceback": traceback.format_exc()})
        return jsonify({"error": "Server error"}), 500

@app.route('/api/analyses/<int:analysis_id>', methods=['GET'])
def get_analysis_details(analysis_id):
    try:
        query = "SELECT ar.id, ar.user_id, ar.tickers, ar.selected_analysts, ar.model_name, ar.start_date, ar.end_date, ar.request_timestamp, ar.status, res.id, res.raw_response_json, res.decisions_json, res.analyst_signals_json, res.generated_at FROM analysis_requests ar LEFT JOIN analysis_results res ON ar.id = res.request_id WHERE ar.id = %s"
        row = execute_query(query, params=(analysis_id,), fetchone=True)
        if not row:
            return jsonify({"error": "Analysis not found"}), 404
        
        detail = {
            "request_id": row[0], "user_id": row[1], "tickers": row[2],
            "selected_analysts": json.loads(row[3]) if row[3] else None, "model_name": row[4],
            "start_date": row[5].isoformat() if row[5] else None, "end_date": row[6].isoformat() if row[6] else None,
            "request_timestamp": row[7].isoformat() if row[7] else None, "status": row[8],
            "result_id": row[9],
            "raw_response": json.loads(row[10]) if row[10] else None,
            "decisions": json.loads(row[11]) if row[11] else None,
            "analyst_signals": json.loads(row[12]) if row[12] else None,
            "generated_at": row[13].isoformat() if row[13] else None
        }
        # Simplified JSON parsing, assuming valid JSON is stored or null
        log_to_db("info", "API_ACCESS", f"Analysis details retrieved for id: {analysis_id}")
        return jsonify(detail), 200
    except Exception as e:
        log_to_db("error", "API_ERROR", f"Error in get_analysis_details: {str(e)}", {"traceback": traceback.format_exc()})
        return jsonify({"error": "Server error"}), 500

@app.route('/api/logs', methods=['GET'])
def get_system_logs():
    try:
        params_list = []
        filters_sql = []
        # Basic filtering
        if request.args.get('level'):
            filters_sql.append("level = %s")
            params_list.append(request.args.get('level'))
        if request.args.get('event_type'):
            filters_sql.append("event_type = %s")
            params_list.append(request.args.get('event_type'))
        
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = "SELECT id, timestamp, level, event_type, message, details_json FROM system_logs"
        if filters_sql:
            query += " WHERE " + " AND ".join(filters_sql)
        query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
        params_list.extend([limit, offset])

        logs_tuples = execute_query(query, params=tuple(params_list), fetchall=True)
        if logs_tuples is None:
            # Handle DB error
            print(f"CRITICAL: DB query failed in get_system_logs") # Avoid log_to_db for log endpoint
            return jsonify({"error": "Database query failed"}), 500

        logs_list = []
        for row in logs_tuples:
            details = None
            try:
                details = json.loads(row[5]) if row[5] else None
            except: pass
            logs_list.append({
                "id": row[0], "timestamp": row[1].isoformat() if row[1] else None,
                "level": row[2], "event_type": row[3], "message": row[4], "details": details
            })
        return jsonify(logs_list), 200
    except Exception as e:
        print(f"CRITICAL: Error in get_system_logs: {str(e)}") # Avoid log_to_db for log endpoint
        return jsonify({"error": "Server error"}), 500

if __name__ == "__main__":
    api_thread = threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 6000, "debug": True, "use_reloader": False})
    api_thread.daemon = True
    api_thread.start()
    print("API Server started on http://localhost:6000")
    
    # Register and Login Endpoints
    @app.route('/api/register', methods=['POST'])
    def register_user():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            return jsonify({"error": "Username, password, and email are required"}), 400

        # Check if user or email already exists
        try:
            query_check = "SELECT id FROM users WHERE username = %s OR email = %s"
            existing_user = execute_query(query_check, params=(username, email), fetchone=True)
            if existing_user:
                log_to_db("warn", "REGISTRATION_FAIL", f"Attempt to register existing user/email: {username}/{email}")
                return jsonify({"error": "Username or email already exists"}), 409
        except Exception as e:
            log_to_db("error", "DB_QUERY_ERROR", f"Error checking existing user: {str(e)}", {"username": username, "email": email})
            return jsonify({"error": f"Database error: {str(e)}"}), 500
            
        password_hash = generate_password_hash(password)
        
        try:
            insert_query = "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)"
            user_id = execute_query(insert_query, params=(username, password_hash, email), commit=True)
            if user_id:
                log_to_db("info", "USER_REGISTRATION", f"User registered: {username}", {"user_id": user_id})
                return jsonify({"message": "User registered successfully", "user_id": user_id}), 201
            else:
                log_to_db("error", "REGISTRATION_FAIL", f"User registration failed for {username} after DB insert.", {"username": username})
                return jsonify({"error": "User registration failed"}), 500
        except Exception as e:
            log_to_db("error", "DB_INSERT_ERROR", f"Error registering user {username}: {str(e)}", {"username": username})
            return jsonify({"error": f"Database error during registration: {str(e)}"}), 500

    @app.route('/api/login', methods=['POST'])
    def login_user():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        try:
            query = "SELECT id, password_hash FROM users WHERE username = %s"
            user_data = execute_query(query, params=(username,), fetchone=True) # Assuming fetchone returns a dict or tuple

            if user_data:
                # Assuming user_data is a tuple (id, password_hash) or dict
                user_id = user_data[0] if isinstance(user_data, tuple) else user_data.get('id')
                stored_password_hash = user_data[1] if isinstance(user_data, tuple) else user_data.get('password_hash')
                
                if check_password_hash(stored_password_hash, password):
                    log_to_db("info", "USER_LOGIN_SUCCESS", f"User login successful: {username}", {"user_id": user_id})
                    # For now, just return user_id. Real app would use tokens/sessions.
                    return jsonify({"message": "Login successful", "user_id": user_id, "username": username}), 200
                else:
                    log_to_db("warn", "USER_LOGIN_FAIL", f"Invalid password for user: {username}", {"username": username})
                    return jsonify({"error": "Invalid username or password"}), 401
            else:
                log_to_db("warn", "USER_LOGIN_FAIL", f"User not found: {username}", {"username": username})
                return jsonify({"error": "Invalid username or password"}), 401
        except Exception as e:
            log_to_db("error", "DB_QUERY_ERROR", f"Error during login for user {username}: {str(e)}", {"username": username})
            return jsonify({"error": f"Database error during login: {str(e)}"}), 500
            
    api_thread.join()
