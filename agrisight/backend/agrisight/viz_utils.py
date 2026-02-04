import datetime

def format_area(area_km2):
    """
    Formats area in km2. If less than 1 km2, converts to hectares.
    """
    try:
        if area_km2 is None:
            return "—"
        value = float(area_km2)
        if hasattr(value, 'is_nan') and value.is_nan(): # Handle pandas/numpy NaN if passed, though float conversion usually handles it or raises
             return "—"
        if value != value: # float('nan') check
            return "—"
            
        if value < 1:
            return f"{value * 100:.1f} ha"
        return f"{value:.1f} km²"
    except (ValueError, TypeError):
        return "—"

def format_number(value):
    """
    Formats number with comma separation.
    """
    try:
        if value is None:
            return "—"
        val_float = float(value)
        if val_float != val_float: # NaN check
             return "—"
        
        # Check if it was essentially an integer to format nicely (optional, but JS Intl usually handles ints nicely)
        # JS Intl.NumberFormat().format(1200) -> "1,200"
        # JS Intl.NumberFormat().format(1200.5) -> "1,200.5"
        
        # Using {:,.2f} might force decimals where not needed.
        # Let's try to match basic behavior:
        if val_float.is_integer():
            return f"{int(val_float):,}"
        return f"{val_float:,}" 
    except (ValueError, TypeError):
        return "—"

def format_date(iso_str, fmt=None):
    """
    Formats ISO date string.
    fmt='MMM dd' -> "Jan 01"
    """
    try:
        if not iso_str:
            return "—"
        
        # Handle string input
        if isinstance(iso_str, str):
            # rudimentary ISO parsing. for full robustness dateutil is better but let's try standard
            dt = datetime.datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        elif isinstance(iso_str, (datetime.date, datetime.datetime)):
            dt = iso_str
        else:
            return "—"

        if fmt == "MMM dd":
            return dt.strftime("%b %d")
        
        # Default roughly matches JS toLocaleString(), which is locale dependent.
        # We'll use a standard readable format: YYYY-MM-DD HH:MM:SS or similar
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "—"

def format_relative_time(iso_input):
    """
    Returns 'X m ago', 'X h ago', etc.
    """
    try:
        if not iso_input:
            return "—"

        now = datetime.datetime.now(datetime.timezone.utc)
        
        if isinstance(iso_input, str):
            dt = datetime.datetime.fromisoformat(iso_input.replace('Z', '+00:00'))
        elif isinstance(iso_input, (datetime.datetime)):
            dt = iso_input
            if dt.tzinfo is None:
                # assume utc if naive, or local? context implies ISO strings usually originate from API/DB in UTC
                dt = dt.replace(tzinfo=datetime.timezone.utc)
        else:
             return "—"
        
        # If input was naive string parsed, check if it has timezone
        if dt.tzinfo is None:
             dt = dt.replace(tzinfo=datetime.timezone.utc)

        diff = now - dt
        minutes = int(diff.total_seconds() / 60)

        if minutes < 1:
            return "just now"
        if minutes < 60:
            return f"{minutes}m ago"
        
        hours = int(minutes / 60)
        if hours < 24:
            return f"{hours}h ago"
        
        days = int(hours / 24)
        return f"{days}d ago"
    except Exception:
        return "—"

def format_vegetation_index(value):
    try:
        if value is None:
            return "—"
        v = float(value)
        if v != v: return "—"
        return f"{v:.2f}"
    except (ValueError, TypeError):
        return "—"

def get_vegetation_index_label(value, type_str="NDVI"):
    try:
        v = float(value)
        if v != v: return f"{type_str}: —"
        
        label = "Moderate"
        if v >= 0.6:
            label = "Healthy"
        elif v <= 0.3:
            label = "Stressed"
        return label
    except (ValueError, TypeError):
         return f"{type_str}: —"

def get_vegetation_index_color(value, type_str="NDVI"):
    try:
        v = float(value)
        if v != v: return ""
        
        if v >= 0.6:
            return "text-green-600 dark:text-green-400"
        if v <= 0.3:
            return "text-red-600 dark:text-red-400"
        return "text-yellow-600 dark:text-yellow-400"
    except (ValueError, TypeError):
        return ""

def get_risk_level_color(risk_level):
    if not risk_level:
        return "text-gray-600 dark:text-gray-400"
    
    rl = str(risk_level).lower()
    
    if rl in ["low", "healthy"]:
        return "text-green-600 dark:text-green-400"
    elif rl in ["medium", "moderate"]:
        return "text-yellow-600 dark:text-yellow-400"
    elif rl in ["high", "critical", "stressed"]:
        return "text-red-600 dark:text-red-400"
    else:
        return "text-gray-600 dark:text-gray-400"
