# app.py
"""
Advanced Unit Converter - Streamlit single-file app
Includes 13 categories:
Temperature, Length, Mass, Volume, Time, Speed, Area,
Energy, Power, Pressure, Density, Force, Data Storage

Features:
 - Clean UI with emojis
 - Auto-clear result when inputs change
 - Reset button (clears session state and reruns)
 - Copy result to clipboard (small HTML/JS)
 - Error handling for non-numeric input
 - All logic local, no external APIs
 - Each conversion factor/function commented for clarity
"""

from typing import Dict
import streamlit as st
import html

# Page config
st.set_page_config(page_title="Advanced Unit Converter", layout="centered")

# --- Session state defaults ---
if "result" not in st.session_state:
    st.session_state.result = ""
if "formula" not in st.session_state:
    st.session_state.formula = ""
if "last_input_signature" not in st.session_state:
    st.session_state.last_input_signature = None

# App header
st.title("Advanced Unit Converter")
st.caption("Local • Fast • Accurate — No API keys required")
st.markdown("---")

# --- Categories map ---
CATEGORIES = {
    "Temperature 🌡️": "temperature",
    "Length / Distance 📏": "length",
    "Mass ⚖️": "mass",
    "Volume 💧": "volume",
    "Time ⏱️": "time",
    "Speed 🏎️": "speed",
    "Area 🌈": "area",
    "Energy 🔋": "energy",
    "Power 🧠": "power",
    "Pressure 🧮": "pressure",
    "Density 🌊": "density",
    "Force ⚙️": "force",
    "Data Storage ⚛️": "data",
}

# ---------- Conversion factor dictionaries ----------
# factor_map: unit -> multiplier to convert unit TO the chosen base unit.

# LENGTH: base unit = meter (m)
LENGTH_TO_M = {
    "Meter (m)": 1.0,
    "Kilometer (km)": 1000.0,
    "Centimeter (cm)": 0.01,
    "Millimeter (mm)": 0.001,
    "Inch (in)": 0.0254,
    "Foot (ft)": 0.3048,
    "Yard (yd)": 0.9144,
    "Mile (mi)": 1609.344,
}

# MASS: base unit = kilogram (kg)
MASS_TO_KG = {
    "Kilogram (kg)": 1.0,
    "Gram (g)": 0.001,
    "Milligram (mg)": 1e-6,
    "Pound (lb)": 0.45359237,
    "Ounce (oz)": 0.028349523125,
    "Tonne (t)": 1000.0,
}

# TIME: base unit = second (s)
TIME_TO_S = {
    "Second (s)": 1.0,
    "Millisecond (ms)": 1e-3,
    "Minute (min)": 60.0,
    "Hour (h)": 3600.0,
    "Day (d)": 86400.0,
    "Week (wk)": 604800.0,
}

# AREA: base unit = square meter (m²)
AREA_TO_M2 = {
    "Square meter (m²)": 1.0,
    "Square kilometer (km²)": 1e6,
    "Square mile (mi²)": 2.589988110336e6,
    "Acre": 4046.8564224,
    "Hectare (ha)": 10000.0,
    "Square foot (ft²)": 0.09290304,
}

# VOLUME: base unit = cubic meter (m³)
VOLUME_TO_M3 = {
    "Cubic meter (m³)": 1.0,
    "Litre (L)": 0.001,               # 1 L = 0.001 m³
    "Millilitre (mL)": 1e-6,
    "Gallon (gal, US)": 0.003785411784,
    "Pint (pt, US)": 0.000473176473,
}

# SPEED: base unit = meter/second (m/s)
SPEED_TO_MS = {
    "Meter/second (m/s)": 1.0,
    "Kilometer/hour (km/h)": 1000.0 / 3600.0,
    "Mile/hour (mph)": 1609.344 / 3600.0,
    "Knot (kt)": 0.514444444,
}

# ENERGY: base unit = joule (J)
ENERGY_TO_J = {
    "Joule (J)": 1.0,
    "Kilojoule (kJ)": 1000.0,
    "Calorie (cal)": 4.184,
    "Kilocalorie (kcal)": 4184.0,
    "Watt-hour (Wh)": 3600.0,
    "Kilowatt-hour (kWh)": 3.6e6,
}

# POWER: base unit = watt (W)
POWER_TO_W = {
    "Watt (W)": 1.0,
    "Kilowatt (kW)": 1000.0,
    "Megawatt (MW)": 1e6,
    "Horsepower (hp)": 745.699872,
}

# PRESSURE: base unit = pascal (Pa)
PRESSURE_TO_PA = {
    "Pascal (Pa)": 1.0,
    "Bar": 1e5,
    "Atmosphere (atm)": 101325.0,
    "PSI (psi)": 6894.757293168,
    "Torr (Torr)": 133.3223684211,
}

# DENSITY: base = kilogram per cubic meter (kg/m³)
DENSITY_TO_KGM3 = {
    "Kilogram/m³ (kg/m³)": 1.0,
    "Gram/cm³ (g/cm³)": 1000.0,
    "Pound/ft³ (lb/ft³)": 16.018463373961,
}

