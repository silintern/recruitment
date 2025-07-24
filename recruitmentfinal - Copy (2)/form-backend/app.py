#!/usr/bin/env python3
"""
Separate Flask Backend for Recruitment Form
This backend handles form submissions and serves the form configuration
"""

import os
import sqlite3
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from collections import defaultdict
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App initialization
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
app.config.update({
    'SECRET_KEY': os.environ.get('FLASK_SECRET_KEY', 'form-backend-secret-key-123'),
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
    'UPLOAD_FOLDER': 'uploads',
    'DATABASE_PATH': '../dashboard/recruitment_final.db',  # Path to shared database
    'ALLOWED_EXTENSIONS': {'pdf', 'doc', 'docx'},
    'DEBUG': os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
})

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_db_connection():
    """Get database connection to the shared dashboard database"""
    try:
        conn = sqlite3.connect(app.config['DATABASE_PATH'], check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def validate_form_data(data, form_config):
    """Validate form data against configuration"""
    errors = []
    
    for section_name, fields in form_config.items():
        for field in fields:
            field_name = field['name']
            field_value = data.get(field_name, '').strip()
            
            # Check required fields
            if field['required'] and not field_value:
                errors.append(f"{field['label']} is required")
                continue
            
            # Skip validation for empty optional fields
            if not field_value:
                continue
                
            # Type-specific validation
            field_type = field['type']
            
            if field_type == 'email' and field_value:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, field_value):
                    errors.append(f"{field['label']} must be a valid email address")
            
            elif field_type == 'tel' and field_value:
                # Basic phone number validation (digits, spaces, +, -, ())
                import re
                phone_pattern = r'^[\+]?[0-9\s\-\(\)]{10,15}$'
                if not re.match(phone_pattern, field_value):
                    errors.append(f"{field['label']} must be a valid phone number")
            
            elif field_type == 'number' and field_value:
                try:
                    float(field_value)
                except ValueError:
                    errors.append(f"{field['label']} must be a valid number")
            
            elif field_type == 'date' and field_value:
                try:
                    datetime.strptime(field_value, '%Y-%m-%d')
                except ValueError:
                    errors.append(f"{field['label']} must be a valid date")
    
    return errors

@app.errorhandler(413)
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    """Handle file size too large error"""
    return jsonify({
        "error": "File too large",
        "message": "The uploaded file exceeds the maximum size limit of 16MB"
    }), 413

@app.errorhandler(500)
def handle_internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected"
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }), 503

