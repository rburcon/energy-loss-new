import streamlit as st
import pandas as pd
import numpy as np
import pvlib
from datetime import datetime

st.set_page_config(page_title="Energy loss - clean sky model", layout="wide")

# Sidebar for inputs
with st.sidebar:
    st.title("Input Parameters")
    
    latitude = st.number_input("Latitude", value=-23.54, format="%.2f")
    longitude = st.number_input("Longitude", value=-51.68, format="%.2f")
    panel_tilt = st.number_input("Panel tilt", value=23.54, format="%.2f")
    azimuth = st.number_input("Azimuth", value=0.0, format="%.2f")
    timezone = st.selectbox("Timezone", 
                          options=['America/Noronha', 'America/Bahia', 
                                  'America/Manaus', 'America/Rio_Branco'],
                          index=1)

# Main content
st.title("☀️ Solar Energy Loss Calculator")
st.markdown("### Clean Sky Model Analysis")

if st.button("Calculate Energy Loss"):
    with st.spinner("Calculating..."):
        try:
            # Create location object
            tus = pvlib.location.Location(latitude, longitude, timezone, 600, 'Maringá')
            
            # Get solar data
            times = pd.date_range(start='2017-01-01', end='2018-01-01', freq='60min', tz=tus.tz)
            ephem_data = tus.get_solarposition(times)
            irrad_data = tus.get_clearsky(times)
            dni_et = pvlib.irradiance.get_extra_radiation(times.dayofyear)
            sun_zen = ephem_data['apparent_zenith']
            AM = pvlib.atmosphere.get_relative_airmass(sun_zen)

            # Calculate irradiance
            model = 'isotropic'
            
            # Horizontal surface
            total = pvlib.irradiance.get_total_irradiance(
                abs(latitude), 0, 
                ephem_data['apparent_zenith'], ephem_data['azimuth'],
                dni=irrad_data['dni'], ghi=irrad_data['ghi'], dhi=irrad_data['dhi'],
                dni_extra=dni_et, airmass=AM,
                model=model,
                surface_type='urban'
            )
            
            # Tilted surface
            total_cor = pvlib.irradiance.get_total_irradiance(
                panel_tilt, azimuth, 
                ephem_data['apparent_zenith'], ephem_data['azimuth'],
                dni=irrad_data['dni'], ghi=irrad_data['ghi'], dhi=irrad_data['dhi'],
                dni_extra=dni_et, airmass=AM,
                model=model,
                surface_type='urban'
            )
            
            # Calculate loss percentage
            loss_percentage = (1 - ((total_cor.poa_global.sum()/365) / (total.poa_global.sum()/365))) * 100
            
            # Display results
            st.success(f"For the panel angle of {panel_tilt:.2f}° and azimuth of {azimuth:.2f}°, "
                      f"we have a loss of {loss_percentage:.2f}%")
            
            # Optional: Show dataframes
            with st.expander("Show Raw Data"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Horizontal Surface Irradiance")
                    st.dataframe(total.head())
                with col2:
                    st.write("Tilted Surface Irradiance")
                    st.dataframe(total_cor.head())
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# About section
with st.expander("About this app"):
    st.markdown("""
    **Solar radiation clear sky model**  
    Developed by Reinaldo Burcon Junior  
    
    This app calculates energy loss based on panel orientation using PVLib's clean sky model.
    """)
    
    st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
