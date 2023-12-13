# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sodapy import Socrata


client = Socrata("data.winnipeg.ca", None)
df = pd.DataFrame.from_records(client.get("6x82-bz5y"))

# save fetched data to csv file
df.to_csv("data/data.csv")

# get date value from dispatch_date
df['dispatch_date'] = df['dispatch_date'].apply(lambda x: np.char.split(x, 'T')).apply(lambda x: x[0])
# change format to datetime
df['dispatch_date'] = pd.to_datetime(df['dispatch_date'])
# change format to int
df['patient_number'] = df['patient_number'].astype(int)

# fill NA
df.fillna('N.A.', inplace=True)

# get date, incident_number and patient_number into a new dataframe
p_number_df = df[['dispatch_date', 'incident_number', 'patient_number']]
# get date, incident_number and patient_number of different substance
o_number_df = p_number_df[df['substance'] == 'Opioids']
a_number_df = p_number_df[df['substance'] == 'Alcohol']
cr_number_df = p_number_df[df['substance'] == 'Crystal Meth']
m_number_df = p_number_df[df['substance'] == 'Marijuana']
co_number_df = p_number_df[df['substance'] == 'Cocaine']

# get number of patients of each day and the running total of number of patients till now
def get_running_total(df):
  # get the max number of patients for different dispatch_date and incident_number
  df = df.groupby(['dispatch_date', 'incident_number'])['patient_number'].max().reset_index()
  # get number of patients for each dispatch_date
  df = df.groupby(['dispatch_date'])['patient_number'].sum().reset_index()
  # get the running total number
  df['running_total'] = df['patient_number'].cumsum()
  return df

# get the daily patients number and running total number
sum_p_number_df = get_running_total(p_number_df)
# get daily and total number for different substance
sum_o_number_df   = get_running_total(o_number_df)
sum_a_number_df   = get_running_total(a_number_df)
sum_cr_number_df  = get_running_total(cr_number_df)
sum_m_number_df   = get_running_total(m_number_df)
sum_co_number_df  = get_running_total(co_number_df)

def plot_and_save(df, name):
  # Set up the figure and the first y-axis
  fig, ax1 = plt.subplots(figsize=(10, 6))

  # Plotting 'running_total' on the first y-axis
  ax1.plot(df['dispatch_date'], df['patient_number'], label='Daily Incidents', color='blue')

  # Adding labels for the first y-axis
  ax1.set_xlabel('Date')
  ax1.set_ylabel('Daily Incidents', color='black')
  ax1.tick_params('y', colors='black')

  # Create a secondary y-axis for 'another_column'
  ax2 = ax1.twinx()

  # Plotting 'another_column' on the second y-axis
  ax2.plot(df['dispatch_date'], df['running_total'], marker='x', label='Total', color='grey')

  # Adding labels for the second y-axis
  ax2.set_ylabel('Running Total', color='grey')
  ax2.tick_params('y', colors='grey')
  
  n = 5
  xticks_indices = range(0, len(df['dispatch_date']), len(df['dispatch_date']) // n)
  xticks_labels = df['dispatch_date'].iloc[xticks_indices].dt.date
  ax1.set_xticks(xticks_labels)
  ax1.set_xticklabels(xticks_labels, rotation=45, ha='right')

  # Adding legend
  lines, labels = ax1.get_legend_handles_labels()
  lines2, labels2 = ax2.get_legend_handles_labels()
  ax2.legend(lines + lines2, labels + labels2, loc='upper left')

  plt.title(f'{name} Incidents Over Time')
  plt.grid(True)

  # Save the plot as a file
  plt.savefig(f'data/{name.replace(" ","_")}.png', bbox_inches='tight')
  #plt.show()

plot_and_save(sum_p_number_df, "Drug and Alcohol")
plot_and_save(sum_o_number_df, "Opioids")
plot_and_save(sum_a_number_df, "Alcohol")
plot_and_save(sum_cr_number_df, "Crystal Meth")
plot_and_save(sum_m_number_df, "Marijuana")
plot_and_save(sum_co_number_df, "Cocaine")

from datetime import datetime, timedelta
import re

# update the index.html to set the updated time
def update_last_modified(html_file_path, tz_adjust = -6):
    try:
        # Read the HTML file
        with open(html_file_path, 'r') as file:
            content = file.read()

        # Use regular expression to replace content within the <span> tags with the current date
        current_date = (datetime.now() + timedelta(hours=tz_adjust)).strftime("%Y-%m-%d %H:%M:%S %p")
        pattern = r'<h2 id="updated_time">.*?</h2>'
        updated_content = re.sub(pattern, '<h2 id="updated_time">Data updated from data.winnipeg.ca at {}</h2>'.format(current_date), content, flags=re.DOTALL)

        # Write the updated content back to the file
        with open(html_file_path, 'w') as file:
            file.write(updated_content)

        print('Last modified date updated successfully.')
    except Exception as e:
        print('Error updating last modified date:', str(e))

# Specify the path to your HTML file
html_file_path = './index.html'

# Call the function to update the last modified date
update_last_modified(html_file_path)
