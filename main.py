from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager
from datetime import datetime, timedelta

GOOGLE_FLIGHT = "https://www.google.co.uk/travel/flights?hl=zh"

# define departure city and search time range
FROM_CITY = "Chengdu"
DAYS_FROM_DELTA = 1
DAYS_TO_DELTA = 30

data_manager = DataManager()
flight_search = FlightSearch()

sheet_data = data_manager.get_destination_data()

update_sheet = False
# query iata based on city in google sheet
for row in data_manager.get_destination_data():
    if row["iataCode"] == "":
        update_sheet = True
        row["iataCode"] = flight_search.query_iata(row['city'])

# update iata to google sheet
if update_sheet:
    data_manager.update_iata()


from_iata = flight_search.query_iata(FROM_CITY)
date_from = datetime.today() + timedelta(days=DAYS_FROM_DELTA)
date_to = date_from + timedelta(days=DAYS_TO_DELTA)

for destination in sheet_data:
    flight_data = flight_search.query_flight_prices(
        from_iata, destination["iataCode"], date_from, date_to)
    message = ""
    try:
        if flight_data.price < destination["lowestPrice"]:
            message = f"Low price alert! Only ￥{flight_data.price} to fly from {flight_data.from_city}-{flight_data.from_airport} to {flight_data.to_city}-{flight_data.to_airport}, from {flight_data.departure_date} to {flight_data.return_date}."
            if flight_data.stop_overs == 1:
                message += f"\nFlight has 1 stop over, via {flight_data.via_city}."
            link = f"{GOOGLE_FLIGHT}&q=Flights%20to%20{flight_data.from_airport}%20from%20{flight_data.to_airport}%20on%20{flight_data.departure_date}%20through%20{flight_data.return_date}"
            noticer = NotificationManager()
            # send message via Dingtalk
            noticer.send_sms(f"{message}\n{link}")
        else:
            message = f"No flights lower than {destination['lowestPrice']} for {flight_data.to_city}."
    except AttributeError:
        message = f"No flights found for {destination['city']}."
    finally:
        print(message)
