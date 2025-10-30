# app.py
"""
Advanced Unit Converter - Streamlit single-file app
Includes: Temperature, Length, Mass, Volume, Time, Speed, Area,
Energy, Power, Pressure, Density, Force, Data Storage

Features:
 - Clean UI with emojis
 - Auto-clear result when inputs change
 - Reset button
 - Copy result (clipboard) button
 - Error handling for non-numeric input
 - All logic local, no external APIs
 - Each conversion function / factor dictionary commented for clarity
"""
from typing import Dict
import streamlit as st
import html

st.set_page_config(page_title="Advanced Unit Converter", layout="centered")

# --- Session state defaults ---
if "result" not in st.session_state:
    st.session_state.result = ""
if "formula" not in st.session_state:
    st.session_state.formula = ""
if "last_input_signature" not in st.session_state:
    st.session_state.last_input_signature = None

st.title("Advanced Unit Converter")
st.caption("Local • Fast • Accurate — No API keys required")
st.markdown("---")

# --- Category map with emojis ---
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
# The pattern: factor maps unit_name -> multiplier to convert TO the category base unit.
# Most base units chosen are SI:
# - length: meter (m)
# - mass: kilogram (kg)
# - time: second (s)
# - area: square meter (m²)
# - volume: cubic meter (m³)
# - speed: meter/second (m/s)
# - energy: joule (J)
# - power: watt (W)
# - pressure: pascal (Pa)
# - density: kilogram per cubic meter (kg/m³)
# - force: newton (N)
# - data: byte (B)

# ---------- Length (base: meter) ----------
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

# ---------- Mass (base: kilogram) ----------
MASS_TO_KG = {
    "Kilogram (kg)": 1.0,
    "Gram (g)": 0.001,
    "Milligram (mg)": 1e-6,
    "Pound (lb)": 0.45359237,
    "Ounce (oz)": 0.028349523125,
    "Tonne (t)": 1000.0,  # metric tonne (a.k.a. megagram)
}

# ---------- Time (base: second) ----------
TIME_TO_S = {
    "Second (s)": 1.0,
    "Millisecond (ms)": 1e-3,
    "Minute (min)": 60.0,
    "Hour (h)": 3600.0,
    "Day (d)": 86400.0,
    "Week (wk)": 604800.0,
}

# ---------- Area (base: square meter) ----------
AREA_TO_M2 = {
    "Square meter (m²)": 1.0,
    "Square kilometer (km²)": 1e6,
    "Square mile (mi²)": 2.589988110336e6,
    "Acre": 4046.8564224,
    "Hectare (ha)": 10000.0,
    "Square foot (ft²)": 0.09290304,
}

# ---------- Volume (base: cubic meter) ----------
VOLUME_TO_M3 = {
    "Cubic meter (m³)": 1.0,
    "Litre (L)": 0.001,               # 1 L = 0.001 m³
    "Millilitre (mL)": 1e-6,
    "Gallon (gal, US)": 0.003785411784,
    "Pint (pt, US)": 0.000473176473,
}

# ---------- Speed (base: meter/second) ----------
SPEED_TO_MS = {
    "Meter/second (m/s)": 1.0,
    "Kilometer/hour (km/h)": 1000.0 / 3600.0,  # = 0.277777...
    "Mile/hour (mph)": 1609.344 / 3600.0,
    "Knot (kt)": 0.514444444,  # nautical mile per hour -> m/s
}

# ---------- Energy (base: joule) ----------
ENERGY_TO_J = {
    "Joule (J)": 1.0,
    "Kilojoule (kJ)": 1000.0,
    "Calorie (cal)": 4.184,             # small calorie
    "Kilocalorie (kcal)": 4184.0,       # food Calorie
    "Watt-hour (Wh)": 3600.0,
    "Kilowatt-hour (kWh)": 3.6e6,
}

# ---------- Power (base: watt) ----------
POWER_TO_W = {
    "Watt (W)": 1.0,
    "Kilowatt (kW)": 1000.0,
    "Megawatt (MW)": 1e6,
    "Horsepower (hp)": 745.699872,  # mechanical horsepower
}

# ---------- Pressure (base: pascal) ----------
PRESSURE_TO_PA = {
    "Pascal (Pa)": 1.0,
    "Bar": 1e5,
    "Atmosphere (atm)": 101325.0,
    "PSI (psi)": 6894.757293168,
    "Torr (Torr)": 133.3223684211,
}

# ---------- Density (base: kilogram per cubic meter) ----------
# Many density units are compound; we provide direct multipliers to kg/m³
DENSITY_TO_KGM3 = {
    "Kilogram/m³ (kg/m³)": 1.0,
    "Gram/cm³ (g/cm³)": 1000.0,    # 1 g/cm³ = 1000 kg/m³
    "Pound/ft³ (lb/ft³)": 16.018463373961,  # 1 lb/ft³ = 16.018463373961 kg/m³
}

# ---------- Force (base: newton) ----------
FORCE_TO_N = {
    "Newton (N)": 1.0,
    "Kilonewton (kN)": 1000.0,
    "Dyne (dyn)": 1e-5,
    "Pound-force (lbf)": 4.4482216152605,
}

# ---------- Data Storage (base: byte) ----------
# We use binary multiples (1 KB = 1024 B)
DATA_TO_B = {
    "Bit (b)": 1.0 / 8.0,
    "Byte (B)": 1.0,
    "Kilobyte (KB)": 1024.0,
    "Megabyte (MB)": 1024.0**2,
    "Gigabyte (GB)": 1024.0**3,
    "Terabyte (TB)": 1024.0**4,
}

