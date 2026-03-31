from ceic_api_client.pyceic import Ceic
import pandas as pd

Ceic.set_token("96nJOPqlNPPoNrYQEQKf7Azb8meQE0TUwMn0h4HggL2tYT5JZTwL5k1YqPDca2ZJ5MyAobpQj04dHA2z4WBUMN9rTnluq6XAy5Czs5Kb75sRimch6sNXoNybcoYQr04X")

series_id = "211457102"

result = Ceic.series_data(series_id)

if hasattr(result, "data") and len(result.data) > 0:
    
    series_obj = result.data[0]  # first series
    
    time_points = series_obj.time_points
    
    rows = []
    for tp in time_points:
        rows.append({
            "date": tp.date,
            "value": tp.value
        })
    
    df = pd.DataFrame(rows)
    
    print(df.head())

else:
    print("No data returned")