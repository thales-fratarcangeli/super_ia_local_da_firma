def parse_qs(qs: str) -> dict[str, list[str]]:
    if not qs:
        return {}
    
    # Remover o "?"
    if qs.startswith("?"):
        qs = qs[1:]
    
    params = {}
    for pair in qs.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
        else:
            key = pair
            value = ""
        
        # Decodificar %XX
        decoded_value = ""
        i = 0
        while i < len(value):
            if i + 2 < len(value) and value[i] == "%" and value[i+1].isdigit() and value[i+2].isdigit():
                hex_val = value[i+1:i+3]
                decoded_value += chr(int(hex_val, 16))
                i += 3
            elif value[i] == "+":
                decoded_value += " "
                i += 1
            else:
                decoded_value += value[i]
                i += 1
        
        if key in params:
            params[key].append(decoded_value)
        else:
            params[key] = [decoded_value]
    
    return params