@app.route('/api/form-config', methods=['GET'])
def get_public_form_config():
    """Public endpoint to fetch the form structure for applicants"""
    try:
        conn = get_db_connection()
        
        # Get section order from form_sections table if it exists
        section_order = {}
        try:
            sections_query = conn.execute(
                "SELECT name, section_order FROM form_sections ORDER BY section_order ASC"
            ).fetchall()
            section_order = {row['name']: row['section_order'] for row in sections_query}
        except sqlite3.OperationalError:
            # Table doesn't exist yet, use default ordering
            pass
        
        # Get all form fields ordered by field_order
        fields_query = conn.execute(
            "SELECT * FROM form_config ORDER BY field_order ASC, id ASC"
        ).fetchall()
        conn.close()
        
        # Group fields by subsection for easier rendering
        subsections = defaultdict(list)
        for field in fields_query:
            field_dict = dict(field)
            # Convert boolean values for JSON serialization
            field_dict['required'] = bool(field_dict['required'])
            field_dict['is_core'] = bool(field_dict['is_core'])
            subsections[field['subsection']].append(field_dict)
        
        # Order subsections by section_order if available
        if section_order:
            subsection_order = sorted(
                subsections.keys(), 
                key=lambda k: section_order.get(k, 9999)
            )
        else:
            # Fallback: maintain order based on first field's order in each section
            subsection_order = sorted(
                subsections.keys(), 
                key=lambda k: min(f['field_order'] for f in subsections[k]) if subsections[k] else 0
            )
        
        ordered_subsections = {k: subsections[k] for k in subsection_order}
        
        logger.info(f"Served form configuration with {len(fields_query)} fields in {len(ordered_subsections)} sections")
        
        return jsonify({
            "success": True,
            "sections": ordered_subsections,
            "metadata": {
                "total_fields": len(fields_query),
                "total_sections": len(ordered_subsections),
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error loading form configuration: {e}")
        return jsonify({
            "error": "Configuration error",
            "message": "Unable to load form configuration. Please try again later."
        }), 500

@app.route('/api/submit-application', methods=['POST'])
def submit_application():
    """Handle form submission with file upload and validation"""
    try:
        # Check if resume file is present
        if 'cv-resume' not in request.files:
            return jsonify({
                "error": "Missing resume",
                "message": "Please upload your resume/CV"
            }), 400
        
        resume_file = request.files['cv-resume']
        if resume_file.filename == '':
            return jsonify({
                "error": "No file selected",
                "message": "Please select a resume file to upload"
            }), 400

        # Validate file type
        if not allowed_file(resume_file.filename):
            return jsonify({
                "error": "Invalid file type",
                "message": f"Please upload a file with one of these extensions: {', '.join(app.config['ALLOWED_EXTENSIONS'])}"
            }), 400

        # Get form data
        form_data = request.form.to_dict()
        
        # Validate required fields
        if not form_data.get('name') or not form_data.get('email'):
            return jsonify({
                "error": "Missing required information",
                "message": "Name and email are required fields"
            }), 400

        # Get form configuration for validation
        conn = get_db_connection()
        try:
            fields_query = conn.execute("SELECT * FROM form_config").fetchall()
            
            # Group fields by subsection for validation
            form_config = defaultdict(list)
            for field in fields_query:
                form_config[field['subsection']].append(dict(field))
            
            # Validate form data
            validation_errors = validate_form_data(form_data, form_config)
            if validation_errors:
                return jsonify({
                    "error": "Validation failed",
                    "message": "Please correct the following errors:",
                    "details": validation_errors
                }), 400

            # Save the resume file
            email = secure_filename(form_data.get('email', 'unknown'))
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = secure_filename(resume_file.filename)
            unique_filename = f"{email}_{timestamp}_{filename}"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            resume_file.save(file_path)
            
            # Prepare data for database insertion
            form_data['resume_path'] = unique_filename
            form_data['submission_timestamp'] = datetime.utcnow().isoformat()
            
            # Get valid database columns
            valid_columns = {field['name'] for field in fields_query}
            valid_columns.add('resume_path')
            valid_columns.add('submission_timestamp')
            
            # Filter form data to only include valid columns
            columns_to_insert = [col for col in form_data.keys() if col in valid_columns]
            values_to_insert = [form_data[col] for col in columns_to_insert]
            
            if not columns_to_insert:
                return jsonify({
                    "error": "No valid data",
                    "message": "No valid form data received"
                }), 400

            # Insert into database
            placeholders = ', '.join(['?'] * len(columns_to_insert))
            query = f"INSERT INTO applications ({', '.join(columns_to_insert)}) VALUES ({placeholders})"
            
            cursor = conn.cursor()
            cursor.execute(query, values_to_insert)
            application_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"New application submitted: ID {application_id}, Email: {form_data.get('email')}")
            
            return jsonify({
                "success": True,
                "message": "Application submitted successfully!",
                "application_id": application_id,
                "submitted_at": form_data['submission_timestamp']
            })
            
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                return jsonify({
                    "error": "Duplicate application",
                    "message": f"An application with the email '{form_data.get('email')}' already exists."
                }), 409
            else:
                raise
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error submitting application: {e}")
        return jsonify({
            "error": "Submission failed",
            "message": "An error occurred while submitting your application. Please try again."
        }), 500

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """Serve uploaded files (for resume viewing)"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({
            "error": "File not found",
            "message": "The requested file could not be found"
        }), 404

@app.route('/api/statistics', methods=['GET'])
def get_form_statistics():
    """Get basic form submission statistics"""
    try:
        conn = get_db_connection()
        
        # Get total applications
        total_apps = conn.execute("SELECT COUNT(*) as count FROM applications").fetchone()['count']
        
        # Get applications by date (last 30 days)
        recent_apps = conn.execute("""
            SELECT DATE(submission_timestamp) as date, COUNT(*) as count
            FROM applications 
            WHERE submission_timestamp >= datetime('now', '-30 days')
            GROUP BY DATE(submission_timestamp)
            ORDER BY date DESC
        """).fetchall()
        
        # Get popular positions
        popular_positions = conn.execute("""
            SELECT post_applying_for, COUNT(*) as count
            FROM applications 
            WHERE post_applying_for IS NOT NULL AND post_applying_for != ''
            GROUP BY post_applying_for
            ORDER BY count DESC
            LIMIT 10
        """).fetchall()
        
        conn.close()
        
        return jsonify({
            "success": True,
            "statistics": {
                "total_applications": total_apps,
                "recent_submissions": [dict(row) for row in recent_apps],
                "popular_positions": [dict(row) for row in popular_positions]
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({
            "error": "Statistics unavailable",
            "message": "Unable to retrieve form statistics"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Different port from dashboard
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Form Backend server on {host}:{port}")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Database path: {app.config['DATABASE_PATH']}")
    
    app.run(host=host, port=port, debug=app.config['DEBUG'])