"""
Lab Components Management System — Flask Backend Application.

Main entry point for the REST API server.
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from utils.database import check_db_connection

from routes.auth_routes import auth_bp
from routes.component_routes import component_bp
from routes.request_routes import request_bp
from routes.issue_routes import issue_bp
from routes.damage_routes import damage_bp
from routes.complaint_routes import complaint_bp


def create_app():
    """Create and configure the Flask application.

    Returns:
        Configured Flask app instance.
    """
    app = Flask(__name__)

    # ---- Logging ----
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # ---- CORS ----
    CORS(app, origins=[Config.CORS_ORIGIN], supports_credentials=True)

    # ---- Register Blueprints ----
    app.register_blueprint(auth_bp)
    app.register_blueprint(component_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(issue_bp)
    app.register_blueprint(damage_bp)
    app.register_blueprint(complaint_bp)

    # ---- Health Check ----
    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint that verifies database connectivity."""
        db_ok = check_db_connection()
        status_code = 200 if db_ok else 503
        return jsonify({
            "success": db_ok,
            "message": "Backend is running",
            "database": "connected" if db_ok else "disconnected",
        }), status_code

    # ---- Global Error Handlers ----
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "message": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "message": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal server error: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return app


# ---- Main Entry Point ----
if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
    )