# ---------- Temperature handled separately ----------
# Temperature conversions are not linear factor multipliers in the same way;
# they require formulaic transforms (additive offsets + scaling).
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

# ---------- Generic converter helper ----------
def convert_via_factors(value: float, from_unit: str, to_unit: str, factor_map: Dict[str, float]) -> float:
    """
    Generic conversion:
    - Normalize to base unit: base_value = value * factor_map[from_unit]
    - Convert to target: result = base_value / factor_map[to_unit]
    factor_map maps unit -> multiplier to convert unit TO base unit.
    """
    base_value = value * factor_map[from_unit]
    return base_value / factor_map[to_unit]

# ---------- Formatting helpers ----------
def format_number(x: float, precision: int = 8) -> str:
    """Round and trim trailing zeros for readability."""
    fmt = f"{{:.{precision}f}}".format(round(x, precision))
    if "." in fmt:
        fmt = fmt.rstrip("0").rstrip(".")
    return fmt

def clear_result_on_input_change(signature: str):
    """If any input changes, clear stored result/formula."""
    if st.session_state.last_input_signature != signature:
        st.session_state.result = ""
        st.session_state.formula = ""
        st.session_state.last_input_signature = signature

# ---------- UI layout ----------
col1, col2 = st.columns([3,1])
with col1:
    category_label = st.selectbox("Select category", list(CATEGORIES.keys()))
with col2:
    if st.button("Reset"):
        st.session_state.result = ""
        st.session_state.formula = ""
        st.session_state.last_input_signature = None
        st.experimental_rerun()

category = CATEGORIES[category_label]

# Build units list per category
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

from_unit = st.selectbox("From Unit", units)
to_unit = st.selectbox("To Unit", units, index=1 if len(units) > 1 else 0)
raw_value = st.text_input("Value to convert", key="value_input", placeholder="Enter a number (e.g., 12.5 or 1.2e3)")

# build signature and auto-clear
input_signature = f"{category}|{from_unit}|{to_unit}|{raw_value}"
clear_result_on_input_change(input_signature)

convert_clicked = st.button("Convert")

# ---------- Conversion logic on click ----------
if convert_clicked:
    # Validate / parse numeric input
    try:
        val_str = raw_value.strip().replace(",", "")
        value = float(val_str)
    except Exception:
        st.error("Please enter a valid number (for example: 12.5 or 1.2e3).")
        st.session_state.result = ""
        st.session_state.formula = ""
    else:
        formula_text = ""
        result_value = None

        # Temperature (special handling)
        if category == "temperature":
            # map short names by checking keywords
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

        # All other categories (use generic converters)
        elif category == "length":
            result_value = convert_via_factors(value, from_unit, to_unit, LENGTH_TO_M)
            formula_text = "Formula: normalize to meters (m), then convert. (value × factor_from) ÷ factor_to"

        elif category == "mass":
            result_value = convert_via_factors(value, from_unit, to_unit, MASS_TO_KG)
            formula_text = "Formula: normalize to kilograms (kg), then convert. (value × factor_from) ÷ factor_to"

        elif category == "time":
            result_value = convert_via_factors(value, from_unit, to_unit, TIME_TO_S)
            formula_text = "Formula: normalize to seconds (s), then convert. (value × factor_from) ÷ factor_to"

        elif category == "area":
            result_value = convert_via_factors(value, from_unit, to_unit, AREA_TO_M2)
            formula_text = "Formula: normalize to square meters (m²), then convert."

        elif category == "volume":
            result_value = convert_via_factors(value, from_unit, to_unit, VOLUME_TO_M3)
            formula_text = "Formula: normalize to cubic meters (m³), then convert. Note: 1 L = 0.001 m³."

        elif category == "speed":
            result_value = convert_via_factors(value, from_unit, to_unit, SPEED_TO_MS)
            formula_text = "Formula: normalize to m/s, then convert. (use length/time ratios)"

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
            # density units already map directly to kg/m^3
            result_value = convert_via_factors(value, from_unit, to_unit, DENSITY_TO_KGM3)
            formula_text = "Formula: multiply by factor to get kg/m³ then convert."

        elif category == "force":
            result_value = convert_via_factors(value, from_unit, to_unit, FORCE_TO_N)
            formula_text = "Formula: normalize to newtons (N), then convert."

        elif category == "data":
            result_value = convert_via_factors(value, from_unit, to_unit, DATA_TO_B)
            formula_text = "Formula: normalize to bytes (B), then convert. (We use 1 KB = 1024 B)"

        else:
            st.error("Unknown category selected.")
            st.session_state.result = ""
            st.session_state.formula = ""
            result_value = None

        # Display result if available
        if result_value is not None:
            st.session_state.result = f"{format_number(value)} {from_unit} = {format_number(result_value)} {to_unit}"
            st.session_state.formula = formula_text

# ---------- Output area ----------
st.markdown("### Result")
if st.session_state.result:
    st.code(st.session_state.result)
    if st.session_state.formula:
        st.caption(st.session_state.formula)

    # Copy-to-clipboard HTML + JS
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
st.markdown("**Notes & assumptions:**")
st.markdown("- SI / standard factors are used for conversions. Volume uses US gallon/pint units (if you want Imperial variants, say so).")
st.markdown("- Data storage uses binary multiples (1 KB = 1024 B).")
st.markdown("- Energy: 'Calorie' is the small calorie (4.184 J); 'Kilocalorie' (kcal) = food Calorie.")
st.markdown("- Temperature conversions use standard formulae (offset + scale).")
st.markdown("- App runs fully locally and is lightweight.")