# FORCE: base = newton (N)
FORCE_TO_N = {
    "Newton (N)": 1.0,
    "Kilonewton (kN)": 1000.0,
    "Dyne (dyn)": 1e-5,
    "Pound-force (lbf)": 4.4482216152605,
}

# DATA STORAGE: base = byte (B), binary multiples (1 KB = 1024 B)
DATA_TO_B = {
    "Bit (b)": 1.0 / 8.0,
    "Byte (B)": 1.0,
    "Kilobyte (KB)": 1024.0,
    "Megabyte (MB)": 1024.0**2,
    "Gigabyte (GB)": 1024.0**3,
    "Terabyte (TB)": 1024.0**4,
}

# TEMPERATURE: special (requires formulas; not simple multiplicative factors)
def celsius_to_fahrenheit(c: float) -> float:
    """(°C × 9/5) + 32"""
    return (c * 9.0 / 5.0) + 32.0

def fahrenheit_to_celsius(f: float) -> float:
    """(°F − 32) × 5/9"""
    return (f - 32.0) * 5.0 / 9.0

def celsius_to_kelvin(c: float) -> float:
    """°C + 273.15"""
    return c + 273.15

def kelvin_to_celsius(k: float) -> float:
    """K − 273.15"""
    return k - 273.15

def fahrenheit_to_kelvin(f: float) -> float:
    """(°F − 32) × 5/9 + 273.15"""
    return (f - 32.0) * 5.0 / 9.0 + 273.15

def kelvin_to_fahrenheit(k: float) -> float:
    """(K − 273.15) × 9/5 + 32"""
    return (k - 273.15) * 9.0 / 5.0 + 32.0

# ---------- Generic conversion helper ----------
def convert_via_factors(value: float, from_unit: str, to_unit: str, factor_map: Dict[str, float]) -> float:
    """
    Generic conversion:
      base_value = value * factor_map[from_unit]
      result = base_value / factor_map[to_unit]
    factor_map maps unit -> multiplier to convert unit TO the base unit.
    """
    base_value = value * factor_map[from_unit]
    return base_value / factor_map[to_unit]

# ---------- Formatting helpers ----------
def format_number(x: float, precision: int = 8) -> str:
    """Round and pretty trim trailing zeros."""
    fmt = f"{{:.{precision}f}}".format(round(x, precision))
    if "." in fmt:
        fmt = fmt.rstrip("0").rstrip(".")
    return fmt

def clear_result_on_input_change(signature: str):
    """Clear result/formula if signature changed (auto-clear behavior)."""
    if st.session_state.last_input_signature != signature:
        st.session_state.result = ""
        st.session_state.formula = ""
        st.session_state.last_input_signature = signature

# ---------- UI layout ----------
col1, col2 = st.columns([3, 1])
with col1:
    category_label = st.selectbox("Select category", list(CATEGORIES.keys()))
with col2:
    # Reset clears all session state and reruns the app
    if st.button("Reset"):
        # Clear only our known keys to avoid surprising behaviour for other Streamlit components
        keys_to_clear = ["result", "formula", "last_input_signature", "value_input"]
        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
        # rerun using new stable API
        st.rerun()

category = CATEGORIES[category_label]

# Build units list based on selected category
if category == "temperature":
    units = ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"]
elif category == "length":
    units = list(LENGTH_TO_M.keys())
elif category == "mass":
    units = list(MASS_TO_KG.keys())
elif category == "volume":
    units = list(VOLUME_TO_M3.keys())
elif category == "time":
    units = list(TIME_TO_S.keys())
elif category == "speed":
    units = list(SPEED_TO_MS.keys())
elif category == "area":
    units = list(AREA_TO_M2.keys())
elif category == "energy":
    units = list(ENERGY_TO_J.keys())
elif category == "power":
    units = list(POWER_TO_W.keys())
elif category == "pressure":
    units = list(PRESSURE_TO_PA.keys())
elif category == "density":
    units = list(DENSITY_TO_KGM3.keys())
elif category == "force":
    units = list(FORCE_TO_N.keys())
elif category == "data":
    units = list(DATA_TO_B.keys())
else:
    units = []

# Unit selection widgets
from_unit = st.selectbox("From Unit", units)
to_unit = st.selectbox("To Unit", units, index=1 if len(units) > 1 else 0)

# Value input: use text input to allow scientific notation; parse later with float()
raw_value = st.text_input("Value to convert", key="value_input", placeholder="Enter a number (e.g., 12.5 or 1.2e3)")

# Build input signature and clear result when any input changes
input_signature = f"{category}|{from_unit}|{to_unit}|{raw_value}"
clear_result_on_input_change(input_signature)

# Convert button
convert_clicked = st.button("Convert")

