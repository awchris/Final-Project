from flask import Flask, render_template, request
from final_pieces import get_key_data
app = Flask(__name__)

@app.route("/")
def main_handler():
    app.logger.info('In MainHandler')
    return render_template('reqform-template.html', page_title='Route Form')

@app.route("/reqresponse")
def get_request_handler():
    loc1 = request.args.get('location1')
    loc2 = request.args.get('location2')
    key_data = get_key_data(loc1,loc2)
    if key_data != None:
        sunset = key_data['sunset_time']
        departure_time = key_data['departure_time']
        trip_time = key_data['trip_time']
        map_url = key_data['map']
        trip_distance = key_data['trip_distance']
        return render_template('resultstemplate.html', page_title='Route Response', sunset = sunset, trip_time=trip_time, 
        location1=loc1, location2=loc2, departure_time=departure_time, map_url=map_url, trip_distance=trip_distance)
    else:
        return render_template('reqform-template.html', page_title='Route Form - error', prompt='There was an error, check your spelling and try being more specific with your location')
if __name__ == "__main__":
    app.run(host="localhost",port=8080,debug=True)