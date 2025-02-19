#import requirement libraries
import random
import json
import pycountry_convert as pc

#import web-based libraries
import html
import requests
import socket
import ipaddress
import ssl
import tldextract
import geoip2.database
import json
from dns import resolver, rdatatype

#import regex and encoding libraries
import re
import base64


def is_valid_base64(string_value):
    try:
        # Decode the string using base64
        byte_decoded = base64.b64decode(string_value)
        # Encode the decoded bytes back to base64 and compare to the original string
        return base64.b64encode(byte_decoded).decode("utf-8") == string_value
    except:
        # If an exception is raised during decoding, the string is not valid base64
        return False


def is_valid_domain(hostname):
    # Extract the TLD, domain, and subdomain from the hostname
    ext = tldextract.extract(hostname)
    # Check if the domain and TLD are not empty
    return ext.domain != "" and ext.suffix != ""


def is_valid_ip_address(ip):
    try:
        # Try out to return True if it's IPV4 or IPV6
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        # Else it returns False
        return False


def is_ipv6(ip):
    try:
        # Try out to return True if it's IPV6
        ipaddress.ip_address(ip)
        if ":" in ip:
            return True
        else:
            # Else it returns False
            return False
    except ValueError:
        return False


def get_ips(node):
    try:
        res = resolver.Resolver()
        res.nameservers = ["8.8.8.8"]

        # Retrieve IPV4 and IPV6
        answers_ipv4 = res.resolve(node, rdatatype.A, raise_on_no_answer=False)
        answers_ipv6 = res.resolve(node, rdatatype.AAAA, raise_on_no_answer=False)

        # Initialize set for IPV4 and IPV6
        ips = set()

        # Append IPV4 and IPV6 into set
        for rdata in answers_ipv4:
            ips.add(rdata.address)

        for rdata in answers_ipv6:
            ips.add(rdata.address)

        return ips
    except Exception:
        return None


def get_ip(node):
    try:
        # Get node and return the current hostname
        return socket.gethostbyname(node)
    except Exception:
        return None


def get_country_from_ip(ip):
    try:
        with geoip2.database.Reader("./geoip-lite/geoip-lite-country.mmdb") as reader:
            response = reader.country(ip)
            country_code = response.country.iso_code
        if not country_code is None:
            return country_code
        else:
            # If country code is NoneType, Returns 'NA'
            return "NA"
    except:
        return "NA"


def get_continent(country_code):
    continent_code = pc.country_alpha2_to_continent_code(country_code)
    if continent_code in ['NA', 'SA']:
        continent_emoji = "\U0001F30E"
    elif continent_code in ['EU', 'AF', 'AN']:
        continent_emoji = "\U0001F30D"
    elif continent_code in ['AS', 'OC']:
        continent_emoji = "\U0001F30F"
    
    return continent_emoji


def check_port(ip, port, timeout=1):
    """
    Check if a port is open on a given IP address.

    Args:
    ip (str): The IP address.
    port (int): The port number.
    timeout (int, optional): The timeout in seconds. Defaults to 5.

    Returns:
    bool: True if the port is open, False otherwise.
    """
    try:
        sock = socket.create_connection(address=(ip, port), timeout=timeout)
        sock.close()
        print("Connection Port: Open".upper())
        return True
    except:
        print("Connection Port Is Closed\n".upper())
        return False


