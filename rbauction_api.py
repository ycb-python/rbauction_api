import time
import json
import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)
df = pd.read_csv('rbauction.csv')

@app.route('/<title>', methods=['GET'])

def get_vehicle_data(title):
    filtered_df = df[df['Title'].str.contains(title, case=False, na=False)]
    if filtered_df.empty:
        return jsonify({'error': 'No matching vehicles found'}), 404
    data = filtered_df.to_dict(orient='records')
    return jsonify(data)
if __name__ == '__main__':
    app.run(debug=True)
