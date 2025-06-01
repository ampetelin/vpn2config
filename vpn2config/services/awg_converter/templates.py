from string import Template

AWG_TEMPLATE = Template("""[Interface]
Address = $address
DNS = $DNS
PrivateKey = $private_key
MTU = $MTU
H1 = $H1
H2 = $H2
H3 = $H3
H4 = $H4
Jc = $Jc
Jmin = $Jmin
Jmax = $Jmax
S1 = $S1
S2 = $S2

[Peer]
PublicKey = $public_key
PresharedKey = $preshared_key
AllowedIPs = $allowed_ips
Endpoint = $endpoint_address:$endpoint_port
PersistentKeepalive = $persistent_keepalive
""")