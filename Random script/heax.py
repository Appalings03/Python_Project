certif = "236e4fefa674f7ed163cf3ef06112457d97edb9d3543b706d0b159e967d41ec9"

# Découper la chaîne en groupes de 2 caractères (1 octet)
octets = [certif[i:i+2] for i in range(0, len(certif), 2)]

# Formater en style 0xXX, séparés par des virgules
result = ", ".join(f"0x{o}" for o in octets)

print(result)