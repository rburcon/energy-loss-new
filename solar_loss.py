# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

try:
    import seaborn as sns
    sns.set(rc={'figure.figsize': (12, 6)})
except ImportError:
    pass

import pvlib

st.set_page_config(page_title="Energy Loss - Clear Sky Model", layout="wide")
st.title("Energy Loss - Clear Sky Model")
st.markdown("Solar radiation clear sky model - Reinaldo Burcon Junior")

# Entrada de dados
col1, col2 = st.columns(2)
with col1:
    latitude = st.number_input("Latitude", value=-23.54, format="%.5f")
    longitude = st.number_input("Longitude", value=-51.68, format="%.5f")
    ang_painel = st.number_input("Panel tilt (°)", value=23.54, format="%.2f")
    azimute = st.number_input("Azimuth (°)", value=0.0, format="%.2f")

with col2:
    fuso = st.selectbox(
        "Timezone",
        ('America/Noronha', 'America/Bahia', 'America/Manaus', 'America/Rio_Branco'),
        index=1
    )

if st.button("Calculate"):
    tus = pvlib.location.Location(latitude, longitude, fuso, 600, 'Maringá')
    times = pd.date_range(start='2017-01-01', end='2018-01-01', freq='60min', tz=tus.tz)
    ephem_data = tus.get_solarposition(times)
    irrad_data = tus.get_clearsky(times)

    surf_tilt = ang_painel
    surf_az = azimute

    dni_et = pvlib.irradiance.get_extra_radiation(times.dayofyear)
    sun_zen = ephem_data['apparent_zenith']
    AM = pvlib.atmosphere.get_relative_airmass(sun_zen)

    totals = {}
    model = 'isotropic'

    total = pvlib.irradiance.get_total_irradiance(
        abs(latitude), 0,
        ephem_data['apparent_zenith'], ephem_data['azimuth'],
        dni=irrad_data['dni'], ghi=irrad_data['ghi'], dhi=irrad_data['dhi'],
        dni_extra=dni_et, airmass=AM,
        model=model, surface_type='urban'
    )
    totals[model] = total

    totals_cor = {}
    total_cor = pvlib.irradiance.get_total_irradiance(
        surf_tilt, surf_az,
        ephem_data['apparent_zenith'], ephem_data['azimuth'],
        dni=irrad_data['dni'], ghi=irrad_data['ghi'], dhi=irrad_data['dhi'],
        dni_extra=dni_et, airmass=AM,
        model=model, surface_type='urban'
    )
    totals_cor[model] = total_cor

    perda_percentual = (1 - ((total_cor.poa_global.sum() / 365) / (total.poa_global.sum() / 365))) * 100
    st.success(f"For the panel angle equal to the latitude, we have a loss of {perda_percentual:.2f}%")

    # Plot
    fig, ax = plt.subplots()
    ax.plot(times, total['poa_global'], label='Optimal Tilt')
    ax.plot(times, total_cor['poa_global'], label='Given Tilt', alpha=0.7)
    ax.set_xlabel("Time")
    ax.set_ylabel("POA Global Irradiance (W/m²)")
    ax.legend()
    st.pyplot(fig)
