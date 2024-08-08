from flask import Flask, render_template, jsonify, request
from datetime import datetime
import pytz
import tzlocal

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/sync_duration', methods=['POST'])
def sync_duration():
    data = request.json
    date_str = data.get('date')
    time_str = data.get('time')
    target_timezone_str = data.get('targetTimezone')

    if not (date_str and time_str and target_timezone_str):
        return jsonify({'error': 'Missing data'}), 400

    try:
        # Adjust time format if necessary
        if len(time_str) == 5:
            time_str += ":00"

        # Parse and localize the target datetime
        local_tz = tzlocal.get_localzone()
        target_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        target_tz = pytz.timezone(target_timezone_str)
        target_time = target_tz.localize(target_datetime, is_dst=None)

        # Convert to UTC and calculate difference
        target_time_utc = target_time.astimezone(pytz.utc)
        current_utc_time = datetime.now(pytz.utc)
        time_difference = target_time_utc - current_utc_time
        total_seconds = int(time_difference.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Local time at the target timezone
        local_time_at_target = target_time_utc.astimezone(local_tz)
        local_time_str = local_time_at_target.strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'local_time_at_target': local_time_str
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