def check_modify_config(array_configuration, protocol_type):
    # Initialize list for modified elements of configuration array
    modified_array = list()
    
    # Initialize array for security types of configuration
    tls_array = list()
    non_tls_array = list()

    # Initialize array for network types of configuration
    tcp_array = list()
    ws_array = list()
    http_array = list()
    grpc_array = list()
    
    if protocol_type == 'SHADOWSOCKS':
        for element in array_configuration:
            # Define ShadowSocks protocol type pattern
            shadowsocks_pattern = r"ss://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:-]+?)\]?:(?P<port>[0-9]+)/?#?(?P<title>(?<=#).*)?"

            # Print out original element
            print(f"ORIGINAL CONFIG: {element}")

            # Try out to match pattern and configuration
            shadowsocks_match = re.match(shadowsocks_pattern, element, flags=re.IGNORECASE)


            if shadowsocks_match is None:
                # Define ShadowSocks protocol type second pattern
                shadowsocks_pattern = r"ss://(?P<id>[^#]+)#?(?P<title>(?<=#).*)?(?P<ip>(?:))(?P<port>(?:))"

                # Try out to match second pattern and configuration
                shadowsocks_match = re.match(shadowsocks_pattern, element, flags=re.IGNORECASE)

                if shadowsocks_match is None:
                    # Append no matches ShadowSocks into unmatched file
                    with open("./splitted/no-match", "a") as no_match_file:
                        no_match_file.write(f"{element}\n")
                    print("NO MATCH\n")
                    # Continue for next element
                    continue


            # Initialize dict to separate match groups by name capturing
            config = {
                "id": shadowsocks_match.group("id"),
                "ip": shadowsocks_match.group("ip"),
                "port": shadowsocks_match.group("port"),
                "title": shadowsocks_match.group("title"),
            }

            config["id"] += "=" * ((4 - len(config["id"]) % 4) % 4)

            # Checkout config ID type
            if not is_valid_base64(config["id"]):
                # Append no matches ShadowSocks into unmatched file
                with open("./splitted/no-match", "a") as no_match_file:
                    no_match_file.write(f"{element}\n")
                print(f"INVALID ENCODED STRING: {config['id']}\n")
                # Continue for next element
                continue


            # Try out to match pattern for ShadowSocks config and extract IP and
            if config["ip"] == "":
                # Define ShadowSocks protocol type Third pattern
                shadowsocks_pattern = (r"(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:-]+?)\]?:(?P<port>[0-9]+)")

                # Try out to match pattern and configuration
                shadowsocks_match = re.match(shadowsocks_pattern, base64.b64decode(config["id"]).decode("utf-8", errors="ignore"), flags=re.IGNORECASE)

                if shadowsocks_match is None:
                    # Append no matches ShadowSocks into unmatched file
                    with open("./splitted/no-match", "a") as no_match_file:
                        no_match_file.write(f"{element}\n")
                    print("NO MATCH\n")
                    # Continue for next element
                    continue

                # Initialize dict to separate match groups by name capturing
                config = {
                    "id": base64.b64encode(shadowsocks_match.group("id").encode("utf-8")).decode("utf-8"),
                    "ip": shadowsocks_match.group("ip"),
                    "port": shadowsocks_match.group("port"),
                    "title": config["title"],
                }


            # Initialize set to append IP addresses
            ips_list = {config["ip"]}

            # Try out to retrieve config IP adresses if It's url link
            if not is_valid_ip_address(config["ip"]):
                ips_list = get_ips(config["ip"])

            # Continue for next element
            if ips_list is None:
                print("NO IP\n")
                continue


            # Iterate over IP addresses to checkout connectivity
            for ip_address in ips_list:
                # Set config dict IP address
                config["ip"] = ip_address

                # Checkout IP address and port connectivity
                if not check_port(config["ip"], int(config["port"])):
                    continue

                # Try out to retrieve country code
                country_code = get_country_from_ip(config["ip"])
                continent_emoji = get_continent(country_code)

                # Modify the IP address if it's IPV6
                if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]"

                '''
                # Continue for next IP address if exists in modified array
                if any(f"ss://{config['id']}@{config['ip']}:{config['port']}" in array_element for array_element in modified_array):
                    continue
                '''
                # Retrieve config network type and security type
                config_secrt = 'NA'
                config_type = 'TCP'

                # Modify configuration title based on server and protocol properties
                config["title"] = f"\U0001F512 SS-TCP-NA {continent_emoji} {country_code}-{config['ip']}:{config['port']}"
                
                # Print out modified configuration
                print(f"MODIFIED CONFIG: ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}\n")

                # Append modified configuration into modified array
                modified_array.append(f"ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}")

                # Append security type array
                if config_secrt == 'TLS' or config_secrt == 'REALITY':
                    tls_array.append(f"ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}")
                elif config_secrt == 'NA':
                    non_tls_array.append(f"ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}")

                # Append network type array
                if config_type == 'TCP':
                    tcp_array.append(f"ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}")
                elif config_type == 'WS':
                    ws_array.append(f"ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}")
                elif config_type == 'HTTP':
                    http_array.append(f"ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}")
                elif config_type == 'GRPC':
                    grpc_array.append(f"ss://{config['id']}@{config['ip']}:{config['port']}#{config['title']}")


    elif protocol_type == 'TROJAN':
        for element in array_configuration:
            # Define Trojan protocol type pattern
            trojan_pattern = r"trojan://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:-]+?)\]?:(?P<port>[0-9]+)/?\??(?P<params>[^#]+)?#?(?P<title>(?<=#).*)?"

            # Print out original element
            print(f"ORIGINAL CONFIG: {element}")

            # Try out to match pattern and configuration
            trojan_match = re.match(trojan_pattern, element, flags=re.IGNORECASE)

            if trojan_match is None:
                # Append no matches ShadowSocks into unmatched file
                with open("./splitted/no-match", "a") as no_match_file:
                    no_match_file.write(f"{element}\n")
                print("NO MATCH\n")
                # Continue for next element
                continue


            # Initialize dict to separate match groups by name capturing
            config = {
                "id": trojan_match.group("id"),
                "ip": trojan_match.group("ip"),
                "host": trojan_match.group("ip"),
                "port": trojan_match.group("port"),
                "params": trojan_match.group("params") or "",
                "title": trojan_match.group("title"),
            }

            # Initialize set to append IP addresses
            ips_list = {config["ip"]}

            # Try out to retrieve config IP adresses if It's url link
            if not is_valid_ip_address(config["ip"]):
                ips_list = get_ips(config["ip"])

            # Continue for next element
            if ips_list is None:
                print("NO IP\n")
                continue


            # Split configuration parameters and initialize dict for parameters
            array_params_input = config["params"].split("&")
            dict_params = {}
            
            # Iterate over parameters and split based on key value
            for pair in array_params_input:
                try:
                    key, value = pair.split("=")
                    key = re.sub(r"servicename", "serviceName", re.sub(r"headertype", "headerType", re.sub(r"allowinsecure", "allowInsecure", key.lower()),),)
                    dict_params[key] = value
                except:
                    pass

            # Set parameters for servicename and allowinsecure keys
            if (dict_params.get("security", "") in ["reality", "tls"] and dict_params.get("sni", "") == "" and is_valid_domain(config["host"])):
                dict_params["sni"] = config["host"]
                dict_params["allowInsecure"] = 1

            # Ignore the configurations with specified security and None servicename
            if (dict_params.get("security", "") in ["reality", "tls"] and dict_params.get("sni", "") == ""):
                continue


            # Iterate over IP addresses to checkout connectivity
            for ip_address in ips_list:
                # Set config dict IP address
                config["ip"] = ip_address

                # Checkout IP address and port connectivity
                if not check_port(config["ip"], int(config["port"])):
                    continue

                # Try out to retrieve country code
                country_code = get_country_from_ip(config["ip"])
                continent_emoji = get_continent(country_code)

                # Modify the IP address if it's IPV6
                if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]"

                # Define configuration parameters string value and stripped based on & character
                config["params"] = f"security={dict_params.get('security', '')}&flow={dict_params.get('flow', '')}&sni={dict_params.get('sni', '')}&encryption={dict_params.get('encryption', '')}&type={dict_params.get('type', '')}&serviceName={dict_params.get('serviceName', '')}&host={dict_params.get('host', '')}&path={dict_params.get('path', '')}&headerType={dict_params.get('headerType', '')}&fp={dict_params.get('fp', '')}&pbk={dict_params.get('pbk', '')}&sid={dict_params.get('sid', '')}&alpn={dict_params.get('alpn', '')}&allowInsecure={dict_params.get('allowInsecure', '')}&"
                config["params"] = re.sub(r"\w+=&", "", config["params"])
                config["params"] = re.sub(r"(?:encryption=none&)|(?:headerType=none&)", "", config["params"], flags=re.IGNORECASE,)
                config["params"] = config["params"].strip("&")

                '''
                # Continue for next IP address if exists in modified array
                if any(f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}" in array_element for array_element in modified_array):
                    continue
                '''
                # Retrieve config network type and security type
                config_type = dict_params.get('type', 'TCP').upper() if dict_params.get('net')!= '' else 'TCP'
                config_secrt = dict_params.get('security', 'TLS').upper() if dict_params.get('tls')!= '' else 'NA'

                # Modify configuration title based on server and protocol properties
                config["title"] = f"\U0001F512 TR-{config_type}-{config_secrt} {continent_emoji} {country_code}-{config['ip']}:{config['port']}"

                # Print out modified configuration
                print(f"MODIFIED CONFIG: trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}\n")

                # Append modified configuration into modified array
                modified_array.append(f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")

                # Append security type array
                if config_secrt == 'TLS' or config_secrt == 'REALITY':
                    tls_array.append(f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")
                elif config_secrt == 'NA':
                    non_tls_array.append(f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")

                # Append network type array
                if config_type == 'TCP':
                    tcp_array.append(f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")
                elif config_type == 'WS':
                    ws_array.append(f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")
                elif config_type == 'HTTP':
                    http_array.append(f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")
                elif config_type == 'GRPC':
                    grpc_array.append(f"trojan://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")


    
    elif protocol_type == 'VMESS':
        for element in array_configuration:
            # Define VMESS protocol type pattern
            vmess_pattern = r"vmess://(?P<json>[^#].*)"

            # Print out original element
            print(f"ORIGINAL CONFIG: {element}")

            # Try out to match pattern and configuration
            vmess_match = re.match(vmess_pattern, element, flags=re.IGNORECASE)

            if vmess_match is None:
                # Append no matches ShadowSocks into unmatched file
                with open("./splitted/no-match", "a") as no_match_file:
                    no_match_file.write(f"{element}\n")
                print("NO MATCH\n")
                # Continue for next element
                continue


            # Initialize dict to separate match groups by name capturing
            json_string = vmess_match.group("json")
            json_string += "=" * ((4 - len(json_string) % 4) % 4)
            
            # Checkout config json encoded string
            if not is_valid_base64(json_string):
                # Append invalid json encoded string config into unmatched file
                with open("./splitted/no-match", "a") as no_match_file:
                    no_match_file.write(f"{element}\n")
                print(f"INVALID ENCODED STRING: {json_string}\n")
                # Continue for next element
                continue


            # Decode json string match
            json_string = base64.b64decode(json_string).decode("utf-8", errors="ignore")

            try:
                # Convert decoded json string into dictionary
                dict_params = json.loads(json_string)
                # Modify dictionary parameters with lower keys and values
                dict_params = {k.lower(): v for k, v in dict_params.items()}
            except:
                # Append invalid json encoded string config into unmatched file
                with open("./splitted/no-match", "a") as no_match_file:
                    no_match_file.write(f"{element}\n")
                print(f"INVALID JSON STRING: {json_string}\n")
                # Continue for next element
                continue


            # Initialize dict to separate match groups by name capturing
            config = {
                "id": dict_params.get("id", ""),
                "ip": dict_params.get("add", ""),
                "host": dict_params.get("add", ""),
                "port": dict_params.get("port", ""),
                "params": "",
                "title": dict_params.get("ps", "")
            }

            # Initialize set to append IP addresses
            ips_list = {config["ip"]}

            # Try out to retrieve config IP adresses if It's url link
            if not is_valid_ip_address(config["ip"]):
                ips_list = get_ips(config["ip"])

            # Continue for next element
            if ips_list is None:
                print("NO IP\n")
                continue


            # Set parameters for servicename and allowinsecure keys
            if (dict_params.get("tls", "") in ["tls"] and dict_params.get("sni", "") == "" and is_valid_domain(config["host"])):
                dict_params["sni"] = config["host"]
                dict_params["allowInsecure"] = 1

            # Ignore the configurations with specified security and None servicename
            if (dict_params.get("tls", "") in ["tls"] and dict_params.get("sni", "") == ""):
                continue


            # Iterate over IP addresses to checkout connectivity
            for ip_address in ips_list:
                # Set config dict IP address
                config["ip"] = ip_address

                # Checkout IP address and port connectivity
                if not check_port(config["ip"], int(config["port"])):
                    continue

                # Try out to retrieve country code
                country_code = get_country_from_ip(config["ip"])
                continent_emoji = get_continent(country_code)

                # Modify the IP address if it's IPV6
                if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]"
                    
                # Define configuration parameters string value and stripped based on & character
                config["params"] = f"tls={dict_params.get('tls', '')}&sni={dict_params.get('sni', '')}&scy={dict_params.get('scy', '')}&net={dict_params.get('net', '')}&host={dict_params.get('host', '')}&path={dict_params.get('path', '')}&type={dict_params.get('type', '')}&fp={dict_params.get('fp', '')}&alpn={dict_params.get('alpn', '')}&aid={dict_params.get('aid', '')}&v={dict_params.get('v', '')}&allowInsecure={dict_params.get('allowInsecure', '')}&"
                config["params"] = re.sub(r"\w+=&", "", config["params"])
                config["params"] = re.sub(r"(?:tls=none&)|(?:type=none&)|(?:scy=none&)|(?:scy=auto&)", "", config["params"], flags=re.IGNORECASE,)
                config["params"] = config["params"].strip("&")
                
                # Retrieve config network type and security type
                config_type = dict_params.get('net', 'TCP').upper() if dict_params.get('net')!= '' else 'TCP'
                config_secrt = dict_params.get('tls','NA').upper() if dict_params.get('tls')!= '' else 'NA'

                # Modify configuration title based on server and protocol properties
                config["title"] = f"\U0001F512 VM-{config_type}-{config_secrt} {continent_emoji} {country_code}-{config['ip']}:{config['port']}"

                dict_params["add"] = config["ip"]
                dict_params["ps"] = config["title"]

                # Print out modified configuration
                print(f"MODIFIED CONFIG: vmess://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}\n")
                
                # Append modified configuration into modified array
                modified_array.append(f"vmess://{base64.b64encode(json.dumps(dict_params).encode('utf-8')).decode('utf-8')}")

                # Append security type array
                if config_secrt == 'TLS' or config_secrt == 'REALITY':
                    tls_array.append(f"vmess://{base64.b64encode(json.dumps(dict_params).encode('utf-8')).decode('utf-8')}")
                elif config_secrt == 'NA':
                    non_tls_array.append(f"vmess://{base64.b64encode(json.dumps(dict_params).encode('utf-8')).decode('utf-8')}")

                # Append network type array
                if config_type == 'TCP':
                    tcp_array.append(f"vmess://{base64.b64encode(json.dumps(dict_params).encode('utf-8')).decode('utf-8')}")
                elif config_type == 'WS':
                    ws_array.append(f"vmess://{base64.b64encode(json.dumps(dict_params).encode('utf-8')).decode('utf-8')}")
                elif config_type == 'HTTP':
                    http_array.append(f"vmess://{base64.b64encode(json.dumps(dict_params).encode('utf-8')).decode('utf-8')}")
                elif config_type == 'GRPC':
                    grpc_array.append(f"vmess://{base64.b64encode(json.dumps(dict_params).encode('utf-8')).decode('utf-8')}")

    

    elif protocol_type == 'VLESS' or protocol_type == 'REALITY':
        for element in array_configuration:
            # Define VMESS protocol type pattern
            vless_pattern = r"vless://(?P<id>[^@]+)@\[?(?P<ip>[a-zA-Z0-9\.:\-:\_]+?)\]?:(?P<port>[0-9]+)/?\?(?P<params>[^#]+)#?(?P<title>(?<=#).*)?"

            # Print out original element
            print(f"ORIGINAL CONFIG: {element}")

            # Try out to match pattern and configuration
            vless_match = re.match(vless_pattern, element, flags=re.IGNORECASE)

            if vless_match is None:
                # Append no matches ShadowSocks into unmatched file
                with open("./splitted/no-match", "a") as no_match_file:
                    no_match_file.write(f"{element}\n")
                print("NO MATCH\n")
                # Continue for next element
                continue


            # Initialize dict to separate match groups by name capturing
            config = {
                "id": vless_match.group("id"),
                "ip": vless_match.group("ip"),
                "host": vless_match.group("ip"),
                "port": vless_match.group("port"),
                "params": vless_match.group("params"),
                "title": vless_match.group("title"),
            }

            # Initialize set to append IP addresses
            ips_list = {config["ip"]}

            # Try out to retrieve config IP adresses if It's url link
            if not is_valid_ip_address(config["ip"]):
                ips_list = get_ips(config["ip"])

            # Continue for next element
            if ips_list is None:
                print("NO IP\n")
                continue


            # Split configuration parameters and initialize dict for parameters
            array_params_input = config["params"].split("&")
            dict_params = {}

            # Iterate over parameters and split based on key value
            for pair in array_params_input:
                try:
                    key, value = pair.split("=")
                    key = re.sub(r"servicename", "serviceName", re.sub(r"headertype", "headerType", re.sub(r"allowinsecure", "allowInsecure", key.lower()),),)
                    dict_params[key] = value
                except:
                    pass

            # Set parameters for servicename and allowinsecure keys
            if (dict_params.get("security", "") in ["reality", "tls"] and dict_params.get("sni", "") == "" and is_valid_domain(config["host"])):
                dict_params["sni"] = config["host"]
                dict_params["allowInsecure"] = 1

            # Ignore the configurations with specified security and None servicename
            if (dict_params.get("security", "") in ["reality", "tls"] and dict_params.get("sni", "") == ""):
                continue


            # Iterate over IP addresses to checkout connectivity
            for ip_address in ips_list:
                # Set config dict IP address
                config["ip"] = ip_address

                # Checkout IP address and port connectivity
                if not check_port(config["ip"], int(config["port"])):
                    continue

                # Try out to retrieve country code
                country_code = get_country_from_ip(config["ip"])
                continent_emoji = get_continent(country_code)

                # Modify the IP address if it's IPV6
                if is_ipv6(config["ip"]):
                    config["ip"] = f"[{config['ip']}]"

                # Define configuration parameters string value and stripped based on & character
                config["params"] = f"security={dict_params.get('security', '')}&flow={dict_params.get('flow', '')}&sni={dict_params.get('sni', '')}&encryption={dict_params.get('encryption', '')}&type={dict_params.get('type', '')}&serviceName={dict_params.get('serviceName', '')}&host={dict_params.get('host', '')}&path={dict_params.get('path', '')}&headerType={dict_params.get('headerType', '')}&fp={dict_params.get('fp', '')}&pbk={dict_params.get('pbk', '')}&sid={dict_params.get('sid', '')}&alpn={dict_params.get('alpn', '')}&allowInsecure={dict_params.get('allowInsecure', '')}&"
                config["params"] = re.sub(r"\w+=&", "", config["params"])
                config["params"] = re.sub(r"(?:encryption=none&)|(?:headerType=none&)", "", config["params"], flags=re.IGNORECASE,)
                config["params"] = config["params"].strip("&")
                
                '''
                # Continue for next IP address if exists in modified array
                if any(f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}" in array_element for array_element in modified_array):
                    continue
                '''
                # Retrieve config network type and security type
                config_type = dict_params.get('type', 'TCP').upper() if dict_params.get('net')!= '' else 'TCP'
                config_secrt = dict_params.get('security','NA').upper() if dict_params.get('tls')!= '' else 'NA'

                # Modify configuration title based on server and protocol properties
                config["title"] = f"\U0001F512 VL-{config_type}-{config_secrt} {continent_emoji} {country_code}-{config['ip']}:{config['port']}"

                # Print out modified configuration
                print(f"MODIFIED CONFIG: vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}\n")
                
                # Append modified configuration into modified array
                modified_array.append(f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")

                # Append security type array
                if config_secrt == 'TLS' or config_secrt == 'REALITY':
                    tls_array.append(f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")
                elif config_secrt == 'NA':
                    non_tls_array.append(f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")

                # Append network type array
                if config_type == 'TCP':
                    tcp_array.append(f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")
                elif config_type == 'WS':
                    ws_array.append(f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")
                elif config_type == 'HTTP':
                    http_array.append(f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")
                elif config_type == 'GRPC':
                    grpc_array.append(f"vless://{config['id']}@{config['ip']}:{config['port']}?{config['params']}#{config['title']}")
                    

    else:
        modified_array = array_configuration

    return modified_array, tls_array, non_tls_array, tcp_array, ws_array, http_array, grpc_array