# ---------- Conversion logic ----------
if convert_clicked:
    # Parse number robustly (allow commas and scientific notation)
    try:
        val_str = raw_value.strip().replace(",", "")
        value = float(val_str)
    except Exception:
        st.error("Please enter a valid number (e.g., 12.5 or 1.2e3).")
        st.session_state.result = ""
        st.session_state.formula = ""
    else:
        formula_text = ""
        result_value = None

        # Temperature: handled by formula functions
        if category == "temperature":
            f_low = from_unit.lower()
            t_low = to_unit.lower()

            if "celsius" in f_low and "fahrenheit" in t_low:
                result_value = celsius_to_fahrenheit(value)
                formula_text = "Formula: (°C × 9/5) + 32"
            elif "fahrenheit" in f_low and "celsius" in t_low:
                result_value = fahrenheit_to_celsius(value)
                formula_text = "Formula: (°F − 32) × 5/9"
            elif "celsius" in f_low and "kelvin" in t_low:
                result_value = celsius_to_kelvin(value)
                formula_text = "Formula: °C + 273.15"
            elif "kelvin" in f_low and "celsius" in t_low:
                result_value = kelvin_to_celsius(value)
                formula_text = "Formula: K − 273.15"
            elif "fahrenheit" in f_low and "kelvin" in t_low:
                result_value = fahrenheit_to_kelvin(value)
                formula_text = "Formula: (°F − 32) × 5/9 + 273.15"
            elif "kelvin" in f_low and "fahrenheit" in t_low:
                result_value = kelvin_to_fahrenheit(value)
                formula_text = "Formula: (K − 273.15) × 9/5 + 32"
            else:
                # same unit or fallback
                result_value = value
                formula_text = "Formula: identity (same unit)"

        # Generic conversions via factor maps
        elif category == "length":
            result_value = convert_via_factors(value, from_unit, to_unit, LENGTH_TO_M)
            formula_text = "Formula: normalize to meters (m), then convert: (value × factor_from) ÷ factor_to"

        elif category == "mass":
            result_value = convert_via_factors(value, from_unit, to_unit, MASS_TO_KG)
            formula_text = "Formula: normalize to kilograms (kg), then convert."

        elif category == "time":
            result_value = convert_via_factors(value, from_unit, to_unit, TIME_TO_S)
            formula_text = "Formula: normalize to seconds (s), then convert."

        elif category == "area":
            result_value = convert_via_factors(value, from_unit, to_unit, AREA_TO_M2)
            formula_text = "Formula: normalize to square meters (m²), then convert."

        elif category == "volume":
            result_value = convert_via_factors(value, from_unit, to_unit, VOLUME_TO_M3)
            formula_text = "Formula: normalize to cubic meters (m³), then convert. (1 L = 0.001 m³)"

        elif category == "speed":
            result_value = convert_via_factors(value, from_unit, to_unit, SPEED_TO_MS)
            formula_text = "Formula: normalize to m/s (distance/time), then convert."

        elif category == "energy":
            result_value = convert_via_factors(value, from_unit, to_unit, ENERGY_TO_J)
            formula_text = "Formula: normalize to joules (J), then convert."

        elif category == "power":
            result_value = convert_via_factors(value, from_unit, to_unit, POWER_TO_W)
            formula_text = "Formula: normalize to watts (W), then convert."

        elif category == "pressure":
            result_value = convert_via_factors(value, from_unit, to_unit, PRESSURE_TO_PA)
            formula_text = "Formula: normalize to pascals (Pa), then convert."

        elif category == "density":
            result_value = convert_via_factors(value, from_unit, to_unit, DENSITY_TO_KGM3)
            formula_text = "Formula: units map directly to kg/m³; convert via factors."

        elif category == "force":
            result_value = convert_via_factors(value, from_unit, to_unit, FORCE_TO_N)
            formula_text = "Formula: normalize to newtons (N), then convert."

        elif category == "data":
            result_value = convert_via_factors(value, from_unit, to_unit, DATA_TO_B)
            formula_text = "Formula: normalize to bytes (B), then convert (1 KB = 1024 B)."

        else:
            st.error("Unknown category selected.")
            st.session_state.result = ""
            st.session_state.formula = ""

        # Set session state result and formula for display
        if result_value is not None:
            st.session_state.result = f"{format_number(value)} {from_unit} = {format_number(result_value)} {to_unit}"
            st.session_state.formula = formula_text

# ---------- Output area ----------
st.markdown("### Result")
if st.session_state.result:
    st.code(st.session_state.result)
    if st.session_state.formula:
        st.caption(st.session_state.formula)

    # Copy-to-clipboard small HTML/JS
    copy_button_html = f"""
    <div>
      <input type="text" value="{html.escape(st.session_state.result)}" id="result_text" style="width:0;height:0;border:0;opacity:0;position:absolute;left:-9999px;">
      <button onclick="navigator.clipboard.writeText(document.getElementById('result_text').value).then(()=>{{document.getElementById('copy_msg').innerText='Copied!'}}).catch(()=>{{document.getElementById('copy_msg').innerText='Copy failed'}})">
        Copy Result
      </button>
      <span id="copy_msg" style="margin-left:8px;color:green;"></span>
    </div>
    """
    st.components.v1.html(copy_button_html, height=60)
else:
    st.info("No result yet — enter a value and click Convert.")

st.markdown("---")
st.caption("Alizay Ahmed")

