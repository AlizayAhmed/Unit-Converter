# app.py
"""
Unit Converter - Streamlit single-file app
Features:
 - Temperature, Length, Mass, Volume conversions
 - Clean UI with emojis for categories
 - Auto-clear result when input changes
 - Reset button, shows formula, copy-to-clipboard
 - All logic local (no external APIs)
"""

from typing import Tuple
import streamlit as st
import math
import html

# --- UI / Session state init ---
st.set_page_config(page_title="Unit Converter", layout="centered")
if "result" not in st.session_state:
    st.session_state.result = ""
if "formula" not in st.session_state:
    st.session_state.formula = ""
if "last_input_signature" not in st.session_state:
    st.session_state.last_input_signature = None

st.title("Unit Converter")
st.caption("Fast • Local • Clean UI — No API keys required")
st.markdown("---")

# Category options with emojis
CATEGORIES = {
    "Temperature 🌡️": "temperature",
    "Length 📏": "length",
    "Mass ⚖️": "mass",
    "Volume (Litre) 💧": "volume",
}

# --- Conversion utilities ---

# ---------- Temperature ----------
# Each function has a comment describing the formula.

def celsius_to_fahrenheit(c: float) -> float:
    """Celsius to Fahrenheit: (°C × 9/5) + 32"""
    return (c * 9.0/5.0) + 32.0

def fahrenheit_to_celsius(f: float) -> float:
    """Fahrenheit to Celsius: (°F − 32) × 5/9"""
    return (f - 32.0) * 5.0/9.0

def celsius_to_kelvin(c: float) -> float:
    """Celsius to Kelvin: °C + 273.15"""
    return c + 273.15

def kelvin_to_celsius(k: float) -> float:
    """Kelvin to Celsius: K − 273.15"""
    return k - 273.15

def fahrenheit_to_kelvin(f: float) -> float:
    """Fahrenheit to Kelvin: (°F − 32) × 5/9 + 273.15"""
    return (f - 32.0) * 5.0/9.0 + 273.15

def kelvin_to_fahrenheit(k: float) -> float:
    """Kelvin to Fahrenheit: (K − 273.15) × 9/5 + 32"""
    return (k - 273.15) * 9.0/5.0 + 32.0

# ---------- Length ----------
# Base unit: meter. Convert everything to meters first, then to target unit.

LENGTH_FACTORS_TO_METER = {
    "Meter (m)": 1.0,
    "Kilometer (km)": 1000.0,
    "Centimeter (cm)": 0.01,
    "Millimeter (mm)": 0.001,
    "Inch (in)": 0.0254,
    "Foot (ft)": 0.3048,
    "Yard (yd)": 0.9144,
    "Mile (mi)": 1609.344,
}

