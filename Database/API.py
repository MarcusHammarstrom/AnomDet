import os
import csv
from flask import Flask, request, jsonify
import psycopg2
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection details
DB_CONFIG = {
    'dbname': 'mytimescaledb',
    'user': 'Anomdet',
    'password': 'G5anomdet',
    'host': 'localhost',
    'port': 5432
}

# Helper function to connect to the database
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to upload and import CSV data into table created in TimescaleDB
@app.route('/import_csv', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            import_csv_to_db(filepath)
            return jsonify({"message": "CSV data imported successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            os.remove(filepath)

    return jsonify({"error": "Invalid file type"}), 400

# Function to import CSV data into TimescaleDB
def import_csv_to_db(filepath):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Performance_metrics with its attributes 
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            cursor.execute(
                """
                INSERT INTO peformance_metrics (timestamp, load_1m, load_5m, load_15m, sys_mem_swap_total, sys_mem_swap_free, sys_mem_free,
              sys_mem_cache, sys_mem_buffered, sys_mem_available, sys_mem_total, cpu_iowait, cpu_system, cpu_user, disk_io_time, disk_bytes_read,
              disk_bytes_written, disk_io_read, disk_io_write, sys_fork_rate, sys_interrupt_rate, sys_context_switch_rate, server_up)
                VALUES (%.5f, %.5f, %.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,Boolean)
                """,
                (row[0], row[1], row[2],row[3], row[4], row[5],row[6], row[7], row[8],row[9], row[10], row[11],row[12], row[13], row[14])
            )

    conn.commit()
    cursor.close()
    conn.close()

# Route to fetch data in table
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM performance_metrics LIMIT 100;")
        rows = cursor.fetchall()
        conn.close()

        # Return data as JSON
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create uploads folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)