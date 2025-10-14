"""
Error handlers for do2done application.
"""
from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register error handlers with the Flask app"""

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        logger.warning(f"Bad Request: {request.url} - {error}")
        if request.is_json:
            return jsonify(error='Bad Request', message=str(error)), 400
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        logger.warning(f"Forbidden: {request.url} - {error}")
        if request.is_json:
            return jsonify(error='Forbidden', message=str(error)), 403
        return render_template('errors/403.html', error=error), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        logger.info(f"Not Found: {request.url}")
        if request.is_json:
            return jsonify(error='Not Found', message='Resource not found'), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        logger.warning(f"Method Not Allowed: {request.method} {request.url}")
        if request.is_json:
            return jsonify(error='Method Not Allowed', message=str(error)), 405
        return render_template('errors/405.html', error=error), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server errors"""
        logger.error(f"Internal Server Error: {request.url} - {error}", exc_info=True)
        if request.is_json:
            return jsonify(error='Internal Server Error', message='An error occurred'), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle uncaught exceptions"""
        # Pass through HTTP errors
        if isinstance(error, HTTPException):
            return error

        # Log the error
        logger.error(f"Unhandled exception: {error}", exc_info=True)

        # Return error response
        if request.is_json:
            return jsonify(error='Internal Server Error', message='An error occurred'), 500
        return render_template('errors/500.html'), 500