def length_convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert length by normalizing to meters then to target."""
    meters = value * LENGTH_FACTORS_TO_METER[from_unit]
    return meters / LENGTH_FACTORS_TO_METER[to_unit]

# ---------- Mass ----------
# Base: gram
MASS_FACTORS_TO_GRAM = {
    "Gram (g)": 1.0,
    "Kilogram (kg)": 1000.0,
    "Milligram (mg)": 0.001,
    "Pound (lb)": 453.59237,
    "Ounce (oz)": 28.349523125,
}

def mass_convert(value: float, from_unit: str, to_unit: str) -> float:
    """Normalize to grams then convert to target."""
    grams = value * MASS_FACTORS_TO_GRAM[from_unit]
    return grams / MASS_FACTORS_TO_GRAM[to_unit]

# ---------- Volume (Litre) ----------
# Base: litre
VOLUME_FACTORS_TO_LITRE = {
    "Litre (L)": 1.0,
    "Millilitre (mL)": 0.001,
    "Gallon (gal)": 3.785411784,      # US liquid gallon
    "Pint (pt)": 0.473176473,         # US liquid pint
}

def volume_convert(value: float, from_unit: str, to_unit: str) -> float:
    """Normalize to litres then convert to target."""
    litres = value * VOLUME_FACTORS_TO_LITRE[from_unit]
    return litres / VOLUME_FACTORS_TO_LITRE[to_unit]

# ---------- Helpers ----------
def format_number(x: float, precision: int = 6) -> str:
    """Format number trimming unnecessary zeros but keep reasonable precision."""
    # Use rounding and strip trailing zeros
    fmt = f"{{:.{precision}f}}".format(round(x, precision))
    # remove trailing zeros and possible trailing dot
    return fmt.rstrip('0').rstrip('.') if '.' in fmt else fmt

def clear_result_on_input_change(signature):
    """If input signature changed, clear result and formula from session state."""
    if st.session_state.last_input_signature != signature:
        st.session_state.result = ""
        st.session_state.formula = ""
        st.session_state.last_input_signature = signature

# --- UI: inputs ---
col1, col2 = st.columns([2,1])
with col1:
    category_label = st.selectbox("Select category", list(CATEGORIES.keys()))
with col2:
    # Reset button
    if st.button("Reset"):
        st.session_state.result = ""
        st.session_state.formula = ""
        st.session_state.last_input_signature = None
        # Rerun to clear UI
        st.experimental_rerun()

category = CATEGORIES[category_label]

# Build unit lists based on category
if category == "temperature":
    units = ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"]
elif category == "length":
    units = list(LENGTH_FACTORS_TO_METER.keys())
elif category == "mass":
    units = list(MASS_FACTORS_TO_GRAM.keys())
elif category == "volume":
    units = list(VOLUME_FACTORS_TO_LITRE.keys())
else:
    units = []

# Input widgets
from_unit = st.selectbox("From Unit", units)
to_unit = st.selectbox("To Unit", units, index=1 if len(units) > 1 else 0)

# using text_input to allow the user to paste text; we will parse it
raw_value = st.text_input("Value to convert", key="value_input", placeholder="Enter a number")

# build a simple signature for the inputs so changes clear results
input_signature = f"{category}|{from_unit}|{to_unit}|{raw_value}"
clear_result_on_input_change(input_signature)

# Convert button
convert_clicked = st.button("Convert")

# Auto-clear result when input changes (already handled by input signature)
# Error handling and conversion
if convert_clicked:
    # parse input
    try:
        # Accept scientific notation and commas (commas are stripped)
        val_str = raw_value.strip().replace(",", "")
        value = float(val_str)
    except Exception:
        st.error("Please enter a valid number (e.g., 12.5 or 1.2e3).")
        st.session_state.result = ""
    else:
        # do conversion based on category
        if category == "temperature":
            # map selected strings to short codes for branching
            short_from = from_unit.split()[0].lower()  # 'Celsius' -> 'celsius'
            short_to = to_unit.split()[0].lower()
            result_value = None
            formula_text = ""

            if short_from.startswith("celsius") and short_to.startswith("fahrenheit"):
                result_value = celsius_to_fahrenheit(value)
                formula_text = "Formula: (°C × 9/5) + 32"
            elif short_from.startswith("fahrenheit") and short_to.startswith("celsius"):
                result_value = fahrenheit_to_celsius(value)
                formula_text = "Formula: (°F − 32) × 5/9"
            elif short_from.startswith("celsius") and short_to.startswith("kelvin"):
                result_value = celsius_to_kelvin(value)
                formula_text = "Formula: °C + 273.15"
            elif short_from.startswith("kelvin") and short_to.startswith("celsius"):
                result_value = kelvin_to_celsius(value)
                formula_text = "Formula: K − 273.15"
            elif short_from.startswith("fahrenheit") and short_to.startswith("kelvin"):
                result_value = fahrenheit_to_kelvin(value)
                formula_text = "Formula: (°F − 32) × 5/9 + 273.15"
            elif short_from.startswith("kelvin") and short_to.startswith("fahrenheit"):
                result_value = kelvin_to_fahrenheit(value)
                formula_text = "Formula: (K − 273.15) × 9/5 + 32"
            else:
                # same unit -> identity
                result_value = value
                formula_text = "Formula: identity (same unit)"

            formatted = format_number(result_value)
            st.session_state.result = f"{format_number(value)} {from_unit} = {formatted} {to_unit}"
            st.session_state.formula = formula_text

        elif category == "length":
            result_value = length_convert(value, from_unit, to_unit)
            st.session_state.result = f"{format_number(value)} {from_unit} = {format_number(result_value)} {to_unit}"
            st.session_state.formula = f"Formula: Convert to meters using factor then to target. (meters = value × factor_from; result = meters ÷ factor_to)"

        elif category == "mass":
            result_value = mass_convert(value, from_unit, to_unit)
            st.session_state.result = f"{format_number(value)} {from_unit} = {format_number(result_value)} {to_unit}"
            st.session_state.formula = f"Formula: Convert to grams using factor then to target. (grams = value × factor_from; result = grams ÷ factor_to)"

        elif category == "volume":
            result_value = volume_convert(value, from_unit, to_unit)
            st.session_state.result = f"{format_number(value)} {from_unit} = {format_number(result_value)} {to_unit}"
            st.session_state.formula = f"Formula: Convert to litres using factor then to target. (litres = value × factor_from; result = litres ÷ factor_to)"

        else:
            st.error("Unknown category selected.")
            st.session_state.result = ""
            st.session_state.formula = ""

# --- Output area ---
st.markdown("### Result")
if st.session_state.result:
    # Show result in a code-like box for easy readability
    st.code(st.session_state.result, language=None)

    # Show formula used
    if st.session_state.formula:
        st.caption(st.session_state.formula)

    # Copy to clipboard button using a tiny JS snippet embedded
    copy_button_html = f"""
    <div>
      <input type="text" value="{html.escape(st.session_state.result)}" id="result_text" style="width:0;height:0;border:0;opacity:0;position:absolute;left:-9999px;">
      <button onclick="navigator.clipboard.writeText(document.getElementById('result_text').value).then(()=>{{document.getElementById('copy_msg').innerText='Copied!'}}).catch(()=>{{document.getElementById('copy_msg').innerText='Copy failed'}})">
        Copy Result
      </button>
      <span id="copy_msg" style="margin-left:8px;color:green;"></span>
    </div>
    """
    st.components.v1.html(copy_button_html, height=50)

else:
    st.info("No result yet — enter a value and click Convert.")

# Small footer/help
st.markdown("---")
st.markdown("**Notes:**")
st.markdown("- Temperature conversions use standard physical formulas (Celsius/Fahrenheit/Kelvin).")
st.markdown("- Length/Mass/Volume conversions use precise SI factors. Gallon/pint are US liquid units.")
st.markdown("- App works fully locally and is lightweight.")
